#! /usr/bin/python
# coding: utf-8

# Copyright 2022 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Compares two different blind test runs and builds summary metrics
"""
import csv
import pandas as pd
import math
from __init__ import UTF_8
from argparse import ArgumentParser

def results_file_to_dataframe(filename:str):
    in_df = pd.read_csv(filename, quoting=csv.QUOTE_ALL,
                        encoding=UTF_8, keep_default_na=False)
    in_df["confidence"] = pd.to_numeric(in_df["confidence"], downcast="float")
    return in_df

def count_correct_answers(df:pd.DataFrame):
    count = df[df["golden intent"] == df["predicted intent"]].shape[0]
    return count

def summarize_correctness(curr_df:pd.DataFrame, prev_df:pd.DataFrame):
    print("** Summarized results **")
    total = len(curr_df)
    curr_correct = count_correct_answers(curr_df)
    diff_correct = count_correct_answers(prev_df)
    print(f"Current  : {curr_correct} of {total} correct")
    print(f"Previous : {diff_correct} of {total} correct")
    if(curr_correct > diff_correct):
        print(f"IMPROVED : {curr_correct-diff_correct} of {total}")
    elif(curr_correct < diff_correct):
        print(f"REGRESSED: {diff_correct-curr_correct} of {total}")
    else:
        print(f"NO DIFFERENCE in total correctness")
    print()

''' Input: Current and previous dataframes.  Output: One dataframe merged on utterance, with current/previous versions of predicted intent, confidence, and score"'''
def merge_dataframes(curr_df:pd.DataFrame, prev_df:pd.DataFrame):
    curr_renamed = curr_df.rename(columns={"predicted intent": "current_prediction",  "confidence": "current_confidence",  "score":"current_score"})
    prev_renamed = prev_df.rename(columns={"predicted intent": "previous_prediction", "confidence": "previous_confidence", "score":"previous_score"})
    curr_renamed = curr_renamed.drop(columns=["detected entity","dialog response","does intent match"])
    prev_renamed = prev_renamed.drop(columns=["detected entity","dialog response","does intent match"])
    prev_renamed = prev_renamed.drop(columns=["golden intent"])

    merged_df = pd.merge(curr_renamed, prev_renamed, how="inner", on="utterance")
    return merged_df

def compare_utterances(df:pd.DataFrame, out_file_name:str):
    print("** Utterance-specific results **")
    df_improved =  df[df['current_score'] > df['previous_score']]
    df_regressed = df[df['current_score'] < df['previous_score']]

    improved_utterance_filename = f"{out_file_name}_improved_utterances.csv"
    regressed_utterance_filename = f"{out_file_name}_regressed_utterances.csv"
    print(f"IMPROVED  utterances: {df_improved.shape[0]} total, saving to {improved_utterance_filename}")
    df_improved.to_csv(improved_utterance_filename, encoding='utf-8', quoting=csv.QUOTE_ALL, index=None)

    print(f"REGRESSED utterances: {df_regressed.shape[0]} total, saving to {regressed_utterance_filename}")
    df_regressed.to_csv(regressed_utterance_filename, encoding='utf-8', quoting=csv.QUOTE_ALL, index=None)

    curr_correct_confidence   = get_confidence(df, "current", 1)
    prev_correct_confidence   = get_confidence(df, "previous", 1)
    curr_incorrect_confidence = get_confidence(df, "current", 0)
    prev_incorrect_confidence = get_confidence(df, "previous", 0)
    print(f"Average confidence in correct   answer (current ): {curr_correct_confidence:.3f}")
    print(f"Average confidence in correct   answer (previous): {prev_correct_confidence:.3f}")
    print(f"Average confidence in incorrect answer (current ): {curr_incorrect_confidence:.3f}")
    print(f"Average confidence in incorrect answer (previous): {prev_incorrect_confidence:.3f}")
    print()

def get_confidence(df:pd.DataFrame, type:str, score:int):
    correct = df[df[f"{type}_score"] == score]
    avg_conf = correct[f"{type}_confidence"].mean()
    if math.isnan(avg_conf):
        avg_conf = 0
    return avg_conf

def compare_intents(df:pd.DataFrame, out_file_name:str):
    print("** Intent-specific results **")
    intents = df["golden intent"].drop_duplicates().sort_values()
    metrics = []
    for intent in intents:
        metrics.append(compute_intent_metrics_tuple(df, intent))
    summary = pd.DataFrame(metrics)
    #print(summary.head(n=10))

    intent_summary_file = f"{out_file_name}_intent_comparison.csv"
    print(f"Computing intent summary comparison, saving to {intent_summary_file}")
    summary.to_csv(intent_summary_file, encoding='utf-8', quoting=csv.QUOTE_ALL, index=None, float_format="%.3f")

    improved_intents_df = summary[summary["curr_correct"] >  summary["prev_correct"]]
    regressed_intents_df = summary[summary["curr_correct"] <  summary["prev_correct"]]
    no_change_intents_df = summary[summary["curr_correct"] == summary["prev_correct"]]
    print(f"IMPROVED  accuracy on {improved_intents_df.shape[0]} intents")
    print(f"REGRESSED accuracy on {regressed_intents_df.shape[0]} intents")
    print(f"UNCHANGED accuracy on {no_change_intents_df.shape[0]} intents")
    print()

def compute_intent_metrics_tuple(df:pd.DataFrame, intent:str):
    tuple = {}
    tuple['intent'] = intent
    df_i = df[df['golden intent']==intent]

    tuple['total'] = df_i.shape[0]
    tuple['curr_correct'] = df_i[df_i['current_score'] == 1].shape[0]
    tuple['prev_correct'] = df_i[df_i['previous_score'] == 1].shape[0]
    tuple['diff_correct'] = tuple['curr_correct'] - tuple['prev_correct']
    tuple['curr_correct_confidence'] = get_confidence(df_i, "current", 1)
    tuple['prev_correct_confidence'] = get_confidence(df_i, "previous", 1)
    tuple['diff_correct_confidence'] = tuple['curr_correct_confidence'] - tuple['prev_correct_confidence']
    tuple['curr_incorrect_confidence'] = get_confidence(df_i, "current", 0)
    tuple['prev_incorrect_confidence'] = get_confidence(df_i, "previous", 0)
    tuple['diff_incorrect_confidence'] = tuple['curr_incorrect_confidence'] - tuple['prev_incorrect_confidence']

    return tuple


def func(args):
    #convert input
    curr_df = results_file_to_dataframe(args.current_file)
    prev_df = results_file_to_dataframe(args.previous_file)
    out_file_base = args.out_file[:-4] if args.out_file.endswith(".csv") else args.out_file

    #columns in each: utterance,golden intent, predicted intent, confidence, detected entity, dialog response, score, does intent match
    #Merge to: "utterance","golden intent","current_prediction","current_confidence","current_score","previous_prediction","previous_confidence","previous_score"
    merged_df = merge_dataframes(curr_df, prev_df)

    #print reports
    summarize_correctness(curr_df, prev_df)
    compare_intents(merged_df, out_file_base)
    compare_utterances(merged_df, out_file_base)

def create_parser():
    parser = ArgumentParser(
        description='Generate confusion matrix')
    parser.add_argument('-c', '--current_file', type=str, required=True,
                        help='File that contains current blind test results')
    parser.add_argument('-p', '--previous_file', type=str, required=True,
                        help='File that contains previous blind test results')
    parser.add_argument('-o', '--out_file', type=str,
                        help='Output file base pathname, will be modified to create different reports',
                        default='compare.csv')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
