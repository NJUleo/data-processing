import configparser
import pymysql
import logging
import random
from functools import reduce
import sys
from utils import hash_str
from utils import encode_id
config = configparser.ConfigParser()
config.read('./merge/merge.ini')


# Connect to database merge
merge_database_setting = config['merge Database']
connection_merge = pymysql.connect(
    host=merge_database_setting['MYSQL_HOST'],
    user=merge_database_setting['MYSQL_USER'],
    password=merge_database_setting['MYSQL_PASSWORD'],
    db=merge_database_setting['MYSQL_DBNAME'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    port=int(merge_database_setting['MYSQL_PORT']))

# Connect to database_ieee
ieee_database_setting = config['IEEE Database']
connection_ieee = pymysql.connect(
    host=ieee_database_setting['MYSQL_HOST'],
    user=ieee_database_setting['MYSQL_USER'],
    password=ieee_database_setting['MYSQL_PASSWORD'],
    db=ieee_database_setting['MYSQL_DBNAME'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    port=int(ieee_database_setting['MYSQL_PORT']))

# Connect to database_acm
acm_database_setting = config['ACM Database']
connection_acm = pymysql.connect(
    host=acm_database_setting['MYSQL_HOST'],
    user=acm_database_setting['MYSQL_USER'],
    password=acm_database_setting['MYSQL_PASSWORD'],
    db=acm_database_setting['MYSQL_DBNAME'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    port=int(acm_database_setting['MYSQL_PORT']))


def my_select(connection, sql):
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        return res
    except Exception as e:
        logging.warning('error in select, sql {}'.format(sql))
        connection.rollback()
        raise e
    finally:
        cursor.close()

def my_insert_many(connection, sql, values):
    try:
        cursor = connection.cursor()
        cursor.executemany(sql, values)
        connection.commit()
    except pymysql.err.IntegrityError as e:
        logging.warning(e.args[1])
    except Exception as e:
        logging.warning('error in insert, sql {}'.format(sql))
        connection.rollback()
        raise e
    finally:
        cursor.close()


def get_same_from_it(src, target, is_equal = lambda src_item, target_item: src_item == target_item):
    """
    从可迭代对象中找出某个元素（自定义相等），没有则返回None
    """
    for i in src:
        if is_equal(i, target):
            return i
    return None

def change_merge_map(from_list, to_list, mapping_list, change = lambda x: x, update = lambda x, y: x, is_equal = lambda x, y: x == y, src = 'unknown', equal_callback = lambda x, y: None):
    """
    将一个list所有的元素做变化（change），加入另一之中（merge），重复的不加入（通过函数定义），每次记录对应（mapping）
    必须有id
    src 为来源标识（比如，acm， ieee）
    """
    for item in from_list:
        main_record = get_same_from_it(to_list, item, is_equal)
        if main_record != None:
            # 已有记录
            main_record = update(main_record, item)
            mapping_list.append((
                main_record['id'],
                item['id'],
                src,
                True
            ))
            # 所有其他的对应的也认为是 true
            for i in mapping_list:
                if i[0] == main_record['id'] and i[3] == False:
                    new_map_record = (i[0], i[1], i[2], True)
                    mapping_list.remove(i)
                    mapping_list.append(new_map_record)
                    break
            equal_callback(main_record, item)
            logging.info('found equal{},{}'.format(main_record, item))
        else:
            new_main_record = item.copy()
            new_main_record = change(new_main_record)
            to_list.append(new_main_record)
            mapping_list.append((
                new_main_record['id'],
                item['id'],
                src,
                False
            ))

def change_ieee_id_src(item):
    item['id'] = hash_str('ieee' + item['id'])
    return item

def change_acm_id_src(item):
    item['id'] = hash_str('acm' + item['id'])
    return item


def merge_publication():
    # merge publication by name and publication time
    publications_ieee = my_select(connection_ieee, 'select * from publication')
    publications_acm = my_select(connection_acm, 'select * from publication')
    publications = []
    publication_mapping = []

    change_merge_map(publications_ieee, publications, publication_mapping, change=change_ieee_id_src, is_equal=lambda x, y: x['name'] == y['name'] and x['publication_date'] == y['publication_date'], src='IEEE')

    change_merge_map(publications_acm, publications, publication_mapping, change=change_acm_id_src, is_equal=lambda x, y: x['name'] == y['name'] and x['publication_date'] == y['publication_date'], src='ACM')

    # 按照下面 sql 对应顺序把字典改为元组
    publications = list(map(
        lambda x: (x['id'], x['name'], x['publication_date'], str(random.uniform(0, 1))),
        publications
    ))
    my_insert_many(connection_merge, 'insert ignore into publication_mapping values(%s, %s, %s, %s)', publication_mapping)
    my_insert_many(connection_merge, 'insert ignore into publication(`id`, `name`, `publication_date`, `impact`) VALUES(%s, %s, %s, %s)', publications)
    return publication_mapping

publication_mapping = merge_publication()

def merge_paper():
    # paper
    # TODO: 也许全加载到内存不是一个好主意。以后再重构。
    paper_mapping = []
    papers = []
    paper_ieee = my_select(connection_ieee, 'select * from paper')
    paper_acm = my_select(connection_acm, 'select * from paper')

    def paper_is_equal(p1, p2):
        """
        return true if two paper is the same paper
        """
        if p1.get('doi') == p2.get('doi') and p1.get('doi') != None:
            return True
        if p1['title'] == p2['title']:
            return True
        return False
    def update_paper(main_record, new_record):
        if main_record['link'] == None:
            main_record['link'] = new_record['link']
        if main_record['doi'] == None:
            main_record['doi'] = new_record['doi']
        print('haha')
        return main_record
    change_merge_map(paper_ieee, papers, paper_mapping, change=change_ieee_id_src, is_equal=paper_is_equal, src='IEEE', update=update_paper)
    change_merge_map(paper_acm, papers, paper_mapping, change=change_acm_id_src, is_equal=paper_is_equal, src='ACM', update=update_paper)

    for paper in papers:
        # map the publication id
        publication_map_record = get_same_from_it(publication_mapping, paper, lambda x, y: x[1] == y['publication_id'])
        if publication_map_record != None:
            paper['publication_id'] = publication_map_record[0]
        else:
            logging.warning('paper with no publication id in publication table paper id {}'.format(paper['id']))

    papers = list(map(
        lambda x: (
            x['id'],
            x['title'],
            x['abs'],
            x['publication_id'],
            x['publication_date'],
            x['link'],
            x['doi'],
            x['citation'],
        ),
        papers
    ))

    my_insert_many(connection_merge, 'insert ignore into paper(id, title, abs, publication_id, publication_date, link, doi, citation) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)', papers)
    my_insert_many(connection_merge, 'insert ignore into paper_mapping(id_main, id, src, merged) values(%s, %s, %s, %s)', paper_mapping)
    return paper_mapping

paper_mapping = merge_paper()

print('haha')