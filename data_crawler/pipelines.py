# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class DataCrawlerPipeline:
    def process_item(self, item, spider):
        return item


# 将所有的item保存为json。TODO: 其他正式的保存方式
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('crawled_items.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item