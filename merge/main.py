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


def get_same_from_it(src, target, is_equal = lambda x, y: x == y):
    """
    从可迭代对象中找出某个元素（自定义相等），没有则返回None
    """
    for i in src:
        if is_equal(i, target):
            return i
    return None

def change_merge_map(from_list, to_list, mapping_list, change = lambda x: x, is_equal = lambda x, y: x == y):
    """
    将一个list所有的元素做变化（change），加入另一之中（merge），重复的不加入（通过函数定义），每次记录对应（mapping）
    """
    for item in from_list:
        main_record = get_same_from_it(to_list, item, is_equal)
        if main_record != None:
            # 已有记录
            mapping_list.append((
                main_record['id'],
                item['id']
            ))
        else:
            new_main_record = item.copy()
            new_main_record = change(new_main_record)
            to_list.append(new_main_record)
            mapping_list.append((
                new_main_record['id'],
                item['id']
            ))


def merge_publication():
    # merge publication by name and publication time
    publications_ieee = my_select(connection_ieee, 'select * from publication')
    publications_acm = my_select(connection_acm, 'select * from publication')
    publications = []
    publication_merge = []

    def change_pub_ieee_id(pub):
        pub['id'] = hash_str('ieee' + pub['id'])
        return pub

    def change_pub_acm_id(pub):
        pub['id'] = hash_str('acm' + pub['id'])
        return pub
    change_merge_map(publications_ieee, publications, publication_merge, change_pub_ieee_id, lambda x, y: x['name'] == y['name'] and x['publication_date'] == y['publication_date'])

    change_merge_map(publications_acm, publications, publication_merge, change_pub_acm_id, lambda x, y: x['name'] == y['name'] and x['publication_date'] == y['publication_date'])

    # 按照下面 sql 对应顺序把字典改为元组
    publications = list(map(
        lambda x: (x['id'], x['name'], x['publication_date'], str(random.uniform(0, 1))),
        publications
    ))
    my_insert_many(connection_merge, 'insert ignore into publication_mapping values(%s, %s)', publication_merge)
    my_insert_many(connection_merge, 'insert ignore into publication(`id`, `name`, `publication_date`, `impact`) VALUES(%s, %s, %s, %s)', publications)

merge_publication()

# paper
# TODO: 也许全加载到内存不是一个好主意。以后再重构。
paper_mapping = []
paper_ieee = my_select(connection_ieee, 'select * from paper')
for p in paper_ieee:
    paper_mapping.append((hash_str(p['id']), p['id']))

print('haha')