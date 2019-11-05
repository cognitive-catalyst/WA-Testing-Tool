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
import os
tool_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tool_base)
from utils import FOLD_NUM_DEFAULT

sys.path.append("utils")
import createPrecisionCurve


class CreatePrecisionCurveTestCase(CommandLineTestCase):
    def setUp(self):
        self.parser = createPrecisionCurve.create_parser()

    def test_with_empty_args(self):
        """ User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_sample_input(self):
        """ User passes correct args, should pass
        """
        raised = False
        test_out_paths = \
            [os.path.join(tool_base, 'resources',
                          'sample', 'kfold', str(idx),
                          'test-out.csv') for idx in range(FOLD_NUM_DEFAULT)]
        classifier_names = \
            ['Classfier {}'.format(idx) for idx in range(FOLD_NUM_DEFAULT)]

        fig_path = os.path.join(self.test_dir, 'figure.png')

        args = \
            self.parser.parse_args(['-t', 'test title', '-o', fig_path] +
                                   ['-n'] + classifier_names +
                                   ['-i'] + test_out_paths)

        try:
            createPrecisionCurve.func(args)
        except Exception as e:
            print(e)
            raised = True
        self.assertFalse(raised, 'Exception raised')


if __name__ == '__main__':
    unittest.main()
