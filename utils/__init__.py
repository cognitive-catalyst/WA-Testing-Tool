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

import logging
import csv
import os
import pandas as pd
from watson_developer_cloud import AssistantV1

UTF_8 = 'utf-8'
TRAIN_FILENAME = 'train.csv'
TEST_FILENAME = 'test.csv'
TEST_OUT_FILENAME = 'test-out.csv'
TRAIN_INTENT_FILENAME = 'intent-train.csv'
TRAIN_ENTITY_FILENAME = 'entity-train.csv'

# CSV column names
INTENT_COLUMN = 'intent'
CONFIDENCE_COLUMN = 'confidence'
UTTERANCE_COLUMN = 'utterance'  # used in any intermediate file
INTENT_JUDGE_COLUMN = 'does intent match'
PREDICTED_INTENT_COLUMN = 'predicted intent'
DETECTED_ENTITY_COLUMN = 'detected entity'
DIALOG_RESPONSE_COLUMN = 'dialog response'
GOLDEN_INTENT_COLUMN = 'golden intent'
SCORE_COLUMN = 'score'

WCS_USERNAME_ITEM = 'username'
WCS_PASSWORD_ITEM = 'password'
WCS_CREDS_SECTION = 'ASSISTANT CREDENTIALS'

SPEC_FILENAME = 'workspace.json'
WORKSPACE_BASE_FILENAME = 'workspace_base.json'

root_path = os.path.abspath(os.path.dirname(__file__))
# Sub-script paths
CREATE_TEST_TRAIN_FOLDS_PATH = os.path.join(root_path,
                                            'createTestTrainFolds.py')
TRAIN_CONVERSATION_PATH = os.path.join(root_path,
                                       'trainConversation.py')
TEST_CONVERSATION_PATH = os.path.join(root_path,
                                      'testConversation.py')
CREATE_PRECISION_CURVE_PATH = os.path.join(root_path,
                                           'createPrecisionCurve.py')
WORKSPACE_PARSER_PATH = os.path.join(root_path,
                                     'workspaceParser.py')


# MODE
KFOLD = 'kfold'
BLIND_TEST = 'blind'
STANDARD_TEST = 'test'

FOLD_NUM_DEFAULT = 5
WCS_VERSION = '2018-02-16'
WORKSPACE_ID_TAG = 'workspace_id'
TIME_TO_WAIT = 600
BOOL_MAP = {True: 'yes', False: 'no'}
DEFAULT_TEST_RATE = 100
DEFAULT_CONF_THRES = 0.2

POPULATION_WEIGHT_MODE = 'population'
EQUAL_WEIGHT_MODE = 'equal'

# WA BASE_URL
BASE_URL = 'https://gateway.watsonplatform.net/assistant/api'


logger = logging.getLogger(__name__)


def configure_logger(level, format):
    """ Styling the logs in each module
    """
    logger.setLevel(level)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(format))
    logger.addHandler(h)


def save_dataframe_as_csv(df, file):
    """ Save dataframe as csv
    """
    return df.to_csv(file, encoding=UTF_8, quoting=csv.QUOTE_ALL,
                     index=False)


def marshall_entity(entities):
    """ Serialize RuntimeEntity list into formatted string
    """
    return ';'.join(['{}:{}'.format(entity['entity'], entity['value'])
                     for entity in entities])


def unmarshall_entity(entities_str):
    """ Deserialize entities string to RuntimeEntity list
    """
    entities = []
    for entity_str in entities_str.split(';'):
        splitted = entity_str.split(':')
        entities.append({'entity': splitted[0], 'value': splitted[0]})
    return entities


def delete_workspaces(username, password, workspace_ids):
    """ Delete workspaces
    """
    c = AssistantV1(username=username, password=password,
                    version=WCS_VERSION, url=BASE_URL)
    for workspace_id in workspace_ids:
        c.delete_workspace(workspace_id=workspace_id)
    print('Cleaned up workspaces')


def parse_partial_credit_table(file):
    df = pd.read_csv(file, quoting=csv.QUOTE_ALL,
                     encoding=UTF_8, keep_default_na=False)
    table = {}
    for _, row in df.iterrows():
        golden_intent = row['Golden Intent'].strip()
        if golden_intent not in table:
            table[golden_intent] = {}
        table[golden_intent][row['Partial Credit Intent'].strip()] = \
            float(row['Partial Credit Intent Score'])

    return table
