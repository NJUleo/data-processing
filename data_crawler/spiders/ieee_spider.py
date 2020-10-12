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

from data_crawler.items import ACMPaperItem

class IEEESpider(scrapy.Spider):
    name = "IEEE_Paper"
    allowed_domains = ["ieeexplore.ieee.org"]
    ieee_urls = get_project_settings().get('IEEE_CONF_URLS')
    ieee_year = get_project_settings().get('IEEE_YEAR')

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
                    'Host': 'ieeexplore.ieee.org'
                }
            )
    
    # 获得此会议历年的列表，遍历判断每个issue是否符合年份要求，符合的继续请求
    def parse_conference_list(self, response):
        conference_list = json.loads(response.text)
        for record in conference_list['records']:
            for issue in record['issues']:
                if int(issue['year']) >= self.ieee_year['from'] and int(issue['year']) <= self.ieee_year['to']:
                    payload = {
                        'punumber': record['publicationNumber'],
                        'isnumber': issue['issueNumber']
                    }
                    payload = json.dumps(payload)
                    yield scrapy.Request(
                        url='https://ieeexplore.ieee.org/rest/search/pub/{}/issue/{}/toc'.format(record['publicationNumber'], issue['issueNumber']),
                        callback=self.parse_issue,
                        method='POST',
                        headers={
                            'Host': 'ieeexplore.ieee.org',
                            'Origin': 'https://ieeexplore.ieee.org',
                            'Referer': 'https://ieeexplore.ieee.org/xpl/conhome/{}/proceeding'.format(record['publicationNumber']),
                            'Content-Type': "application/json"
                        },
                        body=json.dumps({
                            "punumber":record['publicationNumber'],"isnumber":issue['issueNumber']
                        })
                    )
    
    def parse_issue(self, response):
        yield None
        
    