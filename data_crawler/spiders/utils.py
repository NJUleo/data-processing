def get_keywords(paper):
    if 'keywords' not in paper:
        return None
    kwd = None
    for obj in paper['keywords']:
        if obj['type'] == 'INSPEC: Controlled Indexing':
            kwd = obj['kwd']
    # res = []
    # for kds in paper['keywords']:
    #     if 'kwd' in kds and 'type' in kds and 'Author Keywords' not in kds['type']:
    #         res += kds['kwd']
    
    # if not res:
    #     return None
    
    # tmp = []
    # for kwd in res:
    #     if len(kwd) > 15 and ',' in kwd:
    #         tmp += [x for x in kwd.split(',')]
    #     else:
    #         tmp.append(kwd)
    return kwd

# 通过文件保存一些内容，仅用于测试 TODO: 之后需要改成正式的方式保存
def save_byte_file(content, name = 'test_byte'):
    filename = 'test_files/' + name + '.html'
    with open(filename, 'wb') as f:
        f.write(content)

def save_str_file(content, name = 'test_str'):
    filename = 'test_files/' + name + '.html'
    with open(filename, 'w') as f:
        f.write(content)