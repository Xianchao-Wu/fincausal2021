# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
# Copyright 2020 Guillaume Becquin.
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

import collections
import csv
import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Tuple, Union

import torch
from torch.nn import Module
from torch.utils.data import SequentialSampler, DataLoader
from tqdm import tqdm
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

from .config import RunConfig
from .fincausal_evaluation.task2_evaluate import encode_causal_tokens, Task2Data
from .data import FinCausalResult, FinCausalFeatures, FinCausalExample
from .preprocessing import load_examples
from .fincausal_evaluation.task2_evaluate import evaluate as official_evaluate

logger = logging.getLogger(__name__)


def to_list(tensor: torch.Tensor) -> List:
    return tensor.detach().cpu().tolist()


def predict(model: Module,
            tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
            device: torch.device,
            file_path: Path,
            model_type: str,
            output_dir: Path,
            run_config: RunConfig) -> Tuple[List[FinCausalExample], collections.OrderedDict]:
    dataset, examples, features = load_examples(file_path=file_path,
                                                tokenizer=tokenizer,
                                                output_examples=True,
                                                evaluate=True,
                                                run_config=run_config)

    if not output_dir.is_dir():
        output_dir.mkdir(parents=True, exist_ok=True)

    eval_sampler = SequentialSampler(dataset)
    eval_dataloader = DataLoader(dataset,
                                 sampler=eval_sampler,
                                 batch_size=run_config.eval_batch_size)

    # Start evaluation
    logger.info("***** Running evaluation  *****")
    logger.info("  Num examples = %d", len(dataset))
    logger.info("  Batch size = %d", run_config.eval_batch_size)

    all_results = []
    sequence_added_tokens = tokenizer.max_len - tokenizer.max_len_single_sentence

    for batch in tqdm(eval_dataloader, desc="Evaluating", position=0, leave=True):
        model.eval()
        batch = tuple(t.to(device) for t in batch)

        with torch.no_grad():
            inputs = {
                "input_ids": batch[0],
                "attention_mask": batch[1],
                "token_type_ids": batch[2],
            }

            if model_type in ["xlm", "roberta", "distilbert", "camembert"]:
                del inputs["token_type_ids"]

            example_indices = batch[3] # tensor([0,1,2,3], device='cuda:3')
            outputs = model(**inputs) # NOTE important, forward here! start_cause_logits, end_cause_logits, start_effect_logits, end_effect_logits : 4 tensors! each with a shape of [4, 384]!

        for i, example_index in enumerate(example_indices):
            eval_feature = features[example_index.item()]
            unique_id = int(eval_feature.unique_id)

            output = [to_list(output[i]) for output in outputs]
            start_cause_logits, end_cause_logits, start_effect_logits, end_effect_logits = output
            result = FinCausalResult(unique_id,
                                     start_cause_logits, end_cause_logits,
                                     start_effect_logits, end_effect_logits)

            all_results.append(result)

    # Compute predictions
    #import ipdb; ipdb.set_trace()
    predictions = compute_predictions_logits(
        examples, # FinCausalExample list
        features, # FinCausalFeatures list
        all_results, # FinCausalResult list
        output_dir, # e.g., PosixPath('/workspace/megatron/fincausal2021/Financial-Causality-Extraction/output/elgeish/cs224n-squad2.0-albert-xxlarge-v1_model_run_full_True/checkpoint-7762')
        sequence_added_tokens, # 2
        run_config # src.config.RunConfig object
    )

    return examples, predictions


def evaluate(model: Module,
             tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
             device: torch.device,
             file_path: Path,
             model_type: str,
             output_dir: Path,
             run_config: RunConfig) -> Dict:
    examples, predictions = predict(model=model,
                                    tokenizer=tokenizer,
                                    device=device,
                                    file_path=file_path,
                                    model_type=model_type,
                                    output_dir=output_dir,
                                    run_config=run_config)

    # Compute the F1 and exact scores.
    results, correct, wrong = compute_metrics(examples, predictions)
    allnum = len(predictions)
    correctnum = len(correct)
    wrongnum = len(wrong)

    output_prediction_file_correct = output_dir / "predictions_correct_all{}_correct{}.json".format(allnum, correctnum)
    output_prediction_file_wrong = output_dir / "predictions_wrong_all{}_wrong{}.json".format(allnum, wrongnum)

    with output_prediction_file_correct.open('w') as writer:
        writer.write(json.dumps(correct, indent=4) + "\n")

    with output_prediction_file_wrong.open('w') as writer:
        writer.write(json.dumps(wrong, indent=4) + "\n")

    return results


