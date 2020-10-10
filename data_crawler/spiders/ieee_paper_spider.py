import json
import re
import logging
import random

import scrapy

from data_crawler.spiders.utils import get_keywords # 获取关键词
from data_crawler.spiders.utils import save_byte_file
from data_crawler.spiders.utils import save_str_file

from data_crawler.items import IEEEPaperItem

from scrapy.utils.project import get_project_settings # 获取settings.py配置文件中的信息


class IEEESpider(scrapy.Spider):
    name = "ieee"
    base_url = get_project_settings().get('IEEE_URL')[0] # 从setting.py配置文件中获取url

    def start_requests(self):

        start = 1000000
        end = 9080201
        # 某个文章的范围 TODO: 需要将这种方式改成爬取某个search result

        # TODO: 需要改成一个合适的循环（爬取文章）的数量，暂时由于未配置代理，仅爬取五次避免ip封锁
        for _ in range(5):
            # 随机选择一篇IEEE文章
            link_num = random.randrange(start, end)
            
            link_num = str(link_num)
            url = self.base_url + link_num
            yield scrapy.Request(url= url, callback=self.parse_paper, meta={'link_num': link_num})

    def parse_paper(self, response):

        # 取结果中的metadata部分（论文的元数据，其中包含需要的内容）
        pattern = re.compile('metadata={.*};')
        search_res = pattern.search(response.text)

        item = IEEEPaperItem()
    
        if search_res:
            content = json.loads(search_res.group()[9:-1])

            required = ['title', 'authors', 'abstract',
                        'publicationTitle', 'doi', 'publicationYear', 'metrics',
                        'contentType']
            # contentType: conference, journal, book
            for i in required:
                item[i] = content.get(i, None)
            yield item