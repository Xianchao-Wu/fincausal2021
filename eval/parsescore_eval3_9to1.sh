#########################################################################
# File Name: parsescore_eval2.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Mon Sep 13 08:57:35 2021
#########################################################################
#!/bin/bash

# step 1: create to keep list:

tmplog="tmp.eval3.9to1.log"

python parsescore_eval3_9to1.py | grep "full2" | sort -k2 -rn | head -n 3 > $tmplog 
python parsescore_eval3_9to1.py | grep "full2" | sort -k5 -rn | head -n 3 >> $tmplog 
python parsescore_eval3_9to1.py | grep "full-eva" | sort -k2 -rn | head -n 3 >> $tmplog 
python parsescore_eval3_9to1.py | grep "full-eva" | sort -k5 -rn | head -n 3 >> $tmplog 

cat $tmplog | awk 'BEGIN{FS=" "}{print $1}' | sort -u > $tmplog.2keep


