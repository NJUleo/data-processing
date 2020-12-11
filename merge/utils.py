import hashlib
def hash_str(s):
    hl = hashlib.md5() # 如果是同一个 md5 对象然后多次 update 则得到的结果不同
    hl.update(s.encode())
    return hl.hexdigest()

def encode_id(it, prefix):
    for record in it:
        if record.get('id') == None:
            continue
        record['id'] = hash_str(prefix + record['id'])
    return it