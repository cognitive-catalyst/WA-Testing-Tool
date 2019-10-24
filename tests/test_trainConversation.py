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
from utils import WCS_IAM_APIKEY_ITEM, WCS_CREDS_SECTION, \
                  TRAIN_CONVERSATION_PATH, SPEC_FILENAME, delete_workspaces, \
                  WORKSPACE_ID_TAG


class TrainConversationTestCase(CommandLineTestCase):
    def setUp(self):
        self.script_path = TRAIN_CONVERSATION_PATH

    def test_with_empty_args(self):
        """ User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            if subprocess.run([sys.executable,
                               self.script_path]).returncode != 0:
                raise SystemExit()

    def test_with_sample_input(self):
        """ User passes correct args, should pass
        """
        raised = False

        config_path = os.path.join(tool_base, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        apikey = config[WCS_CREDS_SECTION][WCS_IAM_APIKEY_ITEM]

        intent_path = os.path.join(tool_base, 'resources', 'sample',
                                   'intents.csv')
        entity_path = os.path.join(tool_base, 'resources', 'sample',
                                   'entities.csv')

        args = [sys.executable, TRAIN_CONVERSATION_PATH, '-i',
                intent_path, '-e', entity_path, '-a', apikey]

        workspace_spec_json = os.path.join(self.test_dir, SPEC_FILENAME)

        print('Begin training')
        returncode = 0
        with open(workspace_spec_json, 'w+') as f:
            returncode = subprocess.run(args, stdout=f).returncode

        try:
            with open(workspace_spec_json, 'r') as f:
                if returncode != 0:
                    print('Training failed')
                    print(f.read())
                    raise Exception()
                else:
                    print('Training complete')
                    workspace_id = json.load(f)[WORKSPACE_ID_TAG]
                    delete_workspaces(apikey, [workspace_id])

        except Exception as e:
            print(e)
            raised = True
        self.assertFalse(raised, 'Exception raised')


if __name__ == '__main__':
    unittest.main()
