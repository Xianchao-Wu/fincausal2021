#########################################################################
# File Name: parsescore_eval2.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Mon Sep 13 08:57:35 2021
#########################################################################
#!/bin/bash

tmplog="tmp.eval2.log"

python parsescore_eval2.py | sort -k2 -rn | head -n 3 > $tmplog 
python parsescore_eval2.py | sort -k5 -rn | head -n 3 >> $tmplog 
python parsescore_eval2.py | sort -k6 -rn | head -n 3 >> $tmplog 
python parsescore_eval2.py | sort -k9 -rn | head -n 3 >> $tmplog 

cat $tmplog | awk 'BEGIN{FS=" "}{print $1}' | sort -u > $tmplog.2rm


