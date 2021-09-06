# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Run BERT on SQuAD."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import collections
import json
import os
import shutil

#from evaluate_official2_fast import eval_squad
###from evaluate_official2 import eval_squad2

def saveoutfn(preds, refidlist, tmpoutfn):
    with open(tmpoutfn, 'w') as bw:
        bw.write('Index;Text;Cause;Effect\n')

        for aid in refidlist:
            atxt = preds[aid] # txt;cause;effect
            outline = '{};{}\n'.format(aid, atxt)
            bw.write(outline)

    print('file {} saved'.format(tmpoutfn))

#gencombtstout(abc2, refidlist, args)
def gencombtstout(cof, refidlist, args):
    all_scores = collections.OrderedDict()

    idx = 0
    all_nbest = collections.OrderedDict()

    for input_file in args.input_nbest_files.split(","): # e.g., 3 n-best files
        with open(input_file, "r") as reader:
            input_data = json.load(reader, strict=False)
            for (key, entries) in input_data.items(): # key=question.id
                if key not in all_nbest:
                    all_nbest[key] = collections.defaultdict(float)

                for entry in entries:
                    # one entry = top-n中的一个具体结果
                    threeseq = '{};{};{}'.format(entry['text'], entry['cause_text'], entry['effect_text'])
                    all_nbest[key][threeseq] += cof[idx] * entry["probability"] # 每个问题id下面，每个答案的更新之后的得分
        idx += 1

    output_predictions = {}
    for (key, entry_map) in all_nbest.items():
        sorted_texts = sorted(entry_map.keys(), key=lambda x: entry_map[x], reverse=True)
        # TODO important!
        suffix_index = 0
        if key.count('.') == 2:
            suffix_index = int(key.split('.')[-1]) 
        if suffix_index > 0:
            suffix_index -= 1
    
        best_text = sorted_texts[suffix_index]
        output_predictions[key] = best_text # 得到当前问题id的最优得分
        #print(key, best_text, all_nbest[key][best_text])

    # store output_predictions to a tstout.csv file
    aidxstr = '_'.join([str(x) for x in cof ])
    tmpoutfn = './tmp.5.time2.2test/tstout_{}.csv'.format(aidxstr)
    saveoutfn(output_predictions, refidlist, tmpoutfn)

    #return emscore, prf1

def readrefids(reffn):
    outlist = list()
    with open(reffn) as br:
        for aline in br.readlines():
            if aline.startswith('Index'):
                continue
            aid = aline.split(';')[0]
            outlist.append(aid)
    return outlist

def main():
    parser = argparse.ArgumentParser()

    # NOTE
    parser.add_argument('--input_nbest_files', type=str, 
            default="1-7762-albert-out/nbest_predictions.json,2-31642-roberta-out/nbest_predictions.json,3-30647-bert-out/nbest_predictions.json,1-9752-albert-out/nbest_predictions.json,2-6369-roberta-out/nbest_predictions.json"
            #default="submit.1.albert.ensemble/7762/nbest_predictions.json,submit.2.roberta.ensemble/31642/nbest_predictions.json,submit.3.bertlarge.ensemble/30647/nbest_predictions.json,submit.1.albert.ensemble/9752/nbest_predictions.json,submit.2.roberta.ensemble/6369/nbest_predictions.json"
            )
    
    # NOTE change:
    parser.add_argument("--predict_file", default="fnp2020-train-full2.csv")
    #parser.add_argument("--predict_file", default="task2.csv")

    args = parser.parse_args()

    refidlist = readrefids(args.predict_file)

    # NOTE
    #abc2 = [0.4, 0.2, 0.3, 0.0, 0.1] -> comb.1's best weights 
    abc2 = [0.0, 0.8, 0.1, 0.1, 0.0] 
    print(abc2)

    gencombtstout(abc2, refidlist, args)

    print('done')

if __name__ == "__main__":
    main()
