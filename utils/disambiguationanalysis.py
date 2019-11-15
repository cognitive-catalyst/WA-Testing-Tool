#! /usr/bin/python
# coding: utf-8

# Copyright 2019 IBM All Rights Reserved.
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
""" Generate confusion matrix from intent training/testing results
"""
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import asyncio
from argparse import ArgumentParser
from sklearn.metrics import confusion_matrix
from __init__ import UTF_8, save_dataframe_as_csv, \
    UTTERANCE_COLUMN, GOLDEN_INTENT_COLUMN,PREDICTED_INTENT_COLUMN,CONFIDENCE_COLUMN,INTENT_JUDGE_COLUMN, \
    DISAMBIGUATION_OUT_FILENAME, DISAMBIGUATION_MAX_INTENTS_DEFAULT, DISAMBIGUATION_THRESHOLD_DEFAULT, \
    DISAMBIGUATION_THRESHOLD_COLUMN, DISAMBIGUATION_INTENT_COLUMN, \
    DISAMBIGUATION_BENEFIT_COLUMN, DISAMBIGUATION_NEGATIVE_COLUMN, DISAMBIGUATION_NO_HELP_COLUMN

initial_output_header = [UTTERANCE_COLUMN, GOLDEN_INTENT_COLUMN,PREDICTED_INTENT_COLUMN,CONFIDENCE_COLUMN,INTENT_JUDGE_COLUMN]
alt_intents_output_header = [PREDICTED_INTENT_COLUMN, CONFIDENCE_COLUMN, DISAMBIGUATION_INTENT_COLUMN]

def disambiguation_analysis(extended_out_df, row_idx, args):
    # Initialization
    disambiguation_benefit = 0
    intent_match = False

    # Calculate disambiguation threshold
    disambiguation_threshold = (extended_out_df.loc[row_idx][CONFIDENCE_COLUMN] * args.threshold) / 100
    extended_out_df.loc[row_idx, DISAMBIGUATION_THRESHOLD_COLUMN] = disambiguation_threshold

    for i in range(1,args.max_intents):
        predicted_intent = extended_out_df.loc[row_idx, PREDICTED_INTENT_COLUMN + '_' + str(i)]
#        extended_out_df.loc[row_idx, PREDICTED_INTENT_COLUMN + '_' + str(i)] = predicted_intent
        confidence = extended_out_df.loc[row_idx, CONFIDENCE_COLUMN + '_' + str(i)]
#        extended_out_df.loc[row_idx, CONFIDENCE_COLUMN + '_' + str(i)] = confidence
        disambiguated = 0
        if confidence >= disambiguation_threshold:
            disambiguated = 1
            if predicted_intent == extended_out_df.loc[row_idx, GOLDEN_INTENT_COLUMN]:
                disambiguation_benefit = 1

        extended_out_df.loc[row_idx, DISAMBIGUATION_INTENT_COLUMN + '_' + str(i)] = disambiguated

    # Detecting Disambiguation Benefit - Predicted != Golden and Golden = One of the alternate intents
    if (intent_match == False) and (disambiguation_benefit == 1):
        extended_out_df.loc[row_idx, DISAMBIGUATION_BENEFIT_COLUMN] = 1
    else:
        extended_out_df.loc[row_idx, DISAMBIGUATION_BENEFIT_COLUMN] = 0

    # Detecting Disambiguation No Benefit/Neutral - Predicted == Golden and Golden == One of the alternate intents
    if (intent_match == True) and (disambiguation_benefit == 0) and (disambiguated == 1):
        extended_out_df.loc[row_idx, DISAMBIGUATION_NEGATIVE_COLUMN] = 1
    else:
        extended_out_df.loc[row_idx, DISAMBIGUATION_NEGATIVE_COLUMN] = 0

    # Detecting Disambiguation No Help - Predicted != Golden and Golden != One of the alternate intents
    if (intent_match == False) and (disambiguation_benefit == 0) and (disambiguated == 0):
        extended_out_df.loc[row_idx, DISAMBIGUATION_NO_HELP_COLUMN] = 1
    else:
        extended_out_df.loc[row_idx, DISAMBIGUATION_NO_HELP_COLUMN] = 0

    extended_out_df.loc[row_idx, INTENT_JUDGE_COLUMN] = intent_match

    return extended_out_df


def func(args):
    disambiguation_df = pd.DataFrame()

    in_df = pd.read_csv(args.in_file, quoting=csv.QUOTE_ALL,
                        encoding=UTF_8, keep_default_na=False)
    # Look for target columns
#    if args.test_column not in in_df or args.golden_column not in in_df:
#        raise ValueError('Missing required columns')

    disambiguation_df[initial_output_header] = in_df.reindex(index=in_df.index, columns=initial_output_header)
    disambiguation_df[DISAMBIGUATION_THRESHOLD_COLUMN] = ''

    # Populate Intents
    for i in range(1,args.max_intents):
        disambiguation_df[[PREDICTED_INTENT_COLUMN + '_' + str(i)]] = in_df[[PREDICTED_INTENT_COLUMN + '_' + str(i)]].copy()
        disambiguation_df[[CONFIDENCE_COLUMN + '_' + str(i)]] = in_df[[CONFIDENCE_COLUMN + '_' + str(i)]].copy()
        disambiguation_df[DISAMBIGUATION_INTENT_COLUMN + '_' + str(i)] = ''

    disambiguation_df[DISAMBIGUATION_BENEFIT_COLUMN] = ''
    disambiguation_df[DISAMBIGUATION_NEGATIVE_COLUMN] = ''
    disambiguation_df[DISAMBIGUATION_NO_HELP_COLUMN] = ''

    for row_idx in range(disambiguation_df.shape[0]):
        disambiguation_analysis(disambiguation_df, row_idx, args)

    # Save Disambiguation output
    save_dataframe_as_csv(df=disambiguation_df, file=args.out_file)
    print("Wrote disambiguation analysis result file to {}".format(args.out_file))

def create_parser():
    parser = ArgumentParser(
        description='Generate analysis on disambiguation')
    parser.add_argument('-i', '--in_file', type=str, required=True,
                        help='File that contains intent test and golden data')
    parser.add_argument('-o', '--out_file', type=str,
                        help='Output file path',
                        default=DISAMBIGUATION_OUT_FILENAME)
    parser.add_argument('-m', '--max_intents', type=int,
                        help='Maximum alternate intents ',
                        default=DISAMBIGUATION_MAX_INTENTS_DEFAULT)
    parser.add_argument('-t', '--threshold', type=int,
                        default=DISAMBIGUATION_THRESHOLD_DEFAULT,
                        help='Percentage Disambiguation Threshold')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
