# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
# Copyright 2020 Guillaume Becquin. All rights reserved.
# MODIFIED FOR CAUSE EFFECT EXTRACTION
#
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


import json
import logging
import os
import sys
from pathlib import Path
import torch
from src.config import RunConfig, ModelConfigurations, model_tokenizer_mapping
from src.evaluation import evaluate, predict
from src.logging import initialize_log_dict
from src.preprocessing import load_examples
from src.training import train
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train",
        default=False,
        required=False,
        action="store_true",
        help="Flag to specify if the model should be trained",
    )

    parser.add_argument(
        "--eval",
        default=False,
        required=False,
        action="store_true",
        help="Flag to specify if the model should be evaluated",
    )

    parser.add_argument(
        "--evaset",
        default="",
        required=False,
        help="evaluation set, only name is fine and should be in ./data/"
    )

    parser.add_argument(
        "--test",
        default=False,
        required=False,
        action="store_true",
        help="Flag to specify if the model should generate predictions on the train file",
    )
    parser.add_argument(
        "--model",
        default="AlbertSquad",
        required=False,
        help="name of pretrained model, such as AlbertSquad, AlbertxxlargeSquad2",
    )
    parser.add_argument(
        "--gpu",
        default=0,
        required=False,
        help="gpu index to be used"
    )
    parser.add_argument(
        "--full",
        default=False,
        required=False,
        action="store_true",
        help="is use all the data for training, default=False"
    )
    parser.add_argument(
        "--cpt",
        default="",
        required=False,
        help="checkpoint path of the fine-tuned model for testing or continue fine-tuning",
    )
    args = parser.parse_args()
    assert args.train or args.eval or args.test, \
        "At least one task needs to be selected by passing --train, --eval or --test"

    device = torch.device("cuda:{}".format(args.gpu) if torch.cuda.is_available() else "cpu")

    #model_config = ModelConfigurations.RoBERTaSquadLarge
    model_config = ModelConfigurations.AlbertSquad
    if args.model == 'AlbertxxlargeSquad2':
        model_config = ModelConfigurations.AlbertxxlargeSquad2
    elif args.model == 'RoBERTaSquadLarge':
        model_config = ModelConfigurations.RoBERTaSquadLarge
    elif args.model == 'RoBERTaLarge':
        model_config = ModelConfigurations.RoBERTaLarge
    elif args.model == 'BertSquad2':
        model_config = ModelConfigurations.BertSquad2

    run_config = RunConfig()
    run_config.do_train = args.train
    run_config.do_eval = args.eval
    run_config.do_test = args.test

    RUN_NAME = 'model_run'

    (MODEL_TYPE, MODEL_NAME_OR_PATH, DO_LOWER_CASE) = model_config.value

    fincausal_data_path = Path(os.environ.get('FINCAUSAL_DATA_PATH',
                                              os.path.dirname(os.path.realpath(sys.argv[0])) + '/data'))
    fincausal_output_path = Path(os.environ.get('FINCAUSAL_OUTPUT_PATH',
                                                os.path.dirname(os.path.realpath(sys.argv[0])) + '/output'))

    #TRAIN_FILE = fincausal_data_path / "fnp2020-train.csv"
    #TRAIN_FILE = fincausal_data_path / "fnp2020-train-full-train.csv"
    TRAIN_FILE = fincausal_data_path / "fnp2020-train-full.csv"
    if args.full:
        #TRAIN_FILE = fincausal_data_path / "fnp2020-train-full-train.csv"
        TRAIN_FILE = fincausal_data_path / "fnp2020-train-full.csv"
    #EVAL_FILE = fincausal_data_path / "fnp2020-train-full-eva.csv"
    EVAL_FILE = fincausal_data_path / "fnp2020-train-full.csv"
    TEST_FILE = fincausal_data_path / "task2.csv" # NOTE
    #TEST_FILE = fincausal_data_path / "task2.5lines.csv"

    if RUN_NAME:
        #OUTPUT_DIR = fincausal_output_path / (MODEL_NAME_OR_PATH + '_' + RUN_NAME + '_9to1_full_' + str(args.full))
        OUTPUT_DIR = fincausal_output_path / (MODEL_NAME_OR_PATH + '_' + RUN_NAME + '_full2full_' + str(args.full))
    else:
        OUTPUT_DIR = fincausal_output_path / (MODEL_NAME_OR_PATH + '_full2full_' + str(args.full))

    model_class, tokenizer_class = model_tokenizer_mapping[MODEL_TYPE]
    log_file = initialize_log_dict(model_config=model_config,
                                   run_config=run_config,
                                   model_tokenizer_mapping=model_tokenizer_mapping)

    # Training
    if run_config.do_train:

        tokenizer = tokenizer_class.from_pretrained(MODEL_NAME_OR_PATH,
                                                    do_lower_case=DO_LOWER_CASE,
                                                    cache_dir=OUTPUT_DIR)
        model = model_class.from_pretrained(MODEL_NAME_OR_PATH).to(device)

        train_dataset = load_examples(file_path=TRAIN_FILE,
                                      tokenizer=tokenizer,
                                      output_examples=False,
                                      run_config=run_config)

        train(train_dataset=train_dataset,
              model=model,
              tokenizer=tokenizer,
              model_type=MODEL_TYPE,
              output_dir=OUTPUT_DIR,
              predict_file=EVAL_FILE,
              device=device,
              log_file=log_file,
              run_config=run_config
              )
        if not OUTPUT_DIR.is_dir():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if run_config.save_model:
            model_to_save = model.module if hasattr(model, "module") else model
            model_to_save.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
            logger.info("Saving final model to %s", OUTPUT_DIR)
        logger.info("Saving log file to %s", OUTPUT_DIR)
        with open(os.path.join(OUTPUT_DIR, "logs.json"), 'w') as f:
            json.dump(log_file, f, indent=4)

    if run_config.do_eval:
        OUTPUT_DIR = args.cpt
        OUTPUT_DIR = Path(OUTPUT_DIR)
        print(OUTPUT_DIR) # checkpoint path
        #EVAL_FILE = fincausal_data_path / "fnp2020-train-full-eva.csv" # this is 10%
        EVAL_FILE = fincausal_data_path / "fnp2020-eval.csv" # this is the old 65 samples for run3, run4, and run5
        if args.evaset and len(args.evaset) > 0:
            EVAL_FILE = fincausal_data_path / args.evaset
        print("eval.set={}".format(EVAL_FILE))

        tokenizer = tokenizer_class.from_pretrained(str(OUTPUT_DIR), do_lower_case=DO_LOWER_CASE)
        model = model_class.from_pretrained(str(OUTPUT_DIR)).to(device)

        result = evaluate(model=model,
                          tokenizer=tokenizer,
                          device=device,
                          file_path=EVAL_FILE,
                          model_type=MODEL_TYPE,
                          output_dir=OUTPUT_DIR,
                          run_config=run_config
                          )
        cpt = str(OUTPUT_DIR).split('/')[-1]
        print('FINALOUTPUT={}\t{}\t{}\t{}'.format(result, cpt, args.evaset, OUTPUT_DIR))
        print(OUTPUT_DIR)

        print("done")

    if run_config.do_test:
        #import ipdb; ipdb.set_trace()
        OUTPUT_DIR = args.cpt
        OUTPUT_DIR = Path(OUTPUT_DIR)
        print(OUTPUT_DIR) # checkpoint path
        tokenizer = tokenizer_class.from_pretrained(str(OUTPUT_DIR), do_lower_case=DO_LOWER_CASE)
        model = model_class.from_pretrained(str(OUTPUT_DIR)).to(device)

        result = predict(model=model,
                         tokenizer=tokenizer,
                         device=device,
                         file_path=TEST_FILE,
                         model_type=MODEL_TYPE,
                         output_dir=OUTPUT_DIR,
                         run_config=run_config
                         )

        print("done")
