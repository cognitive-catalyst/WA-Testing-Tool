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

""" The script to flatten the dialog node in JSON to rows in CSV.
    Note:
      1. The intent column and entity column consist of values from dialog
        leaves up to the root so they don't match each other necessarily.
      2. 'State variables' corresponds to 'Context variables' in WA.
      3. Doesn't handle jumpto for now.
"""
import pandas as pd
import csv
import json
import re
from argparse import ArgumentParser

PARSER = ArgumentParser(
        description='Convert dialog node content JSON into CSV')
PARSER.add_argument('-i', '--workspace_json_dump_file', type=str,
                    required=True, help='WA workspace JSON dump')
PARSER.add_argument('-o', '--outfile', type=str, help='CSV output',
                    default='dialog-mapping.csv')

ARGS = PARSER.parse_args()

workspace_json_dump_file = ARGS.workspace_json_dump_file
dialog_mapping_file = ARGS.outfile


def get_intents_entities(curr_node, node_list):
    found_intents = []
    found_entities = []
    found_state_vars = []
    candidates = []
    if 'conditions' in curr_node and curr_node['conditions'] is not None:
        and_splitted = curr_node['conditions'].split('&&')
        for candidate in and_splitted:
            for or_splitted in candidate.strip().split('||'):
                candidates.append(or_splitted.strip())

        p = re.compile(r'\(|\)')

        # Parse intent or entity
        for candidate in candidates:
            if candidate[0] == '#':
                found_intents.append(candidate[1:])
            elif candidate[0] == '@':
                found_entities.append(p.sub('', candidate[1:]))
            elif candidate[0] == '{':
                found_state_vars.append(candidate)
            elif candidate[0] == '$':
                found_state_vars.append(candidate[1:])
            elif candidate == 'anything_else' or candidate == 'welcome':
                continue
            else:
                found_entities.append(candidate)

    # Get parent id
    if 'parent' not in curr_node or curr_node['parent'] is None:
        return found_intents, found_entities, found_state_vars
    else:
        for node in node_list:
            if node['dialog_node'] == curr_node['parent']:
                next_found_intents, next_found_entities, \
                    next_found_state_vars = \
                    get_intents_entities(node, node_list)
                return found_intents + next_found_intents, found_entities + \
                    next_found_entities, found_state_vars + \
                    next_found_state_vars


df = pd.DataFrame(columns=['intent', 'Entity formated',
                           'SME answer to use', 'State variables'])

with open(workspace_json_dump_file, 'r') as f:
    workspace = json.load(f)
    dialog_nodes = workspace['dialog_nodes']
    for node in dialog_nodes:
        if ('output' in node) and (node['output'] is not None) and \
           ('text' in node['output']) and \
           (node['output']['text'] is not None) and \
           ('values' in node['output']['text']):
            answers = node['output']['text']['values']
            if len(answers) != 0:
                # Parse conditions
                found_intents, found_entities, found_state_vars = \
                    get_intents_entities(node, dialog_nodes)

                found_intents = list(set(found_intents))  # deduplicate

                # ignore no intent/entity entry
                if not found_intents and not found_entities:
                    continue

                for answer in answers:
                    df = df.append(
                        {'intent': ' || '.join(found_intents),
                         'Entity formated': ';'.join(found_entities),
                         'SME answer to use': answer,
                         'State variables': ' '.join(found_state_vars)},
                        ignore_index=True)

df.to_csv(dialog_mapping_file, encoding='utf-8', quoting=csv.QUOTE_ALL,
          index=False)
