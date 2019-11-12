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
import configparser
import subprocess
import sys
import json
import os
tool_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tool_base)
from utils import WCS_CREDS_SECTION, SPEC_FILENAME, \
                  WCS_IAM_APIKEY_ITEM, TRAIN_CONVERSATION_PATH, \
                  delete_workspaces, WORKSPACE_ID_TAG, DEFAULT_WA_VERSION, \
                  WCS_BASEURL_ITEM

sys.path.append("utils")
import workspaceParser

class WorkspaceParserTestCase(CommandLineTestCase):
    def setUp(self):
        self.parser = workspaceParser.create_parser()

    def test_with_empty_args(self):
        """ User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_sample_input(self):
        """ User passes correct args, should pass
        """
        raised = False

        intent_path = os.path.join(tool_base, 'resources', 'sample',
                                   'intents.csv')
        entity_path = os.path.join(tool_base, 'resources', 'sample',
                                   'entities.csv')
        # #output_path = os.path.join(tool_base, 'data')
        #
        config_path = os.path.join(tool_base, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        #
        apikey = config[WCS_CREDS_SECTION][WCS_IAM_APIKEY_ITEM]
        #
        # args = [sys.executable, TRAIN_CONVERSATION_PATH, '-i', intent_path,
        #         '-e', entity_path, '-a', apikey, '-v', DEFAULT_WA_VERSION,
        #         '-l', config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM]]
        #
        workspace_spec_json = os.path.join(tool_base, 'data', 'workspace_parser_test.json.sample')
        # # Train a new instance in order to pull the workspace detail
        # print('Begin training for setting up environment')
        # with open(workspace_spec_json, 'w+') as f:
        #     if subprocess.run(args, stdout=f).returncode != 0:
        #         print('Training failed')
        #         print(f.read())
        #         raise Exception()

        workspace_id = None
        with open(workspace_spec_json, 'r') as f:
            workspace_id = \
                json.load(f)[WORKSPACE_ID_TAG]

        args = \
            self.parser.parse_args(
                ['-a', apikey, '-i', workspace_spec_json, '-v', DEFAULT_WA_VERSION,
                 '-o', self.test_dir, '-l', config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM]])
        try:
            workspaceParser.func(args)
        except Exception as e:
            print(e)
            raised = True

        # workspace_ids = []
        # workspace_ids.append(workspace_id)
        # delete_workspaces(apikey,config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM], '2019-02-28', workspace_ids)

        self.assertFalse(raised, 'Exception raised')


if __name__ == '__main__':
    unittest.main()
