rmfile = 'tmp.eval2.log.2rm'

def readrmfn(rmfile):
    adict = dict()
    with open(rmfile) as br:
        for aline in br.readlines():
            aline = aline.strip()
            adict[aline] = ''
        return adict

apath = '/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/roberta-large_model_run_9to1_full_True'

adict = readrmfn(rmfile)
import os

for afile in os.listdir(apath):
    if afile.startswith('checkpoint-'):
        print(afile, afile in adict)
        if not afile in adict:
            afile2 = os.path.join(apath, afile)
            afile2 = os.path.join(afile2, 'pytorch_model.bin')
            print(afile2)
            acmd = 'rm {}'.format(afile2)
            print(acmd)
            os.system(acmd)


