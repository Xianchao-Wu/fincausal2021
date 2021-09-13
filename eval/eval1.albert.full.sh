#########################################################################
# File Name: test1.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Tue Aug 31 08:43:08 2021
#########################################################################
#!/bin/bash

apath2="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/"
apath=$apath2"/elgeish/cs224n-squad2.0-albert-xxlarge-v1_model_run_full_True"

for adir in `ls $apath`
do
	if [[ $adir =~ "checkpoint" ]] #&& -e $adir/pytorch_model.bin ]]
	then
		echo $adir
		cptpath="$apath/$adir"

		python main.py --eval --gpu 0 --model AlbertxxlargeSquad2 --full --cpt $cptpath --evaset "fnp2020-train-full2.csv"
		#python main.py --eval --gpu 4 --model BertSquad2 --full --cpt $cptpath --evaset "fnp2020-train-full-eva.csv"
	fi
done
