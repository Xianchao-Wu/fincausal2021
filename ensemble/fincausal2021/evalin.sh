#########################################################################
# File Name: eval.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Wed Sep  1 01:59:47 2021
#########################################################################
#!/bin/bash

# ref.csv and then test.out.csv
if [[ $# -lt 2 ]]
then
	echo "Usage: $0 <ref.fn> <tstout.fn>"
	exit 1
fi

reffn=$1
outfn=$2

python task2_evaluate.py from-file --ref_file $reffn $outfn

