#########################################################################
# File Name: parsescore_eval2.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Mon Sep 13 08:57:35 2021
#########################################################################
#!/bin/bash

# step 1: create to keep list:

tmplog="tmp.eval1.full2full.log"

python parsescore_eval1_full2full.py | grep "full2" | sort -k2 -rn | head -n 3 > $tmplog 
python parsescore_eval1_full2full.py | grep "full2" | sort -k5 -rn | head -n 3 >> $tmplog 

cat $tmplog | awk 'BEGIN{FS=" "}{print $1}' | sort -u > $tmplog.2keep


