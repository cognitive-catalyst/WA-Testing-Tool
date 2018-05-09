import unittest
from test_base import CommandLineTestCase
import sys
import configparser
import subprocess
import os
tool_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, tool_base)
from utils import FOLD_NUM_DEFAULT, KFOLD, BLIND_TEST, STANDARD_TEST


class RunTestCase(CommandLineTestCase):
    def setUp(self):
        self.script_path = os.path.join(tool_base, 'run.py')
        self.intent_path = os.path.join(tool_base, 'resources', 'sample',
                                        'intents.csv')
        self.entity_path = os.path.join(tool_base, 'resources', 'sample',
                                        'entities.csv')

    def test_with_empty_args(self):
        """ User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            if subprocess.run([sys.executable,
                               self.script_path]).returncode != 0:
                raise SystemExit()

    def test_kfold(self):
        """ User passes correct kfold config, should pass
        """
        raised = False

        kfold_test_dir = os.path.join(self.test_dir, KFOLD)
        if not os.path.exists(kfold_test_dir):
            os.makedirs(kfold_test_dir)

        config_path = os.path.join(tool_base, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        config['DEFAULT'] = {
            'mode': KFOLD,
            'intent_train_file': self.intent_path,
            'entity_train_file': self.entity_path,
            'temporary_file_directory': kfold_test_dir,
            'out_figure_path': os.path.join(kfold_test_dir, 'figure.png'),
            'fold_num': FOLD_NUM_DEFAULT,
            'keep_workspace_after_test': 'no'
        }

        kfold_config_path = os.path.join(kfold_test_dir, 'config.ini')

        with open(kfold_config_path, 'w') as configfile:
            config.write(configfile)

        args = [sys.executable, self.script_path, '-c', kfold_config_path]

        if subprocess.run(args).returncode != 0:
            raised = True

        self.assertFalse(raised, 'Exception raised')

    def test_blind(self):
        """ User passes correct blind config, should pass
        """
        raised = False

        blind_test_dir = os.path.join(self.test_dir, BLIND_TEST)
        if not os.path.exists(blind_test_dir):
            os.makedirs(blind_test_dir)

        config_path = os.path.join(tool_base, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        # Use fold 0 training input as intent
        intent_path = os.path.join(tool_base, 'resources', 'sample', 'kfold',
                                   '0', 'train.csv')

        test_input_path = os.path.join(tool_base, 'resources', 'sample',
                                       'kfold', '0', 'test.csv')
        # Use fold 1 test output as previous blind out
        previous_blind_out_path = os.path.join(tool_base, 'resources',
                                               'sample', 'kfold', '1',
                                               'test-out.csv')
        config['DEFAULT'] = {
            'mode': BLIND_TEST,
            'intent_train_file': intent_path,
            'entity_train_file': self.entity_path,
            'test_input_file': test_input_path,
            'previous_blind_out': previous_blind_out_path,
            'test_output_path': os.path.join(blind_test_dir, 'test-out.csv'),
            'temporary_file_directory': blind_test_dir,
            'out_figure_path': os.path.join(blind_test_dir, 'figure.png'),
            'keep_workspace_after_test': 'no'
        }

        blind_config_path = os.path.join(blind_test_dir, 'config.ini')

        with open(blind_config_path, 'w') as configfile:
            config.write(configfile)

        args = [sys.executable, self.script_path, '-c', blind_config_path]

        if subprocess.run(args).returncode != 0:
            raised = True

        self.assertFalse(raised, 'Exception raised')

    def test_std(self):
        """ User passes correct standard test config, should pass
        """
        raised = False

        std_test_dir = os.path.join(self.test_dir, STANDARD_TEST)
        if not os.path.exists(std_test_dir):
            os.makedirs(std_test_dir)

        config_path = os.path.join(tool_base, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        # Use fold 0 training input as intent
        intent_path = os.path.join(tool_base, 'resources', 'sample', 'kfold',
                                   '0', 'train.csv')

        test_input_path = os.path.join(tool_base, 'resources', 'sample',
                                       'kfold', '0', 'test.csv')

        config['DEFAULT'] = {
            'mode': STANDARD_TEST,
            'intent_train_file': intent_path,
            'entity_train_file': self.entity_path,
            'test_input_file': test_input_path,
            'test_output_path': os.path.join(std_test_dir, 'test-out.csv'),
            'temporary_file_directory': std_test_dir,
            'keep_workspace_after_test': 'no'
        }

        std_config_path = os.path.join(std_test_dir, 'config.ini')

        with open(std_config_path, 'w') as configfile:
            config.write(configfile)

        args = [sys.executable, self.script_path, '-c', std_config_path]

        if subprocess.run(args).returncode != 0:
            raised = True

        self.assertFalse(raised, 'Exception raised')


if __name__ == '__main__':
    unittest.main()
