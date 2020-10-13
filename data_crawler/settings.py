# -*- coding: utf-8 -*-

# Scrapy settings for ieee project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import datetime
import rotating_proxies
import os

# 是否为debug模式，如果是, 不使用proxy
DEBUG = False

tem_dir=['scrapy_logs', 'test_files']
for dir in tem_dir:
    if not os.path.exists(dir):
        os.makedirs(dir)

BOT_NAME = 'data_crawler'

SPIDER_MODULES = ['data_crawler.spiders']
NEWSPIDER_MODULE = 'data_crawler.spiders'

# URL for Spider
# TODO: 切换到需要爬取的url（某个search result）
IEEE_URL = ['https://ieeexplore.ieee.org/document/']
ACM_URL = ['https://dl.acm.org/action/doSearch?fillQuickSearch=false&expand=dl&field1=AllField&text1=shit&Ppub=%5B20200907+TO+20201007%5D'] # 填入ACM的地址

IEEE_CONF_URLS = ['https://ieeexplore.ieee.org/xpl/conhome/1000064/all-proceedings']
# 需要的年份(including 'from' and 'to')
IEEE_YEAR = {
    'from': 2010,
    'to': 2020
}

#HTTPERROR_ALLOWED_CODES  =[400]

# Time
START_TIME = datetime.datetime.now()

# LOG
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy_logs/Scrapy_{}_{}_{}_{}_{}_{}.log'.format(START_TIME.year, START_TIME.month, START_TIME.day, START_TIME.hour, START_TIME.minute, START_TIME.second)

# Retry Setting

# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'ieee (http://116.62.23.105)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ieee.middlewares.IeeeSpiderMiddleware': 543,
#}

# rataing_proxy
ROTATING_PROXY_LIST_PATH = 'proxies.txt'

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html


DOWNLOADER_MIDDLEWARES = {
    'data_crawler.middlewares.RandomUserAgentMiddleware': 400,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610 if not DEBUG else None,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620 if not DEBUG else None,
    'data_crawler.middlewares.RequestLogMiddleware': None,
    'data_crawler.middlewares.ResponseLogMiddleware': None
}

ITEM_PIPELINES = {
    'data_crawler.pipelines.RemoveEmptyItemPipeline': 500,
    'data_crawler.pipelines.JsonWriterPipeline': 888,
}
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'ieee.pipelines.IeeePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
