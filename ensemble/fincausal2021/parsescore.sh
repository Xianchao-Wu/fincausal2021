#########################################################################
# File Name: parse.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Wed Sep  1 00:26:09 2021
#########################################################################
#!/bin/bash

if [[ $# -lt 1 ]]
then
	echo "Usage: $0 <in.log.file>"
	exit 1
fi

infn=$1
#cat eval1.sh.log.65eval.allcpts | python parsescore.py | sort -k5 -k2 -rn

cat $infn | python parsescore.py | sort -k5 -k2 -rn