def get_data_from_list(input_data: List[List[str]]) -> List[Task2Data]:
    """
    :param input_data: list of inputs (example id, text, cause, effect)
    :return: list of Task2Data(index, text, cause, effect, labels)
    """
    result = []
    for example in input_data:
        (index, text, cause, effect) = tuple(example)

        text = text.lstrip()
        cause = cause.lstrip()
        effect = effect.lstrip()

        _, labels = zip(*encode_causal_tokens(text, cause, effect))

        result.append(Task2Data(index, text, cause, effect, labels))

    return result


def compute_metrics(examples: List[FinCausalExample], predictions: collections.OrderedDict) \
        -> Tuple[Dict, List[Dict], List[Dict]]:
    y_true = []
    y_pred = []

    for example in examples:
        y_true.append([example.example_id, example.context_text, example.cause_text, example.effect_text])
        prediction = predictions[example.example_id]
        y_pred.append([example.example_id, example.context_text, prediction['cause_text'], prediction['effect_text']])

    all_correct = list()
    all_wrong = list()
    for y_true_ex, y_pred_ex in zip(y_true, y_pred):
        if (y_true_ex[2] == y_pred_ex[2]) and (y_true_ex[3] == y_pred_ex[3]):
            all_correct.append({'text': y_true_ex[1],
                                'cause_true': y_true_ex[2],
                                'effect_true': y_true_ex[3],
                                'cause_pred': y_pred_ex[2],
                                'effect_pred': y_pred_ex[3]
                                })
        else:
            all_wrong.append({'text': y_true_ex[1],
                              'cause_true': y_true_ex[2],
                              'effect_true': y_true_ex[3],
                              'cause_pred': y_pred_ex[2],
                              'effect_pred': y_pred_ex[3]
                              })
    logging.info('* Loading reference data')
    y_true = get_data_from_list(y_true)
    logging.info('* Loading prediction data')
    y_pred = get_data_from_list(y_pred)
    logging.info(f'Load Data: check data set length = {len(y_true) == len(y_pred)}')
    logging.info(f'Load Data: check data set ref. text = {all([x.text == y.text for x, y in zip(y_true, y_pred)])}')
    assert len(y_true) == len(y_pred)
    assert all([x.text == y.text for x, y in zip(y_true, y_pred)])

    precision, recall, f1, exact_match = official_evaluate(y_true, y_pred, ['-', 'C', 'E'])

    scores = [
        "F1: %f\n" % f1,
        "Recall: %f\n" % recall,
        "Precision: %f\n" % precision,
        "ExactMatch: %f\n" % exact_match
    ]
    for s in scores:
        print(s, end='')

    return {
               'F1score:': f1,
               'Precision: ': precision,
               'Recall: ': recall,
               'exact match: ': exact_match
           }, all_correct, all_wrong


_PrelimPrediction = collections.namedtuple(
    "PrelimPrediction", ["feature_index",
                         "start_index_cause",
                         "end_index_cause",
                         "start_logit_cause",
                         "end_logit_cause",
                         "start_index_effect",
                         "end_index_effect",
                         "start_logit_effect",
                         "end_logit_effect"]
)

_NbestPrediction = collections.namedtuple(
    "NbestPrediction", ["text_cause",
                        "start_index_cause",
                        "end_index_cause",
                        "start_logit_cause",
                        "end_logit_cause",
                        "text_effect",
                        "start_index_effect",
                        "end_index_effect",
                        "start_logit_effect",
                        "end_logit_effect"]
)


