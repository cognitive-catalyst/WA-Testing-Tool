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
""" Generate per intent metrics on True Positive/False Positives
"""
import csv
import pandas as pd
from argparse import ArgumentParser
from sklearn.metrics import precision_recall_fscore_support
from __init__ import UTF_8

# For treemap
import matplotlib
import matplotlib.pyplot as plt
from  matplotlib.colors import LinearSegmentedColormap
import squarify

def func(args):
    in_df = pd.read_csv(args.in_file, quoting=csv.QUOTE_ALL,
                        encoding=UTF_8, keep_default_na=False)
    # Look for target columns
    if args.test_column not in in_df or args.golden_column not in in_df:
        raise ValueError('Missing required columns')

    labels = in_df[args.golden_column].drop_duplicates().sort_values()

    precisions, recalls, fscores, support = \
        precision_recall_fscore_support(y_true=in_df[args.golden_column],
                                        y_pred=in_df[args.test_column],
                                        labels=labels,
                                        zero_division=0)

    #Raw accuracy as well
    in_df['correct'] = (in_df[args.golden_column] == in_df[args.test_column])
    samples = len(in_df['correct'])
    num_correct = sum(in_df['correct'])
    accuracy = format(num_correct/samples, '.2f')

    if args.partial_credit_on is not None:
        for idx, label in enumerate(labels):
            retrieved_doc_indx = in_df[args.test_column] == label
            relevant_doc_indx = in_df[args.golden_column] == label
            retrieved_doc_num = len(in_df[retrieved_doc_indx])
            relevant_doc_num  = len(in_df[relevant_doc_indx])

            # precision and recall are 0 if retrieved and revelvant doc numbers are 0
            precision = in_df[retrieved_doc_indx]['score'].sum() / retrieved_doc_num if retrieved_doc_num != 0 else 0
            recall = in_df[relevant_doc_indx]['score'].sum()/ relevant_doc_num if relevant_doc_num != 0 else 0

            precisions[idx] = precision
            recalls[idx] = recall
            fscores[idx] = 0
            
            # handling edge case where precision and recall are 0. Avoids DivideByZeroError
            if precision != 0.0 and recall != 0.0:
                fscores[idx] = (2 * precision * recall) / (precision + recall)

    out_df = pd.DataFrame(data={'intent': labels,
                                'recall': recalls,
                                'precision': precisions,
                                'f-score': fscores,
                                'number of samples': support})

    out_df.to_csv(args.out_file, encoding='utf-8', quoting=csv.QUOTE_ALL,
                  index=False, columns=['intent', 'number of samples', 'recall',
                  'precision', 'f-score'] )

    print ("Wrote intent metrics output to {}. Includes {} correct intents in {} tries for accuracy of {}.".format(args.out_file, num_correct, samples, accuracy))

    # Fill f-score column with the recall when the precision is undefined.  Produces a more actionable tree map especially in partial-credit scenarios.
    if args.partial_credit_on is not None:
        out_df.loc[out_df['precision'] == 0.0,'f-score'] = out_df['recall']
    
    generateTreemap(args.out_file, out_df)

def generateTreemap(base_out_file, out_df):

    # Organize the values for a more readable map.
    # Sort by 'f-score' puts the worst performing intents in top-right and best in lower-left
    # Sort by 'number of samples' puts the intents with least samples in top-right and most-samples in lower-left
    out_df = out_df.sort_values(by=['f-score'], ascending=False)

    # Color should never be the only differentiating factor.
    # If you prefer sorting by 'number of samples' you should use the one-color scale as you otherwise have no visual color-less dimension
    #    to see 'f-score'
    #One-color alternative
    #cmap = matplotlib.cm.Greens
    #Two-color from red-to-green requires sorting by f-score for accessibility. Else you would sort by 'number of samples'
    cmap=LinearSegmentedColormap.from_list('rg',["r", "w", "g"], N=256)

    colors = [cmap(value) for value in out_df['f-score']]
    treemap = squarify.plot(sizes=out_df['number of samples'],
                            label=out_df['intent'],
                            color=colors, alpha=.8,
                            text_kwargs={'fontsize':3},
                            bar_kwargs={'linewidth':0.5, 'edgecolor':'#000000'} )
    plt.axis('off')
    plt.title("Metrics summary per intent\n(Box size from number of samples)")

    patches_array = [
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(0.0), linewidth=0.25, label='0%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(.25), linewidth=0.25, label='25%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(.50), linewidth=0.25, label='50%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(.75), linewidth=0.25, label='75%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(1.0), linewidth=0.25, label='100%')
    ]

    plt.legend(title="f-score",
               handles=patches_array,
               bbox_to_anchor=(1.05, 1),
               loc='upper left',
               borderaxespad=0.)

    metrics_file = base_out_file[:-4] + ".png"
    plt.savefig(metrics_file,bbox_inches='tight',dpi=400)
    print ("Wrote intent metrics tree map image to {}.".format(metrics_file))

def create_parser():
    parser = ArgumentParser(
        description='Generate intent metrics')
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
    parser.add_argument('-p', '--partial_credit_on', type=str,
                        help='Use only if partial credit scoring ')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
