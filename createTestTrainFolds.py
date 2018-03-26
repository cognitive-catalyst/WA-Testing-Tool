#! /usr/bin/python
""" Create the intent test and train folds for cross validation
"""
import os
import csv
import pandas as pd
from argparse import ArgumentParser
from sklearn.model_selection import KFold
from utils import FOLD_NUM_DEFAULT, UTF_8, GOLDEN_INTENT_COLUMN, \
                  UTTERANCE_COLUMN, TRAIN_FILENAME, TEST_FILENAME


def func(args):
    df = pd.read_csv(args.infile, quoting=csv.QUOTE_ALL, encoding=UTF_8,
                     header=None)
    kf = KFold(n_splits=args.fold_num, shuffle=True)
    for fold_idx, (train_idx, test_idx) in \
            enumerate(kf.split(df.index.get_values())):
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


if __name__ == '__main__':
    PARSER = ArgumentParser(description="Create the intent test and \
                            train folds for cross validation")
    PARSER.add_argument('-i', '--infile', type=str, required=True,
                        help='Input file')
    PARSER.add_argument('-o', '--outdir', type=str, help='Output directory',
                        default=os.getcwd())
    PARSER.add_argument('-k', '--fold_num', type=int, default=FOLD_NUM_DEFAULT)
    ARGS = PARSER.parse_args()
    func(ARGS)