def filter_impossible_spans(features,
                            unique_id_to_result: Dict,
                            n_best_size: int,
                            max_answer_length: int,
                            sequence_added_tokens: int,
                            sentence_boundary_heuristic: bool = False,
                            full_sentence_heuristic: bool = False,
                            shared_sentence_heuristic: bool = False,
                            ) -> List[_PrelimPrediction]:
    prelim_predictions = []

    for (feature_index, feature) in enumerate(features):
        result = unique_id_to_result[feature.unique_id]
        assert isinstance(feature, FinCausalFeatures)
        assert isinstance(result, FinCausalResult)
        sentence_offsets = [offset for offset in [feature.sentence_2_offset, feature.sentence_3_offset] if
                            offset is not None]
        start_indexes_cause = _get_best_indexes(result.start_cause_logits, n_best_size)
        end_indexes_cause = _get_best_indexes(result.end_cause_logits, n_best_size)
        start_logits_cause = result.start_cause_logits
        end_logits_cause = result.end_cause_logits
        start_indexes_effect = _get_best_indexes(result.start_effect_logits, n_best_size)
        end_indexes_effect = _get_best_indexes(result.end_effect_logits, n_best_size)
        start_logits_effect = result.start_effect_logits
        end_logits_effect = result.end_effect_logits

        for raw_start_index_cause in start_indexes_cause:
            for raw_end_index_cause in end_indexes_cause:
                cause_pairs = [(raw_start_index_cause, raw_end_index_cause)]
                # Heuristic: a effect of a cause cannot span across multiple sentences
                if len(sentence_offsets) > 0 and sentence_boundary_heuristic:
                    for sentence_offset in sentence_offsets:
                        if raw_start_index_cause < sentence_offset < raw_end_index_cause:
                            cause_pairs = [(raw_start_index_cause, sentence_offset),
                                           (sentence_offset + 1, raw_end_index_cause)]
                for start_index_cause, end_index_cause in cause_pairs:
                    for raw_start_index_effect in start_indexes_effect:
                        for raw_end_index_effect in end_indexes_effect:
                            effect_pairs = [(raw_start_index_effect, raw_end_index_effect)]
                            # Heuristic: a effect of a cause cannot span across multiple sentences
                            if len(sentence_offsets) > 0 and sentence_boundary_heuristic:
                                for sentence_offset in sentence_offsets:
                                    if raw_start_index_effect < sentence_offset < raw_end_index_effect:
                                        effect_pairs = [(raw_start_index_effect, sentence_offset),
                                                        (sentence_offset + 1, raw_end_index_effect)]
                            for start_index_effect, end_index_effect in effect_pairs:
                                if (start_index_cause <= start_index_effect) and (
                                        end_index_cause >= start_index_effect):
                                    continue
                                if (start_index_effect <= start_index_cause) and (
                                        end_index_effect >= start_index_cause):
                                    continue
                                if start_index_effect >= len(feature.tokens) or start_index_cause >= len(
                                        feature.tokens):
                                    continue
                                if end_index_effect >= len(feature.tokens) or end_index_cause >= len(feature.tokens):
                                    continue
                                if start_index_effect not in feature.token_to_orig_map or \
                                        start_index_cause not in feature.token_to_orig_map:
                                    continue
                                if end_index_effect not in feature.token_to_orig_map or \
                                        end_index_cause not in feature.token_to_orig_map:
                                    continue
                                if (not feature.token_is_max_context.get(start_index_effect, False)) or \
                                        (not feature.token_is_max_context.get(start_index_cause, False)):
                                    continue
                                if end_index_cause < start_index_cause:
                                    continue
                                if end_index_effect < start_index_effect:
                                    continue
                                length_cause = end_index_cause - start_index_cause + 1
                                length_effect = end_index_effect - start_index_effect + 1
                                if length_cause > max_answer_length:
                                    continue
                                if length_effect > max_answer_length:
                                    continue

                                # Heuristics extending the prediction spans
                                if full_sentence_heuristic or shared_sentence_heuristic:
                                    num_tokens = len(feature.tokens)
                                    all_sentence_offsets = [sequence_added_tokens] + \
                                                           [offset + 1 for offset in sentence_offsets] + \
                                                           [num_tokens]
                                    cause_sentences = []
                                    effect_sentences = []
                                    for sentence_idx in range(len(all_sentence_offsets) - 1):
                                        sentence_start, sentence_end = all_sentence_offsets[sentence_idx], \
                                                                       all_sentence_offsets[sentence_idx + 1]
                                        if sentence_start <= start_index_cause < sentence_end:
                                            cause_sentences.append(sentence_idx)
                                        if sentence_start <= start_index_effect < sentence_end:
                                            effect_sentences.append(sentence_idx)

                                    # Heuristic (first rule): if a sentence contains only 1 clause the clause is
                                    # extended to the entire sentence.
                                    if set(cause_sentences).isdisjoint(set(effect_sentences)) \
                                            and full_sentence_heuristic:
                                        start_index_cause = min(
                                            [all_sentence_offsets[sent] for sent in cause_sentences])
                                        end_index_cause = max(
                                            [all_sentence_offsets[sent + 1] - 1 for sent in cause_sentences])
                                        start_index_effect = min(
                                            [all_sentence_offsets[sent] for sent in effect_sentences])
                                        end_index_effect = max(
                                            [all_sentence_offsets[sent + 1] - 1 for sent in effect_sentences])
                                    # Heuristic (third rule): if a sentence contains only 2 clauses the span is
                                    # extended as much as possible.
                                    if not set(cause_sentences).isdisjoint(set(effect_sentences)) \
                                            and shared_sentence_heuristic \
                                            and len(cause_sentences) == 1 \
                                            and len(effect_sentences) == 1:
                                        if start_index_cause < start_index_effect:
                                            start_index_cause = min(
                                                [all_sentence_offsets[sent] for sent in cause_sentences])
                                            end_index_effect = max(
                                                [all_sentence_offsets[sent + 1] - 1 for sent in effect_sentences])
                                        else:
                                            start_index_effect = min(
                                                [all_sentence_offsets[sent] for sent in effect_sentences])
                                            end_index_cause = max(
                                                [all_sentence_offsets[sent + 1] - 1 for sent in cause_sentences])

                                prelim_predictions.append(
                                    _PrelimPrediction(
                                        feature_index=feature_index,
                                        start_index_cause=start_index_cause,
                                        end_index_cause=end_index_cause,
                                        start_logit_cause=start_logits_cause[start_index_cause],
                                        end_logit_cause=end_logits_cause[end_index_cause],
                                        start_index_effect=start_index_effect,
                                        end_index_effect=end_index_effect,
                                        start_logit_effect=start_logits_effect[start_index_effect],
                                        end_logit_effect=end_logits_effect[end_index_effect]
                                    )
                                )
    return prelim_predictions


