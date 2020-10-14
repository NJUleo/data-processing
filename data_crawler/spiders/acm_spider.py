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

class ACMSpider(scrapy.Spider):
    name = "ACM_Paper"
    allowed_domains = ["dl.acm.org"]
    start_urls = get_project_settings().get('ACM_URL')

    def __init__(self):
        super(ACMSpider, self).__init__()
        self.startPage = 0
        self.pageSize = 20 # ACM advanced search默认每页显示20篇文章。也许以后会变动

    def parse(self, response):
        print('爬取第', self.startPage, '页')

        # 搜索结果中的文章总数
        results_num = response.xpath('//span[@class="hitsLength"]/text()').get()

        # 对应url没有发现文章时报错
        if(results_num == 0):
            logging.error("no paper found for this url")
            raise scrapy.exceptons.CloseSpider("no_paper")
        logging.info("{} ACM paper found".format(results_num))

        # 所有paper的selector
        papers = response.xpath('//div[@class="issue-item__content-right"]')

        # 依次爬取每篇paper的页面
        for paper in papers:
            paper_url = paper.xpath('.//span[@class="hlFld-Title"]/a/@href').get()
            paper_url = 'https://dl.acm.org' + paper_url
            yield scrapy.Request(url=paper_url, callback=self.parse_paper)

        logging.warning('$ ACM_Spider已爬取：' + str((self.startPage + 1) * self.pageSize))
        
        # 搜索结果多页时，依次爬完所有页
        if (self.startPage + 1) * self.pageSize < int(results_num) and self.startPage < 1:
            self.startPage += 1
            next_url = self.start_urls[0] + '&startPage=' + str(self.startPage) + '&pageSize=' + str(self.pageSize)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
            )
    def parse_paper(self, response):
        yield parse_acm_paper(self, response)