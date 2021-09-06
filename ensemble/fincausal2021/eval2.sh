#########################################################################
# File Name: eval2.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Wed Sep  1 03:02:29 2021
#########################################################################
#!/bin/bash
python task2_evaluate.py from-file --ref_file fnp2020-train-full-eva2.csv ./9951-albert-out/predictions.csv
