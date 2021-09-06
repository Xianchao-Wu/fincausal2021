#########################################################################
# File Name: test1.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Tue Aug 31 08:43:08 2021
#########################################################################
#!/bin/bash

#cptpath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/elgeish/cs224n-squad2.0-albert-xxlarge-v1_model_run_full_True/checkpoint-4578"
apath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/roberta-large_model_run_full_True/"
for aid in 31642 #6369 24080 #14130 14528 16518
do
	echo $aid
	cptpath="$apath/checkpoint-$aid"
	submit="$apath/submit"
	mkdir -p $submit
	curpath="$submit/$aid"
	mkdir -p $curpath

	python -m ipdb main.py --test --gpu 4 --model RoBERTaLarge --full --cpt $cptpath
	pred=$cptpath/predictions.csv
	cp $pred $curpath
	cp $curpath/predictions.csv $curpath/task2.csv

	nbest=$cptpath/nbest_predictions.json
	cp $nbest $curpath

done

