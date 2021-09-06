#########################################################################
# File Name: test1.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Tue Aug 31 08:43:08 2021
#########################################################################
#!/bin/bash

#cptpath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/elgeish/cs224n-squad2.0-albert-xxlarge-v1_model_run_full_True/checkpoint-4578"
#cptpath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/roberta-large_model_run_full_True/checkpoint-7563"

apath="/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/deepset/bert-large-uncased-whole-word-masking-squad2_model_run_full_True/"

for aid in 30647 # 3583 27861 #30846 2986 4180
do
	echo $aid
	cptpath="$apath/checkpoint-$aid"
	submit="$apath/submit"
	mkdir -p $submit
	curpath="$submit/$aid"
	mkdir -p $curpath

	python -m ipdb main.py --test --gpu 3 --model BertSquad2 --full --cpt $cptpath
	pred=$cptpath/predictions.csv
	cp $pred $curpath
	cp $curpath/predictions.csv $curpath/task2.csv

	nbest=$cptpath/nbest_predictions.json
    cp $nbest $curpath
done
