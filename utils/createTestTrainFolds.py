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

""" Create the intent test and train folds for cross validation
"""
import os
import csv
import pandas as pd
from argparse import ArgumentParser
from sklearn.model_selection import KFold
from __init__ import FOLD_NUM_DEFAULT, UTF_8, GOLDEN_INTENT_COLUMN, \
                  UTTERANCE_COLUMN, TRAIN_FILENAME, TEST_FILENAME


def func(args):
    df = pd.read_csv(args.infile, quoting=csv.QUOTE_ALL, encoding=UTF_8,
                     header=None)
    kf = KFold(n_splits=args.fold_num, shuffle=True)
    for fold_idx, (train_idx, test_idx) in \
             enumerate(kf.split(df.index.to_numpy())):
        out_directory = os.path.join(args.outdir, str(fold_idx))
        if not os.path.exists(out_directory):
            os.makedirs(out_directory)
        df.iloc[train_idx].to_csv(os.path.join(out_directory, TRAIN_FILENAME),
                                  quoting=csv.QUOTE_ALL, encoding=UTF_8,
                                  index=False, header=False)
        df.iloc[test_idx].to_csv(os.path.join(out_directory, TEST_FILENAME),
                                 quoting=csv.QUOTE_ALL, encoding=UTF_8,
                                 index=False, header=[UTTERANCE_COLUMN,
                                                      GOLDEN_INTENT_COLUMN])


def create_parser():
    parser = ArgumentParser(description="Create the intent test and \
                            train folds for cross validation")
    parser.add_argument('-i', '--infile', type=str, required=True,
                        help='Input file')
    parser.add_argument('-o', '--outdir', type=str, help='Output directory',
                        default=os.getcwd())
    parser.add_argument('-k', '--fold_num', type=int, default=FOLD_NUM_DEFAULT)

    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
