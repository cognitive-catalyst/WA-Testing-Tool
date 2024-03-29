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

""" Test assistant instance using utterance
"""
import os
import csv
import asyncio
import pandas as pd
import json
from argparse import ArgumentParser
import aiohttp
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, BearerTokenAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import ClassificationsOptions
from ibm_watson.natural_language_understanding_v1 import Features

from choose_auth import choose_auth

from __init__ import UTF_8, CONFIDENCE_COLUMN, \
    UTTERANCE_COLUMN, PREDICTED_INTENT_COLUMN, \
    DETECTED_ENTITY_COLUMN, DIALOG_RESPONSE_COLUMN, \
    marshall_entity, save_dataframe_as_csv, INTENT_JUDGE_COLUMN, \
    TEST_OUT_FILENAME, BOOL_MAP, BASE_URL, DEFAULT_WA_VERSION, \
    parse_partial_credit_table, SCORE_COLUMN

test_out_header = [PREDICTED_INTENT_COLUMN, CONFIDENCE_COLUMN,
                   DETECTED_ENTITY_COLUMN, DIALOG_RESPONSE_COLUMN,
                   SCORE_COLUMN]

MAX_RETRY_LIMIT = 5


async def classify(service, workspace_id, utterance):
    response = service.analyze(
        features=Features(
            classifications=ClassificationsOptions(
                model=workspace_id
            )
        ),
        text=utterance,
        language='en')
    #print(json.dumps(response.get_result(), indent=2))
    return response.get_result()

async def post(service, workspace_id, utterance, sem):
    """ Single post restrained by semaphore
    """
    counter = 0
    async with sem:
        while True:
            try:
                res = await classify(service, workspace_id, utterance)
                return res
            except Exception as e:
                # Max retries reached, print out the response payload
                if counter == MAX_RETRY_LIMIT:
                    print(e)
                    raise e
                counter += 1
                print("RETRY")
                print(counter)

async def fill_df(utterance, row_idx, out_df, workspace_id, nlu, sem):
        """ Send utterance to Assistant and save response to dataframe
        """
#    async:
        # Replace newline chars before sending to WA
        utterance = utterance.replace('\n', ' ')
        resp = await post(nlu, workspace_id, utterance, sem)
        try:
            classes = resp['classifications']

            if len(classes) != 0:
                out_df.loc[row_idx, PREDICTED_INTENT_COLUMN] = \
                    classes[0]['class_name']
                out_df.loc[row_idx, CONFIDENCE_COLUMN] = \
                    classes[0]['confidence']

        except Exception as e:
            print(f"Error classifying {utterance}: ", e)

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
    #add .squeeze('columbs') to end of function call 
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

    # Applied coroutines
    sem = asyncio.Semaphore(args.rate_limit)
    loop = asyncio.get_event_loop()

    authenticator = choose_auth(args)

    nlu = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    ) 

    nlu.set_service_url(args.url)
    nlu.set_disable_ssl_verification(eval(args.disable_ssl))

    tasks = (fill_df(out_df.loc[row_idx, test_column],
                     row_idx, out_df, args.workspace_id, nlu,
                     sem)
             for row_idx in range(out_df.shape[0]))
    loop.run_until_complete(asyncio.gather(*tasks))

    loop.close()

    if args.golden_intent_column is not None:
        golden_intent_column = args.golden_intent_column
        if golden_intent_column not in in_df.columns:
            print("No golden intent column '{}' is found in input."
                  .format(golden_intent_column))
        else:  # Add INTENT_JUDGE_COLUMN based on golden_intent_column
            out_df[INTENT_JUDGE_COLUMN] = \
                (in_df[golden_intent_column]
                    == out_df[PREDICTED_INTENT_COLUMN]).map(BOOL_MAP)
            out_df[SCORE_COLUMN] = \
                out_df[INTENT_JUDGE_COLUMN].map({'yes': 1, 'no': 0})

    if args.partial_credit_table is not None:
        credit_tables = parse_partial_credit_table(args.partial_credit_table)
        for row_idx in range(out_df.shape[0]):
            golden_intent = out_df.loc[row_idx, args.golden_intent_column].strip()
            predict_intent = out_df.loc[row_idx, PREDICTED_INTENT_COLUMN].strip()
            if golden_intent == predict_intent:
                out_df.loc[row_idx, SCORE_COLUMN] = 1.0
            elif golden_intent not in credit_tables or \
               predict_intent not in credit_tables[golden_intent]:
                out_df.loc[row_idx, SCORE_COLUMN] = 0
            else:
                out_df.loc[row_idx, SCORE_COLUMN] = \
                    credit_tables[golden_intent][predict_intent]

    save_dataframe_as_csv(df=out_df, file=args.outfile)
    print("Wrote test result file to {}".format(args.outfile))


def create_parser():
    parser = ArgumentParser(
        description='Test NLU instance using utterance')
    parser.add_argument('-i', '--infile', type=str, required=True,
                        help='File that contains test data')
    parser.add_argument('-o', '--outfile', type=str,
                        help='Output file path',
                        default=os.path.join(os.getcwd(), TEST_OUT_FILENAME))
    parser.add_argument('-w', '--workspace_id', type=str, required=True,
                        help='Classifier ID')
    parser.add_argument('-a', '--iam_apikey', type=str, required=True,
                        help='NLU service IAM api key')
    parser.add_argument('-l', '--url', type=str, default='https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                        help='URL to Watson NLU. Ex: https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
    parser.add_argument('-t', '--test_column', type=str,
                        help='Test column name in input file')
    parser.add_argument('-m', '--merge_input', action='store_true',
                        default=False,
                        help='Merge input content into test out')
    parser.add_argument('-g', '--golden_intent_column', type=str,
                        help='Golden column name in input file')
    parser.add_argument('-r', '--rate_limit', type=int, default=1,
                        help='Maximum number of requests per second')
    parser.add_argument('-c', '--partial_credit_table', type=str,
                        help='Partial credit table')
    parser.add_argument('--auth-type', type=str, default='iam',
                        help='Authentication type, IAM is default, bearer is required for CP4D.', choices=['iam', 'bearer'])
    parser.add_argument('--disable_ssl', type=str, default="False",
                        help="Disables SSL verification. BE CAREFUL ENABLING THIS. Default is False", choices=["True", "False"])
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    #for arg in vars(ARGS):
    #    print("{} {}".format(arg, getattr(ARGS, arg)))
    func(ARGS)
