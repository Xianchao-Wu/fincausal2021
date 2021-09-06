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

def getExactMatchScore(scorefn):
    em = 0.0
    p = 0.0
    r = 0.0
    f1 = 0.0

    prf1 = ''
    with open(scorefn) as br:
        for aline in br.readlines():
            aline = aline.strip()
            if aline.startswith('ExactMatch:'):
                em = float(aline.split(' ')[1])
            elif aline.startswith('F1:'):
                f1 = float(aline.split(' ')[1])
            elif aline.startswith('Recall:'):
                r = float(aline.split(' ')[1])
            elif aline.startswith('Precision:'):
                p = float(aline.split(' ')[1])
    prf1 = 'p{}_r{}_fone{}'.format(p, r, f1) 
    return em, prf1 

def get_score1(cof, refidlist, args):
    all_scores = collections.OrderedDict()

    idx = 0
    all_nbest = collections.OrderedDict()

    for input_file in args.input_nbest_files.split(","): # e.g., 3 n-best files
        with open(input_file, "r") as reader:
            input_data = json.load(reader, strict=False)
            #maxcount = 2
            acount = 0
            for (key, entries) in input_data.items(): # key=question.id
                if key not in all_nbest:
                    all_nbest[key] = collections.defaultdict(float)

                for entry in entries:
                    # one entry = top-n中的一个具体结果
                    threeseq = '{};{};{}'.format(entry['text'], entry['cause_text'], entry['effect_text'])
                    all_nbest[key][threeseq] += cof[idx] * entry["probability"] # 每个问题id下面，每个答案的更新之后的得分
                
                #print(key)
                #print(all_nbest[key])
                acount += 1
                #if acount >= maxcount:
                #    break

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
    tmpoutfn = './tmp.5.time4/tstout_{}.csv'.format(aidxstr)
    saveoutfn(output_predictions, refidlist, tmpoutfn)

    # 1.predict_file=ref file, 参考答案,文件！dev-v2.0.json
    # 2.output_predictions = 结果的dictionary，是词典；不是文件
    # 3.output_scores = dictionary，得分，是词典
    # 4.null answer的阈值
    #eval_score = eval_squad2(args.predict_file, output_predictions, output_scores,
    #                        args.null_score_diff_threshold)
    #return eval_score["best_f1"]
    tmpscorefn = './tmp.5.time4/score_{}.txt'.format(aidxstr)
    acmd = "python task2_evaluate.py from-file --ref_file {} {} > {} 2>&1".format(args.predict_file, tmpoutfn, tmpscorefn)
    out = os.system(acmd)

    # origin_control.csv -> "origin_control.{}.csv".format(aidxstr)
    tmporigfn = './tmp.5.time4/origin_control.csv'
    tmporigfn2 = './tmp.5.time4/origin_control_{}.csv'.format(aidxstr)
    shutil.move(tmporigfn, tmporigfn2)

    emscore, prf1 = getExactMatchScore(tmpscorefn)

    return emscore, prf1

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
    #import ipdb; ipdb.set_trace()
    parser = argparse.ArgumentParser()

    # Required parameters
    # parser.add_argument('--input_null_files', type=str, default=
    # "ensemble/model1/null_odds.json,cls_score.json,ensemble/model2/null_odds.json,ensemble/model3/null_odds.json,ensemble/model6/null_odds.json,ensemble/model8/null_odds.json"
    #                     )
    #
    # parser.add_argument('--input_nbest_files', type=str, default="ensemble/model1/nbest_predictions.json,ensemble/model2/nbest_predictions.json,ensemble/model3/nbest_predictions.json,ensemble/model6/nbest_predictions.json,ensemble/model8/nbest_predictions.json"
    #                     )
    #parser.add_argument('--input_null_files', type=str, default="checkpoint-120/null_odds_checkpoint-120.json,checkpoint-1080/null_odds_checkpoint-1080.json"
    #                    )

    parser.add_argument('--input_nbest_files', type=str, 
            default="1-7762-albert-out/nbest_predictions.json,1-9752-albert-out/nbest_predictions.json,1-9354-albert-out/nbest_predictions.json,1-2190-albert-out/nbest_predictions.json,1-5772-albert-out/nbest_predictions.json"
            )

    parser.add_argument("--predict_file", default="fnp2020-train-full2.csv")

    args = parser.parse_args()

    refidlist = readrefids(args.predict_file)

    from itertools import product
   
    fin_cof = None
    best_score = 0.0
    plist = product(range(11), range(11), range(11), range(11), range(11))
    for abc in plist:
        if sum(abc) != 10:
            continue

        #import ipdb; ipdb.set_trace()
        abc2 = [float(i)/10.0 for i in abc]
        print(abc2)
        score, cur_prf1 = get_score1(abc2, refidlist, args)
        if score > best_score:
            best_score = score
            fin_cof = abc2
        print('cur_EM_score={}, cur_cof={}, cur_prf1={}, best_EM_score={}, best_cof={}'.format(score, abc2, cur_prf1, best_score, fin_cof))
        #break

    print('done')
    print('best_score={}, best_cof={}'.format(best_score, fin_cof))

if __name__ == "__main__":
    main()