def get_predictions(preliminary_predictions: List[_PrelimPrediction], n_best_size: int,
                    features: List[FinCausalFeatures], example: FinCausalExample) -> List[_NbestPrediction]:
    seen_predictions_cause = {}
    seen_predictions_effect = {}
    nbest = []
    for prediction in preliminary_predictions: # 30 elements here! -> pick top-5 as n-best!
        if len(nbest) >= n_best_size:
            break
        feature = features[prediction.feature_index]
        if prediction.start_index_cause > 0:  # this is a non-null prediction
            orig_doc_start_cause = feature.token_to_orig_map[prediction.start_index_cause]
            orig_doc_end_cause = feature.token_to_orig_map[prediction.end_index_cause]
            orig_doc_start_cause_char = example.word_to_char_mapping[orig_doc_start_cause]
            if orig_doc_end_cause < len(example.word_to_char_mapping) - 1:
                orig_doc_end_cause_char = example.word_to_char_mapping[orig_doc_end_cause + 1]
            else:
                orig_doc_end_cause_char = len(example.context_text)
            final_text_cause = example.context_text[orig_doc_start_cause_char: orig_doc_end_cause_char]
            final_text_cause = final_text_cause.strip()

            orig_doc_start_effect = feature.token_to_orig_map[prediction.start_index_effect]
            orig_doc_end_effect = feature.token_to_orig_map[prediction.end_index_effect]
            orig_doc_start_effect_char = example.word_to_char_mapping[orig_doc_start_effect]
            if orig_doc_end_effect < len(example.word_to_char_mapping) - 1:
                orig_doc_end_effect_char = example.word_to_char_mapping[orig_doc_end_effect + 1]
            else:
                orig_doc_end_effect_char = len(example.context_text)
            final_text_effect = example.context_text[orig_doc_start_effect_char: orig_doc_end_effect_char]
            final_text_effect = final_text_effect.strip()

            if final_text_cause in seen_predictions_cause and final_text_effect in seen_predictions_effect:
                continue

            seen_predictions_cause[final_text_cause] = True
            seen_predictions_cause[final_text_effect] = True
        else:
            final_text_cause = final_text_effect = ""
            seen_predictions_cause[final_text_cause] = True
            seen_predictions_cause[final_text_effect] = True
            orig_doc_start_cause = prediction.start_index_cause
            orig_doc_end_cause = prediction.end_index_cause
            orig_doc_start_effect = prediction.end_index_effect
            orig_doc_end_effect = prediction.end_index_effect

        nbest.append(
            _NbestPrediction(text_cause=final_text_cause,
                             start_logit_cause=prediction.start_logit_cause,
                             end_logit_cause=prediction.end_logit_cause,
                             start_index_cause=orig_doc_start_cause,
                             end_index_cause=orig_doc_end_cause,
                             text_effect=final_text_effect,
                             start_logit_effect=prediction.start_logit_effect,
                             end_logit_effect=prediction.end_logit_effect,
                             start_index_effect=orig_doc_start_effect,
                             end_index_effect=orig_doc_end_effect,
                             ))
    return nbest


