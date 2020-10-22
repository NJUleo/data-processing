import json
import re
import logging
import random

import scrapy

from data_crawler.spiders.utils import remove_prefix
from data_crawler.spiders.utils import NoPrefixException
from data_crawler.spiders.utils import save_byte_file
from data_crawler.spiders.utils import save_str_file

from scrapy.utils.project import get_project_settings

from data_crawler.items import ACMPaperItem, IEEEPaperItem

class IEEESpider(scrapy.Spider):
    name = "IEEE_Conferences"
    allowed_domains = ["ieeexplore.ieee.org"]
    ieee_urls = get_project_settings().get('IEEE_CONF_URLS')
    ieee_year = get_project_settings().get('IEEE_YEAR')
    ieee_base_url = 'https://ieeexplore.ieee.org'

    def __init__(self):
        super(IEEESpider, self).__init__()
        self.startPage = 0
        self.pageSize = 25 # IEEE advanced search默认每页显示25篇文章。也许以后会变动
    
    def start_requests(self):
        for url in self.ieee_urls:
            parentId = url[40:47]
            conference_list_url = 'https://ieeexplore.ieee.org/rest/publication/conhome/metadata?parentId=' + parentId
            yield scrapy.Request(
                url=conference_list_url,
                callback=self.parse_conference_list,
                headers={
                    'Referer': url,
                    'Host': self.allowed_domains[0],
                    'Origin': self.ieee_base_url,
                    'Content-Type': 'application/json'
                },
            )
    
    # 获得此会议历年的列表，遍历获取每个issue的metadata（来获取issue的doi）。遍历判断每个issue是否符合年份要求，符合的继续请求
    def parse_conference_list(self, response):
        conference_list = json.loads(response.text)
        logging.info("start crawling conferences")
        logging.info("successfully crawled conferences list, url = {}".format(response.request.headers['Referer']))
        
        for record in conference_list['records']:
            for issue in record['issues']:
                if int(issue['year']) >= self.ieee_year['from'] and int(issue['year']) <= self.ieee_year['to']:
                    yield scrapy.Request(
                        url='https://ieeexplore.ieee.org/rest/publication/home/metadata?pubid=' + record['publicationNumber'],
                        callback=self.parse_conference,
                        method='GET',
                        headers={
                            'Host': 'ieeexplore.ieee.org',
                            'Referer': 'https://ieeexplore.ieee.org/xpl/conhome/{}/proceeding'.format(record['publicationNumber'])
                        },
                        meta={
                            'publicationNumber': record['publicationNumber'],
                            'issueNumber': issue['issueNumber']
                        }
                    )

                    
    
    def parse_conference(self, response):
        """
        主要是获取publication doi然后作为meta传入之后的request
        """
        # save_str_file(response.text, 'IEEE_conference_example.json')
        content = json.loads(response.text)
        publicationDoi = content['publicationDoi']
        publication_number = response.meta['publicationNumber']
        issue_number = response.meta['issueNumber']
        payload = {
            'punumber': publication_number,
            'isnumber': issue_number
        }
        payload = json.dumps(payload)
        # 从此issue的第一页开始
        yield scrapy.Request(
            url='https://ieeexplore.ieee.org/rest/search/pub/{}/issue/{}/toc'.format(publication_number, issue_number),
            callback=self.parse_issue,
            method='POST',
            headers={
                'Host': 'ieeexplore.ieee.org',
                'Origin': 'https://ieeexplore.ieee.org',
                'Referer': 'https://ieeexplore.ieee.org/xpl/conhome/{}/proceeding'.format(publication_number),
                'Content-Type': "application/json"
            },
            body=json.dumps({
                "punumber":publication_number,"isnumber":issue_number,"pageNumber": 1
            }),
            meta={
                'publicationDoi': publicationDoi
            }
        )

    
    # 某issue的某页
    def parse_issue(self, response):
        # save_str_file(response.text, 'IEEE_issue_example.json')
        content = json.loads(response.text)
        request_body = json.loads(response.request.body)
        logging.info("start crawling conference issue {}, page {} / {}".format(response.request.headers['Referer'], request_body['pageNumber'], content['totalPages']))

        #处理此页的所有文章
        for record in content['records']:
            # usually record without author is no paper, but information like title, reviewer panel, author index, etc.
            if 'authors' in record:
                yield scrapy.Request(
                    url=self.ieee_base_url + record['documentLink'],
                    callback=self.parse_document,
                    meta={
                        'publicationDoi': response.meta['publicationDoi']
                    }
                )


        # 如果不是最后一页，继续爬取
        if request_body['pageNumber'] < content['totalPages']:
            request_body['pageNumber'] += 1
            yield scrapy.Request(
                        url=response.request.url,
                        callback=self.parse_issue,
                        method='POST',
                        headers=response.request.headers,
                        body=json.dumps(request_body),
                        meta={
                            'publicationDoi': response.meta['publicationDoi']
                        }
                    )
        
    def parse_document(self, response):
        """parse a single IEEE document(expect to be an IEEE paper), yield a request for references and passes a item including the paper's information(without references) define in data_crawler/items

        keyword arguments:
        search_res -- search result for the metadata, which contains the information needed.
        paper_item -- paper information(without references) to be yield
        """
        #save_str_file(response.text, 'IEEE_document.json')

        # 取结果中的metadata部分（论文的元数据，其中包含需要的内容）
        pattern = re.compile('metadata={.*};')
        search_res = pattern.search(response.text)

        paper_item = IEEEPaperItem()
    
        # TODO: in what case doesn't the document contain metadata? 
        if search_res:
            content = json.loads(search_res.group()[9:-1])
            required = ['title', 'authors', 'abstract',
                        'doi', 'publicationTitle', 'publicationYear', 'metrics',
                        'contentType', 'keywords']
            # contentType: conference, journal, book
            for i in required:
                paper_item[i] = content.get(i, None)
            paper_item['publicationDoi'] = response.meta['publicationDoi']

            # deal with reference
            yield scrapy.Request(
                url='https://ieeexplore.ieee.org/rest/document/{}/references'.format(content['articleNumber']),
                callback=self.parse_references,
                meta={'paper_item': paper_item}
            )
        else:
            yield None
    def parse_references(self, response):
        """ parse references of a paper. Yield the complete paper item
        """
        # save_str_file(response.text, 'refereneces.json')
        references = []
        item = response.meta['paper_item']
        content = json.loads(response.text)
        for reference in content.get('references'):
            ref = {}
            ref['order'] = reference.get('order')
            ref['text'] = reference.get('text') # could be the reference citation
            ref['links'] = reference.get('links')
            ref['title'] = reference.get('title')
            references.append(ref)
        item['references'] = references
        yield item
            