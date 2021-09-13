import json
import demjson


log1="eval2.roberta.9to1.sh.log"
# {'F1score
# /workspace/...

log2="eval2.roberta.9to1.fulleva.sh.log"
#FINALOUTPUT

def loadfn1(log1):
    adict = dict() # checkpoint : [f1, p, r, em]
    curscores = None 
    with open(log1) as br:
        for aline in br.readlines():
            aline = aline.strip()
            if aline.startswith('{\'F1score:'):
                #print(aline)
                alinedict = demjson.decode(aline)
                for akey in alinedict:
                    avalue = alinedict[akey]
                    #print('|||{}|||{}|||'.format(akey, avalue))
                curscores = [alinedict['F1score:'], alinedict['Precision: '], alinedict['Recall: '], alinedict['exact match: ']]
                curscores = ' '.join([str(a) for a in curscores])
            elif aline.startswith('/workspace/'):
                cpt = aline.split('/')[-1]
                #print(cpt)
                adict[cpt] = curscores
        return adict

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


adict = loadfn1(log1)
bdict = loadfn2(log2)

for akey in adict:
    avalue = adict[akey]
    bvalue = bdict[akey] if akey in bdict else '0.0 0.0 0.0 0.0'
    print('{} {} {}'.format(akey, avalue, bvalue))


