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
from argparse import ArgumentParser
import aiohttp

from utils import UTF_8, CONFIDENCE_COLUMN, \
    UTTERANCE_COLUMN, PREDICTED_INTENT_COLUMN, \
    DETECTED_ENTITY_COLUMN, DIALOG_RESPONSE_COLUMN, \
    marshall_entity, save_dataframe_as_csv, INTENT_JUDGE_COLUMN, \
    TEST_OUT_FILENAME

test_out_header = [PREDICTED_INTENT_COLUMN, CONFIDENCE_COLUMN,
                   DETECTED_ENTITY_COLUMN, DIALOG_RESPONSE_COLUMN]


async def post(session, json, url, sem):
    """ Single post restrained by semaphore
    """
    async with sem:
        async with session.post(url, json=json) as response:
            return await response.json()


async def fill_df(utterance, row_idx, out_df, workspace_id, wa_username,
                  wa_password, sem):
    """ Send utterance to Assistant and save response to dataframe
    """
    async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(wa_username, wa_password)) as session:
        url = 'https://gateway.watsonplatform.net/assistant/api/v1/workspaces/{}/message?version=2018-02-16'.format(workspace_id)

        resp = await post(session, {'input': {'text': utterance}}, url, sem)
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

    # Applied coroutines
    sem = asyncio.Semaphore(args.rate_limit)
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(fill_df(out_df.loc[row_idx, test_column],
                                           row_idx, out_df, args.workspace_id,
                                           args.username, args.password,
                                           sem))
             for row_idx in range(out_df.shape[0])]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

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
        description='Test conversation instance using utterance')
    PARSER.add_argument('-i', '--infile', type=str, required=True,
                        help='File that contains test data')
    PARSER.add_argument('-o', '--outfile', type=str,
                        help='Output file path',
                        default=os.path.join(os.getcwd(), TEST_OUT_FILENAME))
    PARSER.add_argument('-w', '--workspace_id', type=str, required=True,
                        help='Workspace ID')
    PARSER.add_argument('-u', '--username', type=str, required=True,
                        help='Conversation service username')
    PARSER.add_argument('-p', '--password', type=str, required=True,
                        help='Conversation service password')
    PARSER.add_argument('-t', '--test_column', type=str,
                        help='Test column name in input file')
    PARSER.add_argument('-m', '--merge_input', action='store_true',
                        default=False,
                        help='Merge input content into test out')
    PARSER.add_argument('-g', '--golden_intent_column', type=str,
                        help='Golden column name in input file')
    PARSER.add_argument('-r', '--rate_limit', type=int, default=1,
                        help='Maximum number of requests per second')
    ARGS = PARSER.parse_args()
    func(ARGS)
