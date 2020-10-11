def get_keywords(paper):
    if 'keywords' not in paper:
        return None
    kwd = None
    for obj in paper['keywords']:
        if obj['type'] == 'INSPEC: Controlled Indexing':
            kwd = obj['kwd']

    return kwd

# 通过文件保存一些内容，仅用于测试 TODO: 之后需要改成正式的方式保存
def save_byte_file(content, name = 'test_byte'):
    filename = 'test_files/' + name
    with open(filename, 'wb') as f:
        f.write(content)

def save_str_file(content, name = 'test_str'):
    filename = 'test_files/' + name
    with open(filename, 'w') as f:
        f.write(content)

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    else:
        raise NoPrefixException(text, prefix)

class NoPrefixException(Exception):
    pass