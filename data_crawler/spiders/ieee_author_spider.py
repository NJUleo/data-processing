import json
import re
import logging
import random

import scrapy

from data_crawler.spiders.utils import save_byte_file
from data_crawler.spiders.utils import save_str_file

class IEEEAuthorSpider(scrapy.Spider):
    name = "ieee_author"
    base_url = "https://ieeexplore.ieee.org/author/"
    pattern = '[^A-Z]+'

    def start_requests(self):

        start = 37085628262
        end =   37085728262
        # 某个作者的范围 TODO:需要确定这个范围的具体值如何。

        # 无限循环持续进行？
        for num in range(1):
            # 随机选择一个作者
            link_num = random.randrange(start, end)
            # if collection.find_one({'ieeeId': link_num}):
            #     continue
            link_num = 37085628262 #TODO:仅用于测试，只爬取贺之张的主页
            link_num = str(link_num)
            url = self.base_url + link_num
            yield scrapy.Request(url=url, callback=self.parse_author, meta={'link_num': link_num})
            # yield scrapy.Request(url='https://ieeexplore.ieee.org/author/' + link_num, callback=self.parse_author, meta={'link_num': link_num})
    
    def parse_author(self, response):
        save_byte_file(response.body, 'author')
        yield scrapy.Request(url="https://ieeexplore.ieee.org/rest/author/37077817100", callback=self.parse_author_rest)
        # yield scrapy.Request(url = "https://ieeexplore.ieee.org/rest/user/info", callback=self.parse_info, meta={'link_num': response.meta['link_num']})

    def parse_author_rest(self, response):
        save_byte_file(response.body, 'author_rest')
    
    def parse_info(self, response):
        save_byte_file(response.body, 'info')
        search_payload = [{"searchWithin":["\"Author Ids\":37077817100"],"history":"no","sortType":"newest","highlight":True,"returnFacets":["ALL"],"returnType":"SEARCH","matchPubs":True}]
        yield scrapy.Request(url='https://ieeexplore.ieee.org/rest/search', body=json.dumps(search_payload), method="POST", callback=self.parse_search)

    def parse_search(self, response):
        save_byte_file(response.body, 'search')
    
