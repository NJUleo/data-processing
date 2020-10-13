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

from data_crawler.spiders.acm_paper_parser import parse_acm_paper

from urllib.parse import urlencode

class ACMProceedingSpider(scrapy.Spider):
    name = "ACM_Proceedings"
    allowed_domains = ["dl.acm.org"]
    start_urls = get_project_settings().get('ACM_PROCEEDING_URL')

    def __init__(self):
        super(ACMProceedingSpider, self).__init__()
        self.startPage = 0
        self.pageSize = 20 # ACM advanced search默认每页显示20篇文章。也许以后会变动

    def parse(self, response):
        """
        由于ACM proceeding页面使用懒加载，需要
        1. 获取必要的用于模拟懒加载请求的，不知道什么意思的request payload, pbContext.
        2. 获得目标组件（SESSIONS列表）的widgetId
        3. 获得ssession
        4. 对每个session，获取head id
        5. 依次请求每个session
        6. 对每个session的所有文章依次爬取文章界面。
        
        """
        # request payload for lazy loading
        pbContext = response.xpath('./head/meta/@content').get()
        doi =  response.request.url[35:] # proceeding url is https://dl.acm.org/doi/proceedings/ + doi
        widget = response.xpath('//div[@class="table-of-content table-of-content--lazy"]/..')
        widgetId = widget.xpath('./@data-widgetid').get()

        session_ids = widget.xpath('//div/a[contains(@class, "section__title")]/@id').getall()

        for session_id in session_ids:
            query_string_param = {
                'tocHeading': session_id,
                'widgetId': widgetId,
                'doi': doi,
                'pbContext': pbContext
            }
            yield scrapy.Request(
                url='https://dl.acm.org/pb/widgets/lazyLoadTOC?' + urlencode(query_string_param),
                callback=self.parse_session,
                meta={
                    # information just for logging
                    'proceeding_doi': doi,
                    'session_heading': session_id,
                    'session_num': len(session_ids)
                }
            )

    def parse_session(self, response):
        self.logger.info('crawled ACM proceeding {} session {} paper list, totoal {} sessions'.format(
            response.meta['proceeding_doi'], 
            response.meta['session_heading'][7:], 
            response.meta['session_num']))
        papers_dois = response.xpath('//div[@class="issue-item__content-right"]/h5/a/@href').getall()
        for paper_doi in papers_dois:
            yield scrapy.Request(
                url='https://dl.acm.org' + paper_doi,
                callback=self.parse_paper
            )
    
    def parse_paper(self, response):
        yield parse_acm_paper(self, response)
