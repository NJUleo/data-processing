import hashlib
def hash_str(s):
    hl = hashlib.md5() # 如果是同一个 md5 对象然后多次 update 则得到的结果不同
    hl.update(s.encode())
    return hl.hexdigest()