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
from argparse import ArgumentParser
from sklearn.metrics import confusion_matrix
from __init__ import UTF_8


def func(args):
    in_df = pd.read_csv(args.in_file, quoting=csv.QUOTE_ALL,
                        encoding=UTF_8, keep_default_na=False)
    # Look for target columns
    if args.test_column not in in_df or args.golden_column not in in_df:
        raise ValueError('Missing required columns')

    labels = in_df[args.golden_column].drop_duplicates().sort_values()

    output_matrix = \
        confusion_matrix(y_true=in_df[args.golden_column],
                         y_pred=in_df[args.test_column],
                         labels=labels)

    #Thanks to https://stackoverflow.com/questions/50325786/sci-kit-learn-how-to-print-labels-for-confusion-matrix for this clever line of python
    index_labels  = ['golden:{:}'.format(x) for x in labels]
    column_labels = [  'test:{:}'.format(x) for x in labels] 

    out_df = pd.DataFrame(output_matrix, 
                           index=index_labels,
                           columns=column_labels)

    out_df.to_csv(args.out_file, encoding='utf-8', quoting=csv.QUOTE_ALL, index=index_labels, columns=column_labels)
    print ("Wrote confusion matrix output to {}.".format(args.out_file))

    #Plot a normalized confusion matrix as a heatmap
    plt.figure(figsize = (10,10))
    df_cm = pd.DataFrame(output_matrix, index=index_labels, columns=column_labels)
    df_cm = df_cm.to_numpy()
    df_cm = df_cm.astype('float') / df_cm.sum(axis=1)[:, np.newaxis]
    sns.set(font_scale=1)
    # Add 'annot=True' to the list of options for heatmap if you want to print the numbers, ideal only for small maps
    hm = sns.heatmap(df_cm, cmap="Greys",cbar=False,fmt='.1%',linewidths=0.1,linecolor='black',xticklabels=column_labels, yticklabels=index_labels)
    hm.set_yticklabels(hm.get_yticklabels(), rotation=0)
    hm.set_xticklabels(hm.get_xticklabels(), rotation=90)
    plt.title("Normalized Confusion Matrix")
    plt.tight_layout()
    plt.autoscale()
    out_image_file = args.out_file[:-4] + ".png"
    plt.savefig(out_image_file,bbox_inches='tight',dpi=400)
   
    print ("Wrote confusion matrix diagram to {}.".format(out_image_file))

def create_parser():
    parser = ArgumentParser(
        description='Generate confusion matrix')
    parser.add_argument('-i', '--in_file', type=str, required=True,
                        help='File that contains intent test and golden data')
    parser.add_argument('-o', '--out_file', type=str,
                        help='Output file path',
                        default='confusion-matrix.csv')
    parser.add_argument('-t', '--test_column', type=str,
                        default='predicted intent',
                        help='Test column name')
    parser.add_argument('-g', '--golden_column', type=str,
                        default='golden intent',
                        help='Golden column name')
    #parser.add_argument('-p', '--partial_credit_on', type=str,
    #                    help='Use only if partial credit scoring ')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
