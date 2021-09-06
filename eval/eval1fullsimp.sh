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
#for aid in 4578 8359 9354 8757 
for adir in `ls $apath`
do
	#echo $aid
	#echo "adir="$adir
	if [[ $adir =~ "checkpoint" ]]
	then
		echo $adir
		cptpath="$apath/$adir"
		#submit="$apath/submit"
		#mkdir -p $submit
		#curpath="$submit/$aid"
		#mkdir -p $curpath

		outfn=$cptpath/predictions.csv

		
		#python main.py --eval --gpu 4 --model AlbertxxlargeSquad2 --full --cpt $cptpath --evaset 
		eva="./data/fnp2020-train-full2.csv"
		python task2_evaluate.py from-file --ref_file $eva $outfn

		#pred=$cptpath/predictions.csv
		#cp $pred $curpath
		#cp $curpath/predictions.csv $curpath/task2.csv
	fi
done
