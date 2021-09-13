rmfile = 'tmp.eval3.full2full.log.2keep'

def readrmfn(rmfile):
    adict = dict()
    with open(rmfile) as br:
        for aline in br.readlines():
            aline = aline.strip()
            aline = aline.replace('-fnp', ' ').split(' ')[0]
            adict[aline] = ''
        return adict

apath='/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/deepset'
apath=apath+'/bert-large-uncased-whole-word-masking-squad2_model_run_full2full_True'

adict = readrmfn(rmfile)
print(adict)

import os

for afile in os.listdir(apath):
    break
    if afile.startswith('checkpoint-'):
        print(afile, afile in adict)
        if not afile in adict:
            afile2path = os.path.join(apath, afile)
            afile2 = os.path.join(afile2path, 'pytorch_model.bin')
            print(afile2)
            acmd = 'rm {}'.format(afile2)
            print(acmd)
            os.system(acmd)

            acmd2 = 'gzip {}/*.json'.format(afile2path)
            print(acmd2)
            os.system(acmd2)

            acmd2 = 'gzip {}/*.csv'.format(afile2path)
            print(acmd2)
            os.system(acmd2)



