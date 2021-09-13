import json
import demjson


log2="eval2.roberta.full2full.fulleva.sh.log"
#FINALOUTPUT

def loadfn2(log2):
    bdict = dict()
    with open(log2) as br:
        for aline in br.readlines():
            aline = aline.strip()
            if aline.startswith('FINALOUTPUT'):
                aline = aline.replace(',', '').replace('}', '').replace('\t', ' ')
                cols = aline.split(' ')
                #for i in range(len(cols)):
                #    print('i={} cols.i={}'.format(i, cols[i]))
                avalue = ' '.join([cols[1], cols[4], cols[7], cols[11]])
                bdict[cols[12]] = avalue
        return bdict


adict = loadfn2(log2)

for akey in adict:
    avalue = adict[akey]
    print('{} {}'.format(akey, avalue))


