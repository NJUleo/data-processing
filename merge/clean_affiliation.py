# %%
import configparser
import pymysql
import logging
import sys
import os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), ".."))
from merge.db_helper import db_helper
from merge.utils import hash_str
from merge.utils import get_clean_name_by_name
# %%
config = configparser.ConfigParser()
config.read('/home/leo/Desktop/ASE/data-processing/merge/local.ini')
db = db_helper(config['merge Database'])

# %%
def change_affiliation(db: db_helper):
    affiliations = db.my_select('select * from affiliation')
    researcher_affiliation = db.my_select('select * from researcher_affiliation')
    affiliations_mapping = []
    num_aff = len(affiliations)
    num_now = 0
    def get_aff_num_by_id(affs, aid):
        num = 0
        for i in affs:
            if i['id'] == aid:
                num += 1
        return num
    def set_aff_by_aid(affs, aid, new_aid, new_name):
        for aff in affs:
            if aff['id'] == aid:
                aff['id'] = new_aid
                aff['name'] = new_name
    def set_ra_aid(ra, aid, new_aid):
        for i in ra:
            if i['aid'] == aid:
                i['aid'] = new_aid
    for aff in affiliations:
        num_now += 1
        if(num_now % 100 == 0):
            logging.warning('cleaning affiliations, {}/{}'.format(num_now, num_aff))

        new_name = get_clean_name_by_name(aff['name'])
        if new_name == None:
            new_name = aff['name']
        new_id = hash_str(new_name)
        affiliations_mapping.append({
            'id': new_id,
            'name': new_name,
            'src_id': aff['id'],
            'src_name': aff['name'],
        })
        if new_name == aff['name']:
            continue
        main_record_num = get_aff_num_by_id(affiliations, new_id)
        if main_record_num == 0:
            set_ra_aid(researcher_affiliation, aff['id'], new_id)
            set_aff_by_aid(affiliations, aff['id'], new_id, new_name)
        elif main_record_num == 1:
            affiliations = list(filter(lambda x, aid = aff['id']: x['id'] != aid, affiliations))
            researcher_affiliation = list(filter(lambda x, aid = aff['id']: x['aid'] != aid, researcher_affiliation))
        else:
            logging.warning('duplite id in affiliation, id: "{}"'.format(new_id))


    affiliations_mapping_tuple = list(map(
        lambda x: (
            x['id'],
            x['name'],
            x['src_id'],
            x['src_name']
        ),
        affiliations_mapping
    ))
    aff_tuple = list(map(
        lambda x: (
            x['id'],
            x['name'],
            x['description']
        ),
        affiliations
    ))
    ra_tuple = list(map(
        lambda x: (
            x['rid'],
            x['aid'],
            x['year']
        ),
        researcher_affiliation
    ))

    db.my_delete_update('delete from affiliation')
    db.my_delete_update('delete from researcher_affiliation')
    db.my_insert_many('insert ignore into affiliation(id, name, description) values(%s, %s, %s)', aff_tuple)
    db.my_insert_many('insert ignore into researcher_affiliation(`rid`, `aid`, `year`) values(%s, %s, %s)', ra_tuple)

    db.my_insert_many(
        'INSERT IGNORE INTO affiliation_mapping(`id`, `name`, `src_id`, `src_name`) VALUES (%s, %s, %s, %s)',
        affiliations_mapping_tuple)
        
    print('haha')

# %%
# change_affiliation(db)

# %%
def change_domain(db: db_helper):
    domains = db.my_select('select * from domain')
    paper_domains = db.my_select('select * from paper_domain')
    result_domains = []
    def get_domain_by_name(domains, name):
        """
        从 domains 中获取名字为 name 的domain。不存在则返回 None
        """
        for domain in domains:
            if domain['name'] == name:
                return domain
        return None
    def change_paper_domain_by_name(paper_domains, new_name, name):
        new_id = hash_str(new_name)
        old_id = hash_str(name)
        for pd in paper_domains:
            if pd['did'] == old_id:
                pd['did'] = new_id
    for domain in domains:
        new_name = domain['name'].lower()
        if new_name == domain['name']:
            # 全部是小写，没有变化
            result_domains.append(domain)
        else:
            # 含有大写，使用小写代替
            # 判断是否有这个小写的 domain
            main_domain = get_domain_by_name(domains, new_name) # 作为这个 domain 的主记录
            if main_domain == None:
                # 修改当前 domain 并插入
                result_domains.append({
                    'id': hash_str(new_name),
                    'name': new_name,
                    'url': None
                })
            else:
                # 删掉当前 domain （result中不含它）
                pass
            # 修改关系表
            change_paper_domain_by_name(paper_domains, new_name, domain['name'])
    domain_tuple = list(map(
        lambda x: (
            x['id'],
            x['name'],
            x['url']
        ),
        result_domains
    ))
    paper_domain_tuple = list(map(
        lambda x: (
            x['pid'],
            x['did']
        ),
        paper_domains
    ))
    db.my_delete_update('delete from domain')
    db.my_delete_update('delete from paper_domain')
    db.my_insert_many('insert ignore into domain(`id`, `name`, `url`) values(%s, %s, %s)', domain_tuple)
    db.my_insert_many('insert ignore into paper_domain(`pid`, `did`) values(%s, %s)', paper_domain_tuple)
    print('haha')

# %%
change_domain(db)
# %%
