#! /usr/bin/python
""" Test assistant instance using utterance
"""
import os
import csv
import pandas as pd
from argparse import ArgumentParser
from watson_developer_cloud import AssistantV1

from utils import UTF_8, WCS_VERSION, CONFIDENCE_COLUMN, \
    UTTERANCE_COLUMN, PREDICTED_INTENT_COLUMN, \
    DETECTED_ENTITY_COLUMN, DIALOG_RESPONSE_COLUMN, \
    marshall_entity, save_dataframe_as_csv, INTENT_JUDGE_COLUMN, \
    TEST_OUT_FILENAME

test_out_header = [PREDICTED_INTENT_COLUMN, CONFIDENCE_COLUMN,
                   DETECTED_ENTITY_COLUMN, DIALOG_RESPONSE_COLUMN]


def func(args):
    in_df = None
    out_df = None
    test_column = UTTERANCE_COLUMN
    if args.test_column is not None:  # Test input has multiple columns
        test_column = args.test_column
        in_df = pd.read_csv(args.infile, quoting=csv.QUOTE_ALL,
                            encoding=UTF_8, keep_default_na=False)
        if test_column not in in_df:  # Look for target test_column
            raise ValueError(
                "Test column {} doesn't exist in file.".format(test_column))

        if args.merge_input:  # Merge rest of columns from input to output
            out_df = in_df
        else:
            out_df = in_df[[test_column]].copy()
            out_df.columns = [test_column]

    else:
        test_series = pd.read_csv(args.infile, quoting=csv.QUOTE_ALL,
                                  encoding=UTF_8, header=None, squeeze=True,
                                  keep_default_na=False)
        if isinstance(test_series, pd.DataFrame):
            raise ValueError('Unknown test column')
        # Test input has only one column and no header
        out_df = test_series.to_frame()
        out_df.columns = [test_column]

    # Initial columns for test output
    for column in test_out_header:
        out_df[column] = ''

    conv = AssistantV1(username=args.username, password=args.password,
                       version=WCS_VERSION)

    for row_idx in range(out_df.shape[0]):
        utterance = out_df.loc[row_idx, test_column]
        resp = conv.message(workspace_id=args.workspace_id,
                            input={'text': utterance},
                            alternate_intents=True)
        intents = resp['intents']
        if len(intents) != 0:
            out_df.loc[row_idx, PREDICTED_INTENT_COLUMN] = \
                intents[0]['intent']
            out_df.loc[row_idx, CONFIDENCE_COLUMN] = \
                intents[0]['confidence']

        out_df.loc[row_idx, DETECTED_ENTITY_COLUMN] = \
            marshall_entity(resp['entities'])

        response_text = ''
        response_text_list = resp['output']['text']
        if len(response_text_list) != 0:
            response_text = response_text_list.pop()
        out_df.loc[row_idx, DIALOG_RESPONSE_COLUMN] = response_text

    if args.golden_intent_column is not None:
        golden_intent_column = args.golden_intent_column
        if golden_intent_column not in in_df.columns:
            print("No golden intent column '{}' is found in input."
                  .format(golden_intent_column))
        else:  # Add INTENT_JUDGE_COLUMN based on golden_intent_column
            bool_map = {True: 'yes', False: 'no'}
            out_df[INTENT_JUDGE_COLUMN] = \
                (in_df[golden_intent_column]
                    == out_df[PREDICTED_INTENT_COLUMN]).map(bool_map)

    save_dataframe_as_csv(df=out_df, file=args.outfile)


if __name__ == '__main__':
    PARSER = ArgumentParser(
        description='Test assistant instance using utterance')
    PARSER.add_argument('-i', '--infile', type=str, required=True,
                        help='File that contains test data')
    PARSER.add_argument('-o', '--outfile', type=str,
                        help='Output file path',
                        default=os.path.join(os.getcwd(), TEST_OUT_FILENAME))
    PARSER.add_argument('-w', '--workspace_id', type=str, required=True,
                        help='Workspace ID')
    PARSER.add_argument('-u', '--username', type=str, required=True,
                        help='Assistant service username')
    PARSER.add_argument('-p', '--password', type=str, required=True,
                        help='Assistant service password')
    PARSER.add_argument('-t', '--test_column', type=str,
                        help='Test column name in input file')
    PARSER.add_argument('-m', '--merge_input', action='store_true',
                        default=False,
                        help='Merge input content into test out')
    PARSER.add_argument('-g', '--golden_intent_column', type=str,
                        help='Golden column name in input file')
    ARGS = PARSER.parse_args()
    func(ARGS)
