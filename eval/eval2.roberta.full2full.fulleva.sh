#########################################################################
# File Name: test1.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Tue Aug 31 08:43:08 2021
#########################################################################
#!/bin/bash

apath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/roberta-large_model_run_full2full_True/"

for adir in `ls $apath`
do
	if [[ $adir =~ "checkpoint" ]]
	then
		echo $adir
		cptpath="$apath/$adir"

		python main.py --eval --gpu 1 --model RoBERTaLarge --full --cpt $cptpath --evaset "fnp2020-train-full2.csv"
	fi
done
