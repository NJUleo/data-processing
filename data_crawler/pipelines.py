# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
import json

from data_crawler.items import IEEEPaperItem
from scrapy.exceptions import DropItem

class DataCrawlerPipeline:
    def process_item(self, item, spider):
        return item

# 空的item去除
class RemoveEmptyItemPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if item == None:
            raise DropItem("found none item")
        if isinstance(item, IEEEPaperItem):
            # TODO: 暂时对于空的paper的判断是通过是否有title来进行，可能要进行修改
            if item.get('title') == None:
                raise DropItem("ieee paper item found: %r" % item)

        return item


# 将所有的item保存为json。TODO: 其他正式的保存方式
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('test_files/crawled_items.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item