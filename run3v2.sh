#########################################################################
# File Name: run.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Mon Aug 30 13:38:15 2021
#########################################################################
#!/bin/bash

#python -m ipdb main.py --train
# use full set as train and eva!
python main.py --train --gpu 1 --model AlbertxxlargeSquad2 --full
