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
matplotlib.use('Agg') # Generate images without having a window appear
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from itertools import cycle
import pandas as pd
import csv

from utils import INTENT_JUDGE_COLUMN, UTF_8, CONFIDENCE_COLUMN

STEP = 0.01  # resolution for confidence intervals
nSteps = int(1 / STEP)

# total different number of line style len(line_styles) * len(line_color) = 12
line_styles = ['-', '--', '-.', ':']
line_color = ['b', 'g', 'r']

LEGEND_AXIS_FONT_SIZE = 14
TITLE_FONT_SIZE = 16


def func(args):
    """ Read classifiers results and draw the curves on one canvas for comparision

        Input Schema:
        | confidence       | does intent match |
        | confidence score | yes/no value      |
    """
    classifier_stat_list = []
    cf_frames = []

    # Initialization
    for i in range(len(args.classifiers_results)):
        file_path = args.classifiers_results[i]
        frame = pd.read_csv(file_path, encoding=UTF_8, quoting=csv.QUOTE_ALL)
        if INTENT_JUDGE_COLUMN not in frame.columns:  # Column validation
            raise ValueError("'{}' column not in {}".format(
                INTENT_JUDGE_COLUMN, file_path))
        # Read the cf files into list
        cf_frames.append(frame)
        # array of zeros to hold precision values
        classifier_stat_list.append(np.zeros([nSteps + 1, 3]))

    for i in range(0, nSteps + 1):  # add +1 to include full range
        conf = i * STEP
        for j in range(len(cf_frames)):
            cf_frame = cf_frames[j]
            correct = \
                cf_frame[(cf_frame[INTENT_JUDGE_COLUMN] == 'yes')
                         & (cf_frame[CONFIDENCE_COLUMN] >= conf)].shape[0]
            answered = cf_frame[cf_frame[CONFIDENCE_COLUMN] >= conf].shape[0]
            precision = correct / answered
            classifier_stat_list[j][i, 0] = precision
            classifier_stat_list[j][i, 1] = 100 * answered / len(cf_frame)
            classifier_stat_list[j][i, 2] = conf

    for precision in classifier_stat_list:
        precision = precision[::-1]  # reversing order for helpful plotting

    # plotting
    fig = plt.figure()
    ax = fig.gca()

    ax.grid(color='b', linestyle='--', alpha=0.3)
    ax.set_xlabel('Percentage of Questions Answered',
                  fontsize=LEGEND_AXIS_FONT_SIZE)
    ax.set_ylabel('Precision', fontsize=LEGEND_AXIS_FONT_SIZE)
    line_style_cycler = cycle(line_styles)
    line_color_cycler = cycle(line_color)

    # Prepare labels for each curve
    labels = [os.path.splitext(os.path.basename(file_path))[0]
              for file_path in args.classifiers_results]

    if args.classifier_names:
        labels = args.classifier_names

    # plot the curve and save the figure
    for i in range(len(classifier_stat_list)):
        classifier_stat = classifier_stat_list[i]
        plt.plot(classifier_stat[:, 1], classifier_stat[:, 0],
                 color=next(line_color_cycler),
                 linestyle=next(line_style_cycler), label=labels[i])

    # text box
    ax.legend(loc='upper right', shadow=False,
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
    PARSER.add_argument('-t', '--figure_title', required=True,
                        help='Title of output figure')
    PARSER.add_argument('-o', '--outfile', help="File of the output figure",
                        default='figure.png')
    ARGS = PARSER.parse_args()
    func(ARGS)
