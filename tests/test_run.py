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

import unittest
from test_base import CommandLineTestCase
import sys
import configparser
import subprocess
import json
import os
tool_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tool_base)
from utils import FOLD_NUM_DEFAULT, KFOLD, BLIND_TEST, STANDARD_TEST, \
                  TRAIN_CONVERSATION_PATH, WCS_CREDS_SECTION, \
                  WCS_IAM_APIKEY_ITEM, \
                  WORKSPACE_ID_TAG, SPEC_FILENAME, BOOL_MAP, \
                  delete_workspaces, WCS_BASEURL_ITEM

from run import WORKSPACE_ID_ITEM, MODE_ITEM, DEFAULT_SECTION, \
                DO_KEEP_WORKSPACE_ITEM, TEMP_DIR_ITEM, FIGURE_PATH_ITEM, \
                FOLD_NUM_ITEM, PREVIOUS_BLIND_OUT_ITEM, TEST_FILE_ITEM, \
                TEST_OUT_PATH_ITEM, PARTIAL_CREDIT_TABLE_ITEM


class RunTestCase(CommandLineTestCase):
    def setUp(self):
        self.script_path = os.path.join(tool_base, 'run.py')
        self.train_path = TRAIN_CONVERSATION_PATH

        config_path = os.path.join(tool_base, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        config[DEFAULT_SECTION][DO_KEEP_WORKSPACE_ITEM] = BOOL_MAP[False]

        self.config = config

    def test_with_empty_args(self):
        """ User passes no args, should fail with SystemExit
        """
        print('=======================================================================')
        print('test_with_empty_args - User passes no args, should fail with SystemExit')
        print('=======================================================================')

        with self.assertRaises(SystemExit):
            if subprocess.run([sys.executable,
                               self.script_path]).returncode != 0:
                raise SystemExit()

    def test_kfold(self):
        """ User passes correct kfold config, should pass
        """
        print('=============================================')
        print('test_kfold - Executes KFOLD tests with run.py')
        print('=============================================')

        raised = False

        kfold_test_dir = os.path.join(self.test_dir, KFOLD)
        if not os.path.exists(kfold_test_dir):
            os.makedirs(kfold_test_dir)

        intent_path = os.path.join(tool_base, 'resources', 'sample',
                                   'intents.csv')
        entity_path = os.path.join(tool_base, 'resources', 'sample',
                                   'entities.csv')

        apikey = self.config[WCS_CREDS_SECTION][WCS_IAM_APIKEY_ITEM]

        args = [sys.executable, TRAIN_CONVERSATION_PATH, '-i', intent_path,
                '-e', entity_path, '-a', apikey, '-n', 'KFOLD_TEST_RUN', '-l', self.config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM]]

        workspace_spec_json = os.path.join(self.test_dir, SPEC_FILENAME)
        # Train a new instance in order to pull the workspace detail
        print('Begin training for setting up environment')
        with open(workspace_spec_json, 'w+') as f:
            if subprocess.run(args, stdout=f).returncode != 0:
                print('Training failed')
                print(f.read())
                raise Exception()

        with open(workspace_spec_json, 'r') as f:
            self.config[DEFAULT_SECTION][WORKSPACE_ID_ITEM] = json.load(f)[WORKSPACE_ID_TAG]

        self.config[DEFAULT_SECTION][MODE_ITEM] = KFOLD
        self.config[DEFAULT_SECTION][TEMP_DIR_ITEM] = kfold_test_dir
        self.config[DEFAULT_SECTION][FIGURE_PATH_ITEM] = \
            os.path.join(kfold_test_dir, 'figure.png')
        self.config[DEFAULT_SECTION][FOLD_NUM_ITEM] = str(FOLD_NUM_DEFAULT)
        self.config[DEFAULT_SECTION][PARTIAL_CREDIT_TABLE_ITEM] = \
            os.path.join(tool_base, 'resources', 'sample',
                         'partial-credit-table.csv')

        kfold_config_path = os.path.join(kfold_test_dir, 'config.ini')

        with open(kfold_config_path, 'w') as configfile:
            self.config.write(configfile)

        args = [sys.executable, self.script_path, '-c', kfold_config_path]

        if subprocess.run(args).returncode != 0:
            raised = True

        workspace_ids = []
        workspace_ids.append(self.config[DEFAULT_SECTION][WORKSPACE_ID_ITEM])

        delete_workspaces(apikey,self.config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM], '2019-02-28',workspace_ids)

        self.assertFalse(raised, 'Exception raised')

    def test_blind(self):
        """ User passes correct blind config, should pass
        """
        print('=============================================')
        print('test_blind - Executes BLIND tests with run.py')
        print('=============================================')

        raised = False

        blind_test_dir = os.path.join(self.test_dir, BLIND_TEST)
        if not os.path.exists(blind_test_dir):
            os.makedirs(blind_test_dir)

        # Use fold 0 training input as intent
        intent_path = os.path.join(tool_base, 'resources', 'sample', 'kfold',
                                   '0', 'train.csv')
        entity_path = os.path.join(tool_base, 'resources', 'sample',
                                   'entities.csv')

        test_input_path = os.path.join(tool_base, 'resources', 'sample',
                                       'kfold', '0', 'test.csv')
        # Use fold 1 test output as previous blind out
        previous_blind_out_path = os.path.join(tool_base, 'resources',
                                               'sample', 'kfold', '1',
                                               'test-out.csv')

        apikey = self.config[WCS_CREDS_SECTION][WCS_IAM_APIKEY_ITEM]

        args = [sys.executable, TRAIN_CONVERSATION_PATH, '-i', intent_path,
                '-e', entity_path, '-a', apikey, '-n', 'BLIND_TEST_RUN', '-l', self.config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM]]

        workspace_spec_json = os.path.join(self.test_dir, SPEC_FILENAME)
        # Train a new instance in order to pull the workspace detail
        print('Begin training for setting up environment')
        with open(workspace_spec_json, 'w+') as f:
            if subprocess.run(args, stdout=f).returncode != 0:
                print('Training failed')
                print(f.read())
                raise Exception()

        with open(workspace_spec_json, 'r') as f:
            self.config[DEFAULT_SECTION][WORKSPACE_ID_ITEM] = \
                json.load(f)[WORKSPACE_ID_TAG]

        self.config[DEFAULT_SECTION][MODE_ITEM] = BLIND_TEST
        self.config[DEFAULT_SECTION][TEMP_DIR_ITEM] = blind_test_dir
        self.config[DEFAULT_SECTION][FIGURE_PATH_ITEM] = \
            os.path.join(blind_test_dir, 'figure.png')
        self.config[DEFAULT_SECTION][PREVIOUS_BLIND_OUT_ITEM] = \
            previous_blind_out_path
        self.config[DEFAULT_SECTION][TEST_FILE_ITEM] = test_input_path
        self.config[DEFAULT_SECTION][TEST_OUT_PATH_ITEM] = \
            os.path.join(blind_test_dir, 'test-out.csv')
        self.config[DEFAULT_SECTION][PARTIAL_CREDIT_TABLE_ITEM] = \
            os.path.join(tool_base, 'resources', 'sample',
                         'partial-credit-table.csv')

        blind_config_path = os.path.join(blind_test_dir, 'config.ini')

        with open(blind_config_path, 'w') as configfile:
            self.config.write(configfile)

        args = [sys.executable, self.script_path, '-c', blind_config_path]

        if subprocess.run(args).returncode != 0:
            raised = True

        workspace_ids = []
        workspace_ids.append(self.config[DEFAULT_SECTION][WORKSPACE_ID_ITEM])

        delete_workspaces(apikey,self.config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM],'2019-02-28',workspace_ids)

        self.assertFalse(raised, 'Exception raised')

    def test_std(self):
        """ User passes correct standard test config, should pass
        """
        print('==============================================')
        print('test_std - Executes Standard tests with run.py')
        print('==============================================')

        raised = False

        std_test_dir = os.path.join(self.test_dir, STANDARD_TEST)
        if not os.path.exists(std_test_dir):
            os.makedirs(std_test_dir)

        # Use fold 0 training input as intent
        intent_path = os.path.join(tool_base, 'resources', 'sample', 'kfold',
                                   '0', 'train.csv')
        entity_path = os.path.join(tool_base, 'resources', 'sample',
                                   'entities.csv')

        apikey = self.config[WCS_CREDS_SECTION][WCS_IAM_APIKEY_ITEM]

        args = [sys.executable, TRAIN_CONVERSATION_PATH, '-i', intent_path,
                '-e', entity_path, '-a', apikey, '-n', 'STD_TEST_RUN', '-l', self.config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM]]

        workspace_spec_json = os.path.join(self.test_dir, SPEC_FILENAME)
        # Train a new instance in order to pull the workspace detail
        print('Begin training for setting up environment')
        with open(workspace_spec_json, 'w+') as f:
            if subprocess.run(args, stdout=f).returncode != 0:
                print('Training failed')
                print(f.read())
                raise Exception()

        with open(workspace_spec_json, 'r') as f:
            self.config[DEFAULT_SECTION][WORKSPACE_ID_ITEM] = \
                json.load(f)[WORKSPACE_ID_TAG]

        test_input_path = os.path.join(tool_base, 'resources', 'sample',
                                       'kfold', '0', 'test.csv')

        self.config[DEFAULT_SECTION][MODE_ITEM] = STANDARD_TEST
        self.config[DEFAULT_SECTION][TEMP_DIR_ITEM] = std_test_dir
        self.config[DEFAULT_SECTION][TEST_FILE_ITEM] = test_input_path
        self.config[DEFAULT_SECTION][TEST_OUT_PATH_ITEM] = \
            os.path.join(std_test_dir, 'test-out.csv')

        std_config_path = os.path.join(std_test_dir, 'config.ini')

        with open(std_config_path, 'w') as configfile:
            self.config.write(configfile)

        args = [sys.executable, self.script_path, '-c', std_config_path]

        if subprocess.run(args).returncode != 0:
            raised = True

        workspace_ids = []
        workspace_ids.append(self.config[DEFAULT_SECTION][WORKSPACE_ID_ITEM])

        delete_workspaces(apikey,self.config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM], '2019-02-28', workspace_ids)

        self.assertFalse(raised, 'Exception raised')


if __name__ == '__main__':
    unittest.main()
