#########################################################################
# File Name: run.sh
# Author: Xianchao Wu
# mail: xianchaow@nvidia.com
# Created Time: Mon Aug 30 13:38:15 2021
#########################################################################
#!/bin/bash

#python -m ipdb main.py --train
#python main.py --train --gpu 3 --model RoBERTaSquadLarge2 --full
python main.py --train --gpu 2 --model BertSquad2 --full
