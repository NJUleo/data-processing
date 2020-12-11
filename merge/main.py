import configparser
import pymysql
import logging
import random
from functools import reduce
import sys
from utils import hash_str
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

# merge publication by name and publication time
publications_ieee = my_select(connection_ieee, 'select * from publication')
publications_acm = my_select(connection_acm, 'select * from publication')
publications = []
publication_merge = []
def get_same_date_name(publications, pub):
    # TODO:
    for p in publications:
        if p['name'] == pub['name'] and p['publication_date'] == pub['publication_date']:
            return p
    return None

for pub in publications_ieee + publications_acm:
    main_record = get_same_date_name(publications, pub)
    if main_record != None:
        publication_merge.append((
            main_record['id'],
            pub['id']
        ))
    else:
        new_main_record = pub.copy()
        new_main_record['id'] = hash_str(new_main_record['id'])
        publications.append(new_main_record)
publications = list(map(
    lambda x: (x['id'], x['name'], x['publication_date'], str(random.uniform(0, 1))),
    publications
))
my_insert_many(connection_merge, 'insert ignore into publication_merge values(%s, %s)', publication_merge)
my_insert_many(connection_merge, 'insert ignore into publication(`id`, `name`, `publication_date`, `impact`) VALUES(%s, %s, %s, %s)', publications)
print('haha')