def compute_predictions_logits(
        all_examples: List[FinCausalExample],
        all_features: List[FinCausalFeatures],
        all_results: List[FinCausalResult],
        output_dir: Path,
        sequence_added_tokens: int,
        run_config: RunConfig) -> collections.OrderedDict:
    example_index_to_features = collections.defaultdict(list)
    for feature in all_features:
        example_index_to_features[feature.example_index].append(feature)

    unique_id_to_result = {}
    for result in all_results:
        unique_id_to_result[result.unique_id] = result

    all_predictions = collections.OrderedDict()
    all_nbest_json = collections.OrderedDict()

    for (example_index, example) in enumerate(all_examples):
        features = example_index_to_features[example_index]
        suffix_index = 0
        if example.example_id.count('.') == 2 and run_config.top_n_sentences:
            suffix_index = int(example.example_id.split('.')[-1])
        prelim_predictions = filter_impossible_spans(features, # predefined limitations! see the original paper of GPe
                                                     unique_id_to_result,
                                                     run_config.n_best_size,
                                                     run_config.max_answer_length,
                                                     sequence_added_tokens,
                                                     run_config.sentence_boundary_heuristic,
                                                     run_config.full_sentence_heuristic,
                                                     run_config.shared_sentence_heuristic, )
        prelim_predictions = sorted(list(set(prelim_predictions)),
                                    key=lambda x: (x.start_logit_cause + x.end_logit_cause +
                                                   x.start_logit_effect + x.end_logit_effect), # NOTE sum-up of these four scores!
                                    reverse=True)

        nbest = get_predictions(prelim_predictions, run_config.n_best_size, features, example) # NOTE important!

        # In very rare edge cases we could have no valid predictions. So we
        # just create a none prediction in this case to avoid failure.
        if not nbest:
            nbest.append(_NbestPrediction(text_cause="empty", start_logit_cause=0.0, end_logit_cause=0.0,
                                          text_effect="empty", start_logit_effect=0.0, end_logit_effect=0.0,
                                          start_index_effect=0, end_index_effect=0,
                                          start_index_cause=0, end_index_cause=0))

        assert len(nbest) >= 1

        total_scores = []
        best_non_null_entry = None
        for entry in nbest:
            total_scores.append(entry.start_logit_cause + entry.end_logit_cause +
                                entry.start_logit_effect + entry.end_logit_effect)
            if not best_non_null_entry:
                if entry.text_cause and entry.text_effect:
                    best_non_null_entry = entry

        probabilities = _compute_softmax(total_scores)

        nbest_json = []
        current_example_spans = []
        for (i, entry) in enumerate(nbest):
            output = collections.OrderedDict()
            output["text"] = example.context_text
            output["probability"] = probabilities[i]
            output["cause_text"] = entry.text_cause
            output["cause_start_index"] = entry.start_index_cause
            output["cause_end_index"] = entry.end_index_cause
            output["cause_start_score"] = entry.start_logit_cause
            output["cause_end_score"] = entry.end_logit_cause
            output["effect_text"] = entry.text_effect
            output["effect_start_score"] = entry.start_logit_effect
            output["effect_end_score"] = entry.end_logit_effect
            output["effect_start_index"] = entry.start_index_effect
            output["effect_end_index"] = entry.end_index_effect
            new_span = SpanCombination(start_cause=entry.start_index_cause, end_cause=entry.end_index_cause,
                                       start_effect=entry.start_index_effect, end_effect=entry.end_index_effect)
            output["is_new"] = all([new_span != other for other in current_example_spans])
            nbest_json.append(output)
            current_example_spans.append(new_span)

        assert len(nbest_json) >= 1
        if suffix_index > 0:
            suffix_index -= 1
        # 重要：当suffix_index=0的时候，取的是0号元素；
        # 然而，当suffix_index>=1的时候，需要取值是suffix_index -= 1
        # 这个是从N-best构造1-best的关键！！！
        all_predictions[example.example_id] = {"text": nbest_json[suffix_index]["text"],
                                               "cause_text": nbest_json[suffix_index]["cause_text"],
                                               "effect_text": nbest_json[suffix_index]["effect_text"]}
        all_nbest_json[example.example_id] = nbest_json
    
    sample_num = len(all_predictions)
    output_prediction_file = output_dir / "predictions_sample{}.json".format(sample_num)
    csv_output_prediction_file = output_dir / "predictions_sample{}.csv".format(sample_num)
    output_nbest_file = output_dir / "nbest_predictions_sample{}.json".format(sample_num)

    logger.info("Writing predictions to: %s" % output_prediction_file)
    with open(output_prediction_file, "w") as writer:
        writer.write(json.dumps(all_predictions, indent=4) + "\n")

    with open(csv_output_prediction_file, "w", encoding='utf-8', newline='') as writer:
        csv_writer = csv.writer(writer, delimiter=';')
        csv_writer.writerow(['Index', 'Text', 'Cause', 'Effect'])
        for (example_id, prediction) in all_predictions.items():
            csv_writer.writerow([example_id, prediction['text'], prediction['cause_text'], prediction['effect_text']])

    logger.info("Writing nbest to: %s" % output_nbest_file)
    with open(output_nbest_file, "w") as writer:
        writer.write(json.dumps(all_nbest_json, indent=4) + "\n")

    return all_predictions


