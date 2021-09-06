
import sys

if len(sys.argv) < 2:
    print("Usage: {} <in.log.fn>".format(sys.argv[0]))
    exit(1)

infn = sys.argv[1]

with open(infn) as br:
    curlist = list()
    idx = 0
    for aline in br.readlines():
        aline = aline.strip()
        if aline.startswith('Iteration Loss:'):
            aloss = float(aline.split(':')[1])
            curlist.append(aloss)
        else:
            if len(curlist) > 0:
                avg = sum(curlist)/len(curlist)
                print('{}, avg={}, len={}'.format(idx, avg, len(curlist)))
                idx += 1
                curlist = list()

