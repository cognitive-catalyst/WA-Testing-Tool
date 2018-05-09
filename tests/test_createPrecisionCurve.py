import unittest
from test_base import CommandLineTestCase
import sys
import os
tool_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tool_base)
import createPrecisionCurve
from utils import CREATE_PRECISION_CURVE_PATH, FOLD_NUM_DEFAULT


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
