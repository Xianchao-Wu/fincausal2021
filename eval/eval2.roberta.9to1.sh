#########################################################################
# File Name: test1.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Tue Aug 31 08:43:08 2021
#########################################################################
#!/bin/bash

apath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/roberta-large_model_run_9to1_full_True/"

for adir in `ls $apath`
do
	if [[ $adir =~ "checkpoint" ]]
	then
		echo $adir
		cptpath="$apath/$adir"
		#submit="$apath/submit"
		#mkdir -p $submit
		#curpath="$submit/$aid"
		#mkdir -p $curpath

		#python main.py --test --gpu 3 --model AlbertxxlargeSquad2 --full --cpt $cptpath
		python main.py --eval --gpu 0 --model RoBERTaLarge --full --cpt $cptpath --evaset "fnp2020-train-full-eva.csv"
		#pred=$cptpath/predictions.csv
		#cp $pred $curpath
		#cp $curpath/predictions.csv $curpath/task2.csv
	fi
done
