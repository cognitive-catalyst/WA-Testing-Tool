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
from ibm_watson import AssistantV1, AssistantV2

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
g_tested_utterances = 0

async def message(service, workspace_id, utterance, apiversion):
    # Include user_id in request body for Plus and Premium plans
    if apiversion == 'v1':
        response = service.message(
            workspace_id=workspace_id,
            input={
                'text': utterance,
                'alternate_intents': True
            },
            context={
                'metadata': {
                    'user_id': 'test'
                }
            })
    else:
        response = service.message_stateless(
            assistant_id=workspace_id,
            input={
                'message_type': 'text',
                'text': utterance,
                'options': {
                    'alternate_intents': True
                }
            },
            context={
                'metadata': {
                    'user_id': 'test'
                }
            })

    global g_tested_utterances
    g_tested_utterances += 1
    if g_tested_utterances % 10 == 0:
        print("Tested",g_tested_utterances, "utterances...")
        
    return response.get_result()

async def post(service, workspace_id, utterance, apiversion, sem):
    """ Single post restrained by semaphore
    """
    counter = 0
    async with sem:
        while True:
            try:
                res = await message(service, workspace_id, utterance, apiversion)
                return res
            except Exception as e:
                # Max retries reached, print out the response payload
                if counter == MAX_RETRY_LIMIT:
                    print(e)
                    raise e
                counter += 1
                print(f"RETRY {counter}")

async def fill_df(utterance, row_idx, out_df, workspace_id, conversation, apiversion, sem):
        """ Send utterance to Assistant and save response to dataframe
        """
#    async:
        # Replace newline chars before sending to WA
        utterance = utterance.replace('\n', ' ')
        resp = await post(conversation, workspace_id, utterance, apiversion, sem)
        try:
            if 'intents' in resp:
                intents = resp['intents']
            if 'output' in resp and 'intents' in resp['output']:
                intents = resp['output']['intents']

            if len(intents) != 0:
                out_df.loc[row_idx, PREDICTED_INTENT_COLUMN] = \
                    intents[0]['intent']
                out_df.loc[row_idx, CONFIDENCE_COLUMN] = \
                    intents[0]['confidence']

            if 'entities' in resp:
                out_df.loc[row_idx, DETECTED_ENTITY_COLUMN] = \
                    marshall_entity(resp['entities'])
            if 'output' in resp and 'entities' in resp['output']:
                out_df.loc[row_idx, DETECTED_ENTITY_COLUMN] = \
                    marshall_entity(resp['output']['entities'])

            response_text = ''
            response_text_list = []
            if 'text' in resp['output']:
                response_text_list = resp['output']['text']
            elif 'generic' in resp['output'] and len(resp['output']['generic']) != 0 and 'text' in resp['output']['generic'][0]:
                response_text_list = [ resp['output']['generic'][0]['text'] ]
            #Auto-disambiguation (suggestions)
            elif 'generic' in resp['output'] and len(resp['output']['generic']) != 0 and 'title' in resp['output']['generic'][0]:
                response_text_list = resp['output']['generic'][0]['title']
                suggestions = resp['output']['generic'][0]['suggestions']
                for suggestion in suggestions:
                    response_text_list += " " + suggestion ['label']
            else:
                pass
            
            if len(response_text_list) != 0:
                response_text_list = [text for text in response_text_list if type(text) == str]
                response_text = ' '.join(response_text_list)

            out_df.loc[row_idx, DIALOG_RESPONSE_COLUMN] = response_text

        except Exception as e:
            print("analysis error",e)

async def gather_all_tasks(tasks):
    task_set = await asyncio.gather(*tasks)
    return task_set

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

    authenticator = choose_auth(args)

    if(args.apiversion.lower() == 'v1'):
        conv = AssistantV1(
            version=args.version,
            authenticator=authenticator
        )
    else:
        conv = AssistantV2(
            version=args.version,
            authenticator=authenticator
        )
    conv.set_disable_ssl_verification(eval(args.disable_ssl))
    conv.set_service_url(args.url)

    tasks = (fill_df(out_df.loc[row_idx, test_column],
                     row_idx, out_df, args.workspace_id, conv,
                     args.apiversion.lower(),
                     sem)
             for row_idx in range(out_df.shape[0]))
    print("Testing",len(out_df),"utterances...")
    asyncio.run(gather_all_tasks(tasks))

    print("Aggregating output...")
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
    print("Wrote result file to {}".format(args.outfile))


def create_parser():
    parser = ArgumentParser(
        description='Test conversation instance using utterance')
    parser.add_argument('-i', '--infile', type=str, required=True,
                        help='File that contains test data')
    parser.add_argument('-o', '--outfile', type=str,
                        help='Output file path',
                        default=os.path.join(os.getcwd(), TEST_OUT_FILENAME))
    parser.add_argument('-p', '--apiversion', type=str,
                        help='Watson Assistant API version ("v1" or "v2")', default='v1')
    parser.add_argument('-w', '--workspace_id', type=str, required=True,
                        help='Workspace ID (v1) or Assistant Environment ID (v2)')
    parser.add_argument('-a', '--iam_apikey', type=str, required=True,
                        help='Assistant service IAM api key')
    parser.add_argument('-l', '--url', type=str, default='https://gateway.watsonplatform.net/assistant/api',
                        help='URL to Watson Assistant. Ex: https://gateway-wdc.watsonplatform.net/assistant/api')
    parser.add_argument('-t', '--test_column', type=str,
                        help='Test column name in input file')
    parser.add_argument('-m', '--merge_input', action='store_true',
                        default=True,
                        help='Merge input content into test out')
    parser.add_argument('-g', '--golden_intent_column', type=str,
                        help='Golden column name in input file')
    parser.add_argument('-r', '--rate_limit', type=int, default=1,
                        help='Maximum number of requests per second')
    parser.add_argument('-c', '--partial_credit_table', type=str,
                        help='Partial credit table')
    parser.add_argument('-v', '--version', type=str, default=DEFAULT_WA_VERSION,
                        help='Watson Assistant API version in YYYY-MM-DD form')
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
