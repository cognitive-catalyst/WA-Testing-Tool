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
from argparse import ArgumentParser
from watson_developer_cloud import AssistantV1
from utils import WCS_VERSION, TRAIN_INTENT_FILENAME, TRAIN_ENTITY_FILENAME, \
                  WORKSPACE_BASE_FILENAME


def func(args):
    conv = AssistantV1(username=args.username, password=args.password,
                       version=WCS_VERSION)
    workspace = conv.get_workspace(workspace_id=args.workspace_id, export=True)
    intent_train_file = os.path.join(args.outdir, TRAIN_INTENT_FILENAME)
    entity_train_file = os.path.join(args.outdir, TRAIN_ENTITY_FILENAME)
    workspace_file = os.path.join(args.outdir, WORKSPACE_BASE_FILENAME)

    intent_exports = workspace['intents']
    entity_exports = workspace['entities']
    if len(intent_exports) == 0:
        raise ValueError("No intent is found in workspace")

    # Save workspace json
    with open(workspace_file, 'w+') as file:
        json.dump(workspace, file)

    # Parse intents to file
    with open(intent_train_file, 'w+') as csvfile:
        intent_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for intent_export in workspace['intents']:
            intent = intent_export['intent']
            if len(intent_export['examples']) == 0:
                intent_writer.writerow(['', intent])
            else:
                for example in intent_export['examples']:
                    intent_writer.writerow([example['text'], intent])

    if len(entity_exports) != 0:
        # Parse entities to file
        with open(entity_train_file, 'w+') as csvfile:
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
    parser.add_argument('-w', '--workspace_id', type=str, required=True,
                        help='Workspace ID')
    parser.add_argument('-u', '--username', type=str, required=True,
                        help='Assistant service username')
    parser.add_argument('-p', '--password', type=str, required=True,
                        help='Assistant service password')
    parser.add_argument('-o', '--outdir', type=str, help='Output directory',
                        default=os.getcwd())
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
