import json
import logging

import scrapy

from data_crawler.spiders.utils import save_str_file

from scrapy.utils.project import get_project_settings

class ProxySpider(scrapy.Spider):
    """
    crawl proxies from https://www.kuaidaili.com/free/, stored in text_filex/proxies.txt
    """

    name = 'kuai_proxy'
    start_urls = ['https://www.kuaidaili.com/free/']

    def parse(self, response):
        proxy_ips = response.xpath('.//div[@id="list"]/table/tbody/tr/td[@data-title="IP"]/text()').getall()
        proxy_ports = response.xpath('.//div[@id="list"]/table/tbody/tr/td[@data-title="PORT"]/text()').getall()
        result = ''
        for i in range(len(proxy_ips)):
            result += proxy_ips[i] + ':' + proxy_ports[i] + '\n'
        save_str_file(result, 'proxies.txt')
        yield None

