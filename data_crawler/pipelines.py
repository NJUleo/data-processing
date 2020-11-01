# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
import json

from data_crawler.items import IEEEPaperItem, PaperItem, ACMPaperItem
from scrapy.exceptions import DropItem
from data_crawler.utils import hash_str as encode

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

class ACMPaper2UnifyPipeline:
    """
    transfer ACM paper item to unify paper item
    """
    def process_item(self, item, spider):
        def get_acm_keywords(tree):
            """
            从ACM index tree中获得所有关键词
            """
            result = []
            if tree['url'] != None:
                # 根结点是没有url的，其title是文章标题
                result.append(tree['title'])
            for child in tree['child']:
                result.extend(get_acm_keywords(child))
            return result
        # 只处理ACMPaperItem
        if not isinstance(item, ACMPaperItem):
            return item
        paper = PaperItem()
        paper['title'] = item['title']

        order = 0
        paper_authors = []
        for author in item['authors']:
            order += 1
            paper_author = {
                'id': 'ACM_' + author['author_profile'][19:], # "dl.acm.org/profile/99659280949" removed 'dl.acm.org/profile/', 19 charactors
                'name': author['author_name'],
                'order': order
            }
            paper_authors.append(paper_author)
        paper['authors'] = paper_authors        
        paper['abstract'] = item['abstract']
        paper['publicationDoi'] = item['conference']['conference_doi']
        paper['publication_id'] = encode(item['conference']['conference_doi'])
        paper['publicationTitle'] = item['conference']['conference_title']
        paper['doi'] = item['doi']
        paper['id'] = encode(item['doi'])
        paper['citation'] = '0' # TODO:
        paper['publicationYear'] = item['month_year'].split()[1]
        
        # TODO: 需要把reference改为统一从google scholar来获取
        paper_references = []
        paper_ref_citaion = []
        for reference in item['references']:
            no_dl = True # whether this reference has DL link, if not, store the citation.
            for link in reference['reference_links']:
                if link['link_type'] == 'Digital Library':
                    # logging.warning(link['link_type'])
                    # 形式可能是 "/doi/10.1109/TSE.2015.2419611" 或 "https://dl.acm.org/doi/10.1145/3092703.3092718"
                    link_element = link['link_url'].split('/')
                    paper_references.append(link_element[len(link_element) - 2] + '/' + link_element[len(link_element) - 1])
                    no_dl = False
            if no_dl:
                paper_ref_citaion.append(reference['reference_citation'])

        paper['references'] = paper_references
        paper['ref_citation'] = paper_ref_citaion
        paper['ref_ieee_document'] = []
        paper['ref_title'] = []
        
        paper['keywords'] = get_acm_keywords(item['index_term_tree'])

        return paper


class IEEEPaper2UnifyPipeline:
    """
    transfer IEEE paper item to unify paper item
    """
    def process_item(self, item, spider):
        # 只处理IEEEPaperItem
        if not isinstance(item, IEEEPaperItem):
            return item
        paper = PaperItem()
        paper['title'] = item['title']

        order = 0
        paper_authors = []
        for author in item['authors']:
            order += 1
            paper_author = {
                'id': 'IEEE_' + author['id'],
                'name': author['name'],
                'order': order
            }
            paper_authors.append(paper_author)
        paper['authors'] = paper_authors
        paper['abstract'] = item['abstract']
        paper['publicationDoi'] = item['publicationDoi']
        paper['publication_id'] = encode(item['publicationDoi'])
        paper['publicationTitle'] = item['publicationTitle']
        paper['doi'] = item['doi']
        paper['id'] = encode(paper['doi'])
        paper['citation'] = item['metrics']['citationCountPaper']
        paper['publicationYear'] = item['publicationYear']

        # 对IEEE需要处理两种：crossRefLink acmLink. 第三种是document类型的，需要爬一个新的页面。
        paper_references_doi = []
        paper['ref_ieee_document'] = []
        paper['ref_title'] = []
        paper['ref_citation'] = []
        for reference in item['references']:
            if 'links' in reference and reference['links'] != None:
                reference_doi = ''
                if 'acmLink' in reference['links']:
                    if 'https://doi.org/' in reference['links']['acmLink']:
                        reference_doi = reference['links']['acmLink'][16:]
                elif 'crossRefLink' in reference['links']:
                    if 'https://doi.org/' in reference['links']['crossRefLink']:
                        # 不确定是否crossref都是doi开头，故只取doi的
                        reference_doi = reference['links']['crossRefLink'][16:] # remove https://doi.org/, 16 charactors
                elif 'documentLink' in reference['links']:
                    paper['ref_ieee_document'].append(reference['links']['documentLink'])
                    continue
                else:
                    paper['ref_title'].append(reference['title'])
                    continue
                paper_references_doi.append(reference_doi)
            else:
                # no links, only avaliable in google scholar
                paper['ref_title'].append(reference['title'])
        paper['references'] = paper_references_doi
        
        paper_keywords = []
        # 将IEEE controlled index作为domain存储
        for keyword_group in item['keywords']:
            if keyword_group['type'] == 'INSPEC: Controlled Indexing':
                for controlled_index in keyword_group['kwd']:
                    paper_keywords.append(controlled_index)
        paper['keywords'] = paper_keywords
        return paper
    
