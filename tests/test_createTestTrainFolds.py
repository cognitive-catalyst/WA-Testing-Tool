import unittest
from test_base import CommandLineTestCase
import sys
import os
tool_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tool_base)
import createTestTrainFolds


class TestTrainTrainFoldsTestCase(CommandLineTestCase):
    def setUp(self):
        self.parser = createTestTrainFolds.create_parser()

    def test_with_empty_args(self):
        """ User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_sample_input(self):
        """ User passes correct args, should pass
        """
        raised = False
        args = \
            self.parser.parse_args(
                ['-i',
                 os.path.join(tool_base, 'resources', 'sample',
                              'intents.csv'),
                 '-o', self.test_dir, '-k', '5'])
        try:
            createTestTrainFolds.func(args)
        except Exception:
            raised = True
        self.assertFalse(raised, 'Exception raised')


if __name__ == '__main__':
    unittest.main()
