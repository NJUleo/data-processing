import binascii
def str_2_utf8_hex(s):
    b = s.encode('utf-8') # 以 utf-8 编码为bytes
    h = binascii.hexlify(b) # 转换为16进制编码序列
    return h.decode('utf-8') # 16进制数作为字符串保存( utf-8 编码)

def utf8_hex_2_str(s):
    b = s.encode('utf-8') # 字符串通过 utf-8 编码为 bytes
    resultb = binascii.unhexlify(b) # 16进制转回 bytes
    return resultb.decode('utf-8') # 作为 utf-8 解码