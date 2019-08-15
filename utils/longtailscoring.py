#! /usr/bin/python
# coding: utf-8

# Copyright 2018 IBM All Rights Reserved.
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
""" Transform initial classification results based on presence of a "long tail intent"
"""
import csv
import pandas as pd
from argparse import ArgumentParser
from __init__ import UTF_8
from intentmetrics import func as intent_metrics_function
from confusionmatrix import func as confusion_matrix_function

def func(args):
    in_df = pd.read_csv(args.in_file, quoting=csv.QUOTE_ALL,
                        encoding=UTF_8, keep_default_na=False)
    # Look for target columns
    if args.test_column not in in_df:
        raise ValueError('Missing required column: test_column')
    if args.golden_column not in in_df:
        raise ValueError('Missing required column: golden_column')
    if args.confidence_column not in in_df:
        raise ValueError('Missing required column: confidence_column')

    long_tail_label = args.long_tail_intent_name
    tau = args.confidence_level
    
    out_test = []
    idx = 0
    correct = 0
    for row in in_df.itertuples():
       #Convert based on confidence
       if in_df[args.confidence_column][idx] < tau:
          out_test.append(long_tail_label)
       else:
          out_test.append(in_df[args.test_column][idx])
       if out_test[idx] == in_df[args.golden_column][idx]:
          correct = correct + 1
       idx = idx+1
       
    out_df = pd.DataFrame(data={args.golden_column: in_df[args.golden_column],
                                args.test_column: out_test})

    out_df.to_csv(args.out_file, encoding='utf-8', quoting=csv.QUOTE_ALL,
                  index=False, columns=[args.golden_column, args.test_column])

    accuracy = format(correct/idx, '.2f')
    print ("Wrote long-tail converted output to {}. Includes {} correct intents in {} tries for accuracy of {}.".format(args.out_file, correct, idx, accuracy))

    #Invoke additional analyses
    base_out_file = args.out_file
    args.in_file = base_out_file

    args.partial_credit_on = None
    args.out_file = base_out_file + ".metrics.csv"
    intent_metrics_function(args)

    args.out_file = base_out_file + ".confusion.csv"
    confusion_matrix_function(args)

def create_parser():
    parser = ArgumentParser(
        description='Generate long tail intent scoring')
    parser.add_argument('-i', '--in_file', type=str, required=True,
                        help='File that contains intent test and golden data')
    parser.add_argument('-o', '--out_file', type=str,
                        help='Output file path',
                        default='intent-metrics.csv')
    parser.add_argument('-t', '--test_column', type=str,
                        default='predicted intent',
                        help='Test column name')
    parser.add_argument('-g', '--golden_column', type=str,
                        default='golden intent',
                        help='Golden column name')
    parser.add_argument('-c', '--confidence_column', type=str,
                        default='confidence',
                        help='Confidence column name')
    parser.add_argument('-l', '--confidence_level', type=float,
                        default='0.2',
                        help='Confidence threshold for long-tail (tau)')
    parser.add_argument('-n', '--long_tail_intent_name', type=str,
                        default='Irrelevant',
                        help='Long tail intent name')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
