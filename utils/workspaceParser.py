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

""" Parse workspace into artifacts for training
"""
import os
import csv
import json
import os.path
from argparse import ArgumentParser
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from __init__ import TRAIN_INTENT_FILENAME, DEFAULT_WA_VERSION, \
                     TRAIN_ENTITY_FILENAME, WORKSPACE_BASE_FILENAME, UTF_8


def func(args):
    workspace = None
    if not os.path.isfile(args.input):
        authenticator = IAMAuthenticator(args.iam_apikey)
        conv = AssistantV1(
            version=args.version,
            authenticator=authenticator
        )
        conv.set_service_url(args.url)

        raw_workspace = conv.get_workspace(workspace_id=args.input, export=True)
        try:
           #V2 API syntax
           workspace = raw_workspace.get_result()
        except:
           #V1 API syntax
           workspace = raw_workspace
    else:
        with open(args.input) as f:
            workspace = json.load(f)

    intent_train_file = os.path.join(args.outdir, TRAIN_INTENT_FILENAME)
    entity_train_file = os.path.join(args.outdir, TRAIN_ENTITY_FILENAME)
    workspace_file = os.path.join(args.outdir, WORKSPACE_BASE_FILENAME)

    intent_exports = workspace['intents']
    entity_exports = workspace['entities']
    if len(intent_exports) == 0:
        raise ValueError("No intent is found in workspace")

    # Save workspace json
    with open(workspace_file, 'w+', encoding=UTF_8) as file:
        json.dump(workspace, file)

    # Parse intents to file
    with open(intent_train_file, 'w+', encoding=UTF_8) as csvfile:
        intent_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for intent_export in workspace['intents']:
            intent = intent_export['intent']
            if len(intent_export['examples']) != 0:
                for example in intent_export['examples']:
                    intent_writer.writerow([example['text'], intent])

    if len(entity_exports) != 0:
        # Parse entities to file
        with open(entity_train_file, 'w+', encoding=UTF_8) as csvfile:
            entity_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for entity_export in workspace['entities']:
                entity = entity_export['entity']
                for value_export in entity_export['values']:
                    row = [entity, value_export['value']]
                    if 'synonyms' in value_export:
                        row += value_export['synonyms']
                    elif 'patterns' in value_export:
                        row += ['/{}/'.format(pattern)
                                for pattern in value_export['patterns']
                                ]
                    entity_writer.writerow(row)


def create_parser():
    parser = ArgumentParser(
        description="Parse workspace into artifacts for training")
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Workspace ID or path of workspace JSON')
    parser.add_argument('-a', '--iam_apikey', type=str, required=True,
                        help='Assistant service iam api key')
    parser.add_argument('-l', '--url', type=str, default='https://gateway.watsonplatform.net/assistant/api',
                        help='URL to Watson Assistant. Ex: https://gateway-wdc.watsonplatform.net/assistant/api')
    parser.add_argument('-o', '--outdir', type=str, help='Output directory',
                        default=os.getcwd())
    parser.add_argument('-v', '--version', type=str, default=DEFAULT_WA_VERSION,
                        help='Watson Assistant API version in YYYY-MM-DD form')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
