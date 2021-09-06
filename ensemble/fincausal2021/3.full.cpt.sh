#########################################################################
# File Name: 3.full.cpt.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Wed Sep  1 05:40:59 2021
#########################################################################
#!/bin/bash
bash evalin.sh ./fnp2020-train-full2.csv ./1-7762-albert-out/predictions.csv
bash evalin.sh ./fnp2020-train-full2.csv ./2-31642-roberta-out/predictions.csv
bash evalin.sh ./fnp2020-train-full2.csv ./3-30647-bert-out/predictions.csv

