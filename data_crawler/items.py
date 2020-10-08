# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DataCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class IEEEPaperItem(scrapy.Item):
    title = scrapy.Field()
    authors = scrapy.Field()
    abstract = scrapy.Field()
    publicationTitle = scrapy.Field()
    doi = scrapy.Field()
    publicationYear = scrapy.Field()
    metrics = scrapy.Field()
    contentType = scrapy.Field()
