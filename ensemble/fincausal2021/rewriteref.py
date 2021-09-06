
reffn='./fnp2020-train-full.csv'
tstfn='./1-7762-albert-out/predictions.csv'

def readfn(afile):
    fndict = dict()
    with open(afile) as br:
        for aline in br.readlines():
            aline = aline.strip()
            cols = aline.split(';')
            # id, txt, ...
            atxt = cols[1].strip()
            aid = cols[0].strip()
            akey = atxt + "\t" + aid
            fndict[akey] = aline
    return fndict

refdict = readfn(reffn)
print('{} lines loaded from reffn'.format(len(refdict)))

outreffn=reffn.replace('.csv', '2.csv')

count = 0
with open(outreffn, 'w') as bw:
    with open(tstfn) as br:
        for aline in br.readlines():
            aline = aline.strip()
            cols = aline.split(';')

            # id, txt, ...
            atxt = cols[1].strip()
            aid = cols[0].strip()
            akey = atxt + '\t' + aid
            if akey in refdict:
                refline = refdict[akey]
                bw.write(refline+'\n')
                count += 1

print('done, {} lines'.format(count))