class UnifyPaperMysqlPipeline(object):
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
            cursorclass=pymysql.cursors.DictCursor,  # 指定cursor类型
            port=settings['MYSQL_PORT']
        )
        # 连接数据池ConnectionPool，使用pymysql连接
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
        # 返回实例化参数
        return cls(dbpool)

    def process_item(self, item, spider):
        # 只处理PaperItem
        if not isinstance(item, PaperItem):
            return item
        """
        使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
        """
        
        query = self.dbpool.runInteraction(self.do_insert_paper, item)  # 指定操作方法和操作数据
        # 添加异常处理
        query.addCallback(self.handle_error)  # 处理异常

    def do_insert_paper(self, cursor, paper):
        """
        对数据库插入一篇文章，并不需要commit，twisted会自动commit
        """
        logging.debug('inserting paper doi "{}" to mysql'.format(paper['doi']))
        # insert database table: paper
        insert_sql = """
            insert into paper(id, title, abs, publication_id, publication_date, link, citation) VALUES(%s,%s,%s,%s,%s,%s,%s)
                    """
        self.execute_sql(
            insert_sql, 
            (paper['id'], paper['title'], paper['abstract'], paper['publication_id'], paper['publicationYear'], 'doi.org/' + paper['doi'], paper['citation']),
            cursor,
            self.merge_paper,
            (paper,)
        )

        # insert database table: researcher paper_researcher
        # 学者的id为 数据库名_数据库内部ID 如IEEE_37086831215
        for author in paper['authors']:

            # insert database table: researcher
            insert_author_sql = """
                            insert into researcher(`id`, `name`) VALUES(%s, %s)
                            """
            self.execute_sql(
                insert_author_sql,
                (author['id'], author['name']),
                cursor
            )

            # insert database table: paper_researcher
            insert_paper_researcher_sql = """
                            insert into paper_researcher(`pid`, `rid`, `order`) VALUES(%s, %s, %s)
                            """
            self.execute_sql(
                insert_paper_researcher_sql,
                (paper['id'], author['id'], author['order']),
                cursor,
            )

        # insert database table: domain paper_domain
        # TODO: 暂时把所有的关键词作为domain存储
        insert_domain_sql = """
        insert into domain(`id`, `name`) VALUES(%s, %s)
        """
        insert_paper_domain_sql = """
        insert into paper_domain(`pid`, `did`) VALUES(%s, %s)
        """
        for keyword in paper['keywords']:
            logging.debug('inserting keyword "{}" in paper "{}" "{}"'.format(keyword, paper['doi'], paper['title']))
            self.execute_sql(
                insert_domain_sql, 
                (encode(keyword), keyword),
                cursor
            )
            # insert database table: paper_domain
            self.execute_sql(
                insert_paper_domain_sql, 
                (paper['id'], encode(keyword)),
                cursor
            )
            
        # insert database table: paper_reference
        # 1.这里的reference是所有能够获得doi的文章，其他的reference被忽略；
        # 2.很可能这个doi不在爬取的范围内，既在paper表中没有这个doi。
        insert_paper_reference_sql = """
        insert into paper_reference(`pid`, `rid`) VALUES(%s, %s)
        """
        for reference_doi in paper['references']:
            self.execute_sql(
                insert_paper_reference_sql,
                (paper['id'], encode(reference_doi)),
                cursor
            )
        
        # insert database table: publication
        insert_publication_sql = """
        insert into publication(`id`, `name`, `publication_date`) VALUES(%s, %s, %s)
        """
        self.execute_sql(
            insert_publication_sql,
            (paper['publication_id'], paper['publicationTitle'], paper['publicationYear']),
            cursor
        )

        # 仅用于进一步爬取
        # insert database table: paper_ieee_reference_document, paper_reference_citation, paper_reference_title
        for ieee_doc in paper['ref_ieee_document']:
            self.execute_sql(
                'insert into paper_ieee_reference_document(`pid`, `ieee_document`) VALUES(%s, %s)',
                (paper['id'], ieee_doc),
                cursor
            )
        for title in paper['ref_title']:
            self.execute_sql(
                'insert into paper_reference_title(`pid`, `reference_title`) VALUES(%s, %s)',
                (paper['id'], title),
                cursor
            )
        for citation in paper['ref_citation']:
            self.execute_sql(
                'insert into paper_reference_citation(`pid`, `reference_citation`) VALUES(%s, %s)',
                (paper['id'], citation),
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

