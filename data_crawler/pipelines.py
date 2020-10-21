# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
import json

from data_crawler.items import IEEEPaperItem
from scrapy.exceptions import DropItem

import pymysql
import datetime
from twisted.enterprise import adbapi
import logging


class DataCrawlerPipeline:
    def process_item(self, item, spider):
        return item

# 空的item去除
class RemoveEmptyItemPipeline:
    def process_item(self, item, spider):
        if item == None:
            raise DropItem("found none item")
        if isinstance(item, IEEEPaperItem) and item.get('title') == None:
            # TODO: 暂时对于空的paper的判断是通过是否有title来进行，可能要进行修改
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

class MysqlPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
        )
        # 连接数据池ConnectionPool，使用pymysql连接
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
        # 返回实例化参数
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
        """
        
        query = self.dbpool.runInteraction(self.do_insert_IEEE_paper, item)  # 指定操作方法和操作数据
        # 添加异常处理
        query.addCallback(self.handle_error)  # 处理异常

    def do_insert_IEEE_paper(self, cursor, item):
        """
        对数据库插入一篇文章，并不需要commit，twisted会自动commit
        """
        # insert database table: paper
        insert_sql = """
            insert into paper(id, title, abs, publication_id, publication_date, link) VALUES(%s,%s,%s,%s,%s,%s)
                    """
        # TODO: 获得IEEE conference doi（publication_id） 目前只有title，因此暂且作为id保存
        self.execute_sql(
            insert_sql, 
            (item['doi'], item['title'], item['abstract'], item['publicationTitle'], item['publicationYear'], 'doi.org/' + item['doi']),
            cursor,
            self.merge_paper,
            (item,)
        )

        # insert database table: researcher paper_researcher
        # 学者的id为 数据库名_数据库内部ID 如IEEE_37086831215
        order = 0
        for author in item['authors']:
            order += 1

            # insert database table: researcher
            insert_author_sql = """
                            insert into researcher(`id`, `name`) VALUES(%s, %s)
                            """
            self.execute_sql(
                insert_author_sql,
                ('IEEE_' + author['id'], author['name']),
                cursor
            )

            # insert database table: paper_researcher
            insert_paper_researcher_sql = """
                            insert into paper_researcher(`pid`, `rid`, `order`) VALUES(%s, %s, %s)
                            """
            self.execute_sql(
                insert_paper_researcher_sql,
                (item['doi'], 'IEEE_' + author['id'], order),
                cursor,
            )

            # insert database table: domain paper_domain
            # TODO: 暂时把所有的关键词作为domain存储
            insert_domain_sql = """
            insert into domain(`name`) VALUES(%s)
            """
            insert_paper_domain_sql = """
            insert into paper_domain(`pid`, `dname`) VALUES(%s, %s)
            """
            # 将IEEE controlled index作为domain存储
            for keyword_group in item['keywords']:
                if keyword_group['type'] == 'INSPEC: Controlled Indexing':
                    for controlled_index in keyword_group['kwd']:
                        # insert database table: domain
                        self.execute_sql(
                            insert_domain_sql, 
                            (controlled_index,),
                            cursor
                        )
                        # insert database table: paper_domain
                        self.execute_sql(
                            insert_paper_domain_sql, 
                            (item['doi'], controlled_index),
                            cursor
                        )



    @staticmethod
    def execute_sql(sql, values, cursor, callback_dulp_key = None, callback_dulp_key_args = None):
        """
        callback_dupl_key是插入数据库时发现key重复时的回调函数(当且仅当传了这个参数)
        callback_dulp_key_args是一个iterable, unpack之后作为callback_dulp_key's arguments 
        """
        try:
            cursor.execute(sql, values)
        except pymysql.err.IntegrityError as e:
            if(e.args[0] == 1062) and (callback_dulp_key != None):
                # 1062是pymysql duplicate key的错误码
                callback_dulp_key(*callback_dulp_key_args)   
            else:
                # TODO: other exceptions
                logging.warning(e)

    def merge_paper(self, item):
        """
        TODO:发现IEEE ACM的重复文章，合并其中的所有作者、所有affliation
        """
        pass

    def handle_error(self, failure):
        if failure:
            # 打印错误信息
            print(failure)
            logging.error('$ messages from MysqlPipeline: ' + str(failure))

