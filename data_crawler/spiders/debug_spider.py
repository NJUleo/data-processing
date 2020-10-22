import json

import scrapy
from data_crawler.items import IEEEPaperItem, ACMPaperItem

class DebugSpider(scrapy.Spider):
    """
    用于debug，直接读取之前爬取的内容，然后作为item传给pipeline处理
    """
    name = "debug"

    def start_requests(self):
        yield scrapy.Request('http://quotes.toscrape.com/page/1/')
    
    def parse(self, response):
        with open('test_files/crawled_items_debug.json') as f:
            for line in f:
                if 'index_term_tree' in item:
                    # ACM
                    paper = ACMPaperItem()
                else:
                    paper = IEEEPaperItem()
                # TODO: 确定文件中是什么类型的item
                item = json.loads(line)
                for key in item:
                    paper[key] = item[key]
                yield paper
