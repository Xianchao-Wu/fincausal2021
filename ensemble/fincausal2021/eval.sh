#########################################################################
# File Name: eval.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Wed Sep  1 01:59:47 2021
#########################################################################
#!/bin/bash

# ref.csv and then test.out.csv

python task2_evaluate.py from-file --ref_file fnp2020-eval.csv ./9951-roberta-out/predictions.csv

