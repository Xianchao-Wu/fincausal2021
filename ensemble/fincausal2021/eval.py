import sys
import os

acmd = "python task2_evaluate.py from-file --ref_file fnp2020-eval.csv ./9951-roberta-out/predictions.csv > ./9951-roberta-out/score.txt 2>&1"
out=os.system(acmd)
print('='*40)
print(out)
print('='*40)