class SpanCombination:
    def __init__(self, start_cause: int, end_cause: int, start_effect: int, end_effect: int):
        self.start_cause = start_cause
        self.start_effect = start_effect
        self.end_cause = end_cause
        self.end_effect = end_effect

    def __eq__(self, other):
        overlapping_cause = (self.start_cause <= other.start_cause <= self.end_cause) or \
                            (self.start_cause <= other.end_cause <= self.end_cause) or \
                            (self.start_effect <= other.start_cause <= self.end_effect) or \
                            (self.start_effect <= other.end_cause <= self.end_effect)
        overlapping_effect = (self.start_effect <= other.start_effect <= self.end_effect) or \
                             (self.start_effect <= other.end_effect <= self.end_effect) or \
                             (self.start_cause <= other.start_effect <= self.end_cause) or \
                             (self.start_cause <= other.end_effect <= self.end_cause)
        return overlapping_cause and overlapping_effect


def _get_best_indexes(logits, n_best_size) -> List[int]:
    """Get the n-best logits from a list."""
    index_and_score = sorted(enumerate(logits), key=lambda x: x[1], reverse=True)

    best_indexes = []
    for i in range(len(index_and_score)):
        if i >= n_best_size:
            break
        best_indexes.append(index_and_score[i][0])
    return best_indexes


def _compute_softmax(scores) -> List[float]:
    """Compute softmax probability over raw logits."""
    if not scores:
        return []

    max_score = None
    for score in scores:
        if max_score is None or score > max_score:
            max_score = score

    exp_scores = []
    total_sum = 0.0
    for score in scores:
        x = math.exp(score - max_score)
        exp_scores.append(x)
        total_sum += x

    probabilities = []
    for score in exp_scores:
        probabilities.append(score / total_sum)
    return probabilities
