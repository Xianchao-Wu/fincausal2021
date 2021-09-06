#########################################################################
# File Name: test1.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Tue Aug 31 08:43:08 2021
#########################################################################
#!/bin/bash

#cptpath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/elgeish/cs224n-squad2.0-albert-xxlarge-v1_model_run_full_True/checkpoint-4578"
apath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/elgeish/cs224n-squad2.0-albert-xxlarge-v1_model_run_full_True/"

# predictions_albert_squad2_cpt4578_full
#for aid in 8359 9354 8757 
#for aid in 9553 9752
for aid in 7762
do
	echo $aid
	cptpath="$apath/checkpoint-$aid"
	submit="$apath/submit"
	mkdir -p $submit
	curpath="$submit/$aid"
	mkdir -p $curpath

	python -m ipdb main.py --test --gpu 3 --model AlbertxxlargeSquad2 --full --cpt $cptpath
	#pred=$cptpath/predictions.csv
	#cp $pred $curpath
	#cp $curpath/predictions.csv $curpath/task2.csv
done
