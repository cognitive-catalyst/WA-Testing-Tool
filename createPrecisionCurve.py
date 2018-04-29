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
import matplotlib.patches as mpatches
from argparse import ArgumentParser
from itertools import cycle
import pandas as pd
import csv

from utils import INTENT_JUDGE_COLUMN, UTF_8, CONFIDENCE_COLUMN, \
                  PREDICTED_INTENT_COLUMN, GOLDEN_INTENT_COLUMN, \
                  INTENT_COLUMN

# total different number of line style len(line_styles) * len(line_color) = 12
line_styles = ['-', '--', '-.', ':']
line_color = ['b', 'g', 'r']

LEGEND_AXIS_FONT_SIZE = 14
TITLE_FONT_SIZE = 16

WEIGHT_COLUMN = 'weight'

POPULATION_WEIGHT_MODE = 'population'
EQUAL_WEIGHT_MODE = 'equal'

CONF_THRES = 0.2


def func(args):
    """ Read classifiers results and draw the curves on one canvas for comparision

        Input Schema:
        | predicted intent | confidence       | does intent match |
        | intent 0         | confidence score | yes/no value      |
    """

    classifier_stat_list = []
    cf_frames = []
    # intent_uttr_num_mappings = []
    confidences_in_results = pd.Series()
    intents_in_results = pd.Series()

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
        confidences_in_results = pd.concat([confidences_in_results,
                                            frame[CONFIDENCE_COLUMN]])

    intents_in_results = intents_in_results.drop_duplicates()
    all_confidences = confidences_in_results.drop_duplicates().sort_values() \
                                                              .tolist()
    # Read weight
    weights_df = None
    weight_mode = args.weight.lower()
    # Read the intent weights pairs from file
    if weight_mode != POPULATION_WEIGHT_MODE and \
       weight_mode != EQUAL_WEIGHT_MODE:
        weights_df = pd.read_csv(weight_mode, encoding=UTF_8,
                                 quoting=csv.QUOTE_ALL)
        # Validate the completeness
        for _, intent in intents_in_results.iteritems():
            if not any(weights_df[INTENT_COLUMN] == intent):
                raise ValueError("'{}' intent not in {}".format(
                    intent, weight_mode))

    confidence_num = len(all_confidences)
    # Init the classifier_stat_list:
    for i in range(classifier_num):
        # array of zeros to hold precision values
        classifier_stat_list.append(np.zeros([confidence_num, 3]))

    for i in range(confidence_num):  # add +1 to include full range
        conf = all_confidences[i]
        for j in range(classifier_num):
            cf_frame = cf_frames[j]
            precision = 0
            answered = \
                cf_frame[cf_frame[CONFIDENCE_COLUMN] >= conf].shape[0]
            if weight_mode == POPULATION_WEIGHT_MODE:
                correct = \
                    cf_frame[(cf_frame[INTENT_JUDGE_COLUMN] == 'yes')
                             & (cf_frame[CONFIDENCE_COLUMN] >= conf)].shape[0]
                precision = correct / answered
            else:
                intent_uttr_num_map = \
                  cf_frame[cf_frame[CONFIDENCE_COLUMN] >= conf] \
                  .groupby(PREDICTED_INTENT_COLUMN)[PREDICTED_INTENT_COLUMN] \
                  .count().to_dict()

                # Calulate precision use equal weights
                uttr_correct_intent = \
                    cf_frame[(cf_frame[INTENT_JUDGE_COLUMN] == 'yes')
                             & (cf_frame[CONFIDENCE_COLUMN] >= conf)] \
                    .groupby(GOLDEN_INTENT_COLUMN)[GOLDEN_INTENT_COLUMN] \
                    .count()

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
        mark = []
        indices_gtr_tau, = np.where(classifier_stat[:, 2] <= CONF_THRES)
        if len(indices_gtr_tau) > 0:
            tau_idx = indices_gtr_tau[0]
            mark = [tau_idx]

        line, = plt.plot(classifier_stat[:, 1], classifier_stat[:, 0],
                         color=next(line_color_cycler), label=labels[i],
                         linestyle=next(line_style_cycler),
                         markevery=mark, marker='o')
        lines.append(line)

    tau_desc = mpatches.Patch(color='white',
                              label='tau: {}'.format(CONF_THRES))
    ax.legend(handles=lines + [tau_desc], loc='upper right', shadow=False,
              prop={'size': LEGEND_AXIS_FONT_SIZE})
    ax.set_title(args.figure_title,
                 fontsize=TITLE_FONT_SIZE)
    # Save figure as file
    plt.savefig(args.outfile)


if __name__ == '__main__':
    PARSER = ArgumentParser(description="Draw precision curves on a single canvas \
                            from multiple classifiers' classification results")
    PARSER.add_argument('-i', '--classifiers_results', nargs='+',
                        required=True,
                        help='Files of results from individual classifiers')
    PARSER.add_argument('-n', '--classifier_names', nargs='*',
                        help='Names of each classifier')
    PARSER.add_argument('-t', '--figure_title', required=True, type=str,
                        help='Title of output figure')
    PARSER.add_argument('-o', '--outfile', help='File of the output figure',
                        default='figure.png', type=str)
    PARSER.add_argument('-w', '--weight', default='population', type=str,
                        help='Weight configuration for each intent')
    ARGS = PARSER.parse_args()
    func(ARGS)
