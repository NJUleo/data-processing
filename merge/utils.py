import hashlib


def hash_str(s):
    hl = hashlib.md5()  # 如果是同一个 md5 对象然后多次 update 则得到的结果不同
    hl.update(s.encode())
    return hl.hexdigest()


def encode_id(it, prefix):
    for record in it:
        if record.get('id') == None:
            continue
        record['id'] = hash_str(prefix + record['id'])
    return it


def solve_affiliation_name(s):
    """ change affiliation name
    s:要处理的机构名

    Returns:
        处理后的机构名
    """
    l = ['Univ', 'Unniversity', "College", "Montreal", "Polytechnique Montréal", "Research Center",
         "Lab", "Institute", "Business Group", "Microsoft", "Oxford", "Cambrihge", "Cambridge", "ETH"]
    ig = {'Reliability and Trust, Centre For Security, Luxembourg, LUXEMBOURG': 'Reliability and Trust, Centre For Security', 'SAP HANA Cloud Computing, Systems Engineering, Belfast, United Kingdom': 'SAP HANA Cloud Computing, Systems Engineering',
          'BMW Group Research, New Technologies, Innovations, Garching b. München, Germany': 'BMW Group Research, New Technologies, Innovations', 'Department of ECE, Virginia Tech, Blacksburg, VA, USA': 'Department of ECE, Virginia Tech', 'DEEDS Group, TU Darmstadt, Darmstadt, Germany': 'DEEDS Group, TU Darmstadt'}
    if s in ig.keys():
        return ig[s]
    s = s.replace('，', ",")
    strs = s.split(',')
    if len(strs) == 1:
        return s
    index = -1
    for cur in range(0, len(strs)):
        for i in l:
            if i in strs[cur] or len(strs[cur]) > 25:
                index = cur
    if index == -1:
        print(s)
        return strs[0]
    res = strs[0]
    for i in range(0, index):
        res = res + ',' + strs[i]
    return res
