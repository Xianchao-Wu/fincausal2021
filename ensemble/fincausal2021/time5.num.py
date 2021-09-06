from itertools import product

num=0
plist = product(range(11), range(11), range(11), range(11), range(11))
for abc in plist:
    if sum(abc) != 10:
        continue
    num+=1
print(num)

