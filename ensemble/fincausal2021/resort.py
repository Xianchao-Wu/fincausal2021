
# resort ref
ref="fnp2020-train-full-eva.csv"

out="9951-albert-out/predictions.csv"

def readfn(afile):
    outlist = list()
    outdict = dict()
    with open(afile) as br:
        for aline in br.readlines():
            aline = aline.strip()
            outlist.append(aline)

            cols = aline.split(';')
            aid = cols[0]
            outdict[aid] = aline

    return outlist, outdict

reflist, refdict = readfn(ref)
outlist, outdict = readfn(out)

ref2 = ref.replace('.csv', '2.csv')
with open(ref2, 'w') as bw:
    for aoutline in outlist:
        aid = aoutline.split(';')[0]

        arefline = refdict[aid]
        bw.write(arefline+'\n')

print('done')
            


