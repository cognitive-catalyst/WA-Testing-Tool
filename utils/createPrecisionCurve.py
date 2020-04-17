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

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Generate images without having a window appear
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from argparse import ArgumentParser
from itertools import cycle
import pandas as pd
import csv

from __init__ import INTENT_JUDGE_COLUMN, UTF_8, CONFIDENCE_COLUMN, \
                  PREDICTED_INTENT_COLUMN, GOLDEN_INTENT_COLUMN, \
                  INTENT_COLUMN, POPULATION_WEIGHT_MODE, \
                  EQUAL_WEIGHT_MODE, DEFAULT_CONF_THRES, SCORE_COLUMN

# total different number of line style len(line_styles) * len(line_color) = 12
line_styles = ['-', '--', '-.', ':']
line_color = ['b', 'g', 'r']

LEGEND_AXIS_FONT_SIZE = 14
TITLE_FONT_SIZE = 16

WEIGHT_COLUMN = 'weight'


def func(args):
    """ Read classifiers results and draw the curves on one canvas for comparision

        Input Schema:
        | predicted intent | confidence       | does intent match |
        | intent 0         | confidence score | yes/no value      |
    """

    classifier_stat_list = []
    cf_frames = []
    confidences_list = []
    intents_in_results = pd.Series(dtype='float')

    classifier_num = len(args.classifiers_results)

    # Prepare labels for each curve
    labels = [os.path.splitext(os.path.basename(file_path))[0]
              for file_path in args.classifiers_results]

    # Only do cutomization on labels if numbers match
    if args.classifier_names and \
            (len(args.classifier_names) == classifier_num):
        labels = args.classifier_names

    # Initialization
    for i in range(classifier_num):
        file_path = args.classifiers_results[i]
        frame = pd.read_csv(file_path, encoding=UTF_8, quoting=csv.QUOTE_ALL)
        if INTENT_JUDGE_COLUMN not in frame.columns:  # Column validation
            raise ValueError("'{}' column not in {}".format(
                INTENT_JUDGE_COLUMN, file_path))
        # Read the cf files into list
        cf_frames.append(frame)
        # Collect all intents from the classification results
        intents_in_results = pd.concat([intents_in_results,
                                        frame[PREDICTED_INTENT_COLUMN]])
        # Convert nan to zero values to avoid use zero as divider
        confidences_list.append(frame[CONFIDENCE_COLUMN].fillna(0)
                                .drop_duplicates().sort_values().tolist())

    intents_in_results = intents_in_results.drop_duplicates()

    # Read weight
    weights_df = None
    weight_mode = args.weight.lower()
    # Read the intent weights pairs from file
    if weight_mode != POPULATION_WEIGHT_MODE and \
       weight_mode != EQUAL_WEIGHT_MODE:
        try:
            weights_df = pd.read_csv(args.weight, encoding=UTF_8,
                                     quoting=csv.QUOTE_ALL)
            # Validate the completeness
            for _, intent in intents_in_results.iteritems():
                if not any(weights_df[INTENT_COLUMN] == intent):
                    raise ValueError("'{}' intent not in {}".format(
                        intent, args.weight))
        except Exception as e:
            print(e)
            weight_mode = POPULATION_WEIGHT_MODE  # default population mode
            print('Fall back to {} mode'.format(POPULATION_WEIGHT_MODE))

    # Init the classifier_stat_list:
    for i in range(classifier_num):
        # array of zeros to hold precision values
        classifier_stat_list.append(np.zeros([len(confidences_list[i]), 3]))

    for j in range(classifier_num):
        confidences = confidences_list[j]
        for i in range(len(confidences)):
            conf = confidences[i]
            cf_frame = cf_frames[j]
            precision = 0
            answered = \
                cf_frame[cf_frame[CONFIDENCE_COLUMN] >= conf].shape[0]
            if weight_mode == POPULATION_WEIGHT_MODE:
                correct = cf_frame[
                    cf_frame[CONFIDENCE_COLUMN] >= conf][SCORE_COLUMN].sum()
                precision = correct / answered
                # print(precision)
            else:
                intent_uttr_num_map = \
                  cf_frame[cf_frame[CONFIDENCE_COLUMN] >= conf] \
                  .groupby(PREDICTED_INTENT_COLUMN)[PREDICTED_INTENT_COLUMN] \
                  .count().to_dict()

                # Calulate precision use equal weights
                uttr_correct_intent = \
                    cf_frame[cf_frame[CONFIDENCE_COLUMN] >= conf] \
                    .groupby(GOLDEN_INTENT_COLUMN)[SCORE_COLUMN] \
                    .sum()

                intent_weights = None
                weight_coeff = 1 / len(intent_uttr_num_map)

                if weight_mode != EQUAL_WEIGHT_MODE:
                    required_weights_df = \
                        weights_df[
                            weights_df[INTENT_COLUMN]
                            .isin(uttr_correct_intent.index)]
                    weight_sum = required_weights_df[WEIGHT_COLUMN].sum()
                    # Normalize weights
                    weights_df[WEIGHT_COLUMN] = \
                        weights_df[WEIGHT_COLUMN] / weight_sum
                    intent_weights = \
                        weights_df.set_index(INTENT_COLUMN)[WEIGHT_COLUMN] \
                        .to_dict()

                for intent, correct_intent_num in \
                        uttr_correct_intent.iteritems():
                    if weight_mode != EQUAL_WEIGHT_MODE:
                        weight_coeff = intent_weights[intent]

                    precision += \
                        weight_coeff * correct_intent_num \
                        / intent_uttr_num_map[intent]

            classifier_stat_list[j][i, 0] = precision
            classifier_stat_list[j][i, 1] = 100 * answered / len(cf_frame)
            classifier_stat_list[j][i, 2] = conf

    for idx in range(len(classifier_stat_list)):
        # reversing order for helpful plotting
        classifier_stat_list[idx] = classifier_stat_list[idx][::-1]

    # plotting
    fig = plt.figure()
    ax = fig.gca()

    ax.set_ylim([0, 1.0]) # Hardcoding y-axis to a consistent 0-1.0 for the benefit of easing historical comparisions

    ax.grid(color='b', linestyle='--', alpha=0.3)
    ax.set_xlabel('Percentage of Questions Answered',
                  fontsize=LEGEND_AXIS_FONT_SIZE)
    ax.set_ylabel('Precision', fontsize=LEGEND_AXIS_FONT_SIZE)
    line_style_cycler = cycle(line_styles)
    line_color_cycler = cycle(line_color)

    lines = []  # reference to lines
    # plot the curve and save the figure
    for i in range(len(classifier_stat_list)):
        classifier_stat = classifier_stat_list[i]
        # Default to the idx of lowest conf
        tau_idx = len(classifier_stat[:, 2]) - 1
        indices_gtr_tau, = np.where(classifier_stat[:, 2] <= args.tau)
        if len(indices_gtr_tau) > 0:
            tau_idx = indices_gtr_tau[0]

        color = next(line_color_cycler)
        line, = plt.plot(classifier_stat[:, 1], classifier_stat[:, 0],
                         color=color, label=labels[i],
                         linestyle=next(line_style_cycler))

        plt.plot(classifier_stat[tau_idx, 1], classifier_stat[tau_idx, 0],
                 '{}o'.format(color), markerfacecolor='None')
        lines.append(line)

    tau_desc = mlines.Line2D([], [], markeredgecolor='black', marker='o',
                             linestyle='None', markerfacecolor='None',
                             markersize=10,
                             label='tau = {}'.format(args.tau))

    ax.legend(handles=lines + [tau_desc], loc='lower left', shadow=False,
              prop={'size': LEGEND_AXIS_FONT_SIZE})
    ax.set_title(args.figure_title,
                 fontsize=TITLE_FONT_SIZE)

    if args.ymin != 0.0:
        plt.ylim(args.ymin, 1.0)
    # Save figure as file
    plt.savefig(args.outfile)

    print("Wrote precision curve to {}".format(args.outfile))


def create_parser():
    parser = ArgumentParser(description="Draw precision curves on a single canvas \
                            from multiple classifiers' classification results")
    parser.add_argument('-i', '--classifiers_results', nargs='+',
                        required=True,
                        help='Files of results from individual classifiers')
    parser.add_argument('-n', '--classifier_names', nargs='*',
                        help='Names of each classifier')
    parser.add_argument('-t', '--figure_title', required=True, type=str,
                        help='Title of output figure')
    parser.add_argument('-o', '--outfile', help='File of the output figure',
                        default='figure.png', type=str)
    parser.add_argument('-w', '--weight', default='population', type=str,
                        help='Weight configuration for each intent')
    parser.add_argument('--tau', default=DEFAULT_CONF_THRES, type=float,
                        help='Confidence threshold for curve marker')
    parser.add_argument('--ymin', default=0.0, type=float,
                        help='Minimum for Y axis')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
