import sys

def procline(aline):
    aline = aline.replace(',', ' ').replace('}', ' ')
    cols = aline.split(' ')
    olist = list()
    for col in cols:
        if col.startswith('0.'):
            olist.append(col)

    return ' '.join(olist)

def procline2(aline):
    cols = aline.split(' ')
    f1 = cols[-1]
    p = cols[2]
    r = cols[5]
    return '{} {} {}'.format(f1, p, r)

resdict = dict()
curkey = ''
for aline in sys.stdin:
    aline = aline.strip()
    if aline.startswith('checkpoint'):
        curkey = aline
        resdict[curkey] = 'NA'
    elif 'F1score' in aline:
        # checkpoint-1195 {'F1score:': 0.8868256037557255, 'Precision: ': 0.8912841875563948, 'Recall: ': 0.8844053398058253, 'exact match: ': 0.8923076923076924}
        outline = procline(aline)
        resdict[curkey] = outline
    elif 'weighted precision' in aline:
        outline = procline2(aline)
        newline = resdict[curkey] + " " + outline if curkey in resdict else outline
        newline = newline.replace('NA', '')
        resdict[curkey] = newline # p, r, f1
    elif 'ExactMatch:' in aline:
        outline = aline.split(' ')[1]
        newline =resdict[curkey] + " " + outline if curkey in resdict else outline
        newline = newline.replace('NA', '')
        resdict[curkey] = newline

for akey in resdict:

    print('{}\t{}'.format(akey, resdict[akey]))




