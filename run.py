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

import os
import sys
import configparser
import subprocess
import json
from argparse import ArgumentParser
import csv
import pandas as pd
from ibm_watson import AssistantV1
from ibm_watson import NaturalLanguageClassifierV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from utils import TRAIN_FILENAME, TEST_FILENAME, UTTERANCE_COLUMN, \
                  GOLDEN_INTENT_COLUMN, TEST_OUT_FILENAME, WORKSPACE_ID_TAG, CLASSIFIER_ID_TAG, \
                  WA_API_VERSION_ITEM, DEFAULT_WA_VERSION, UTF_8, INTENT_JUDGE_COLUMN, BOOL_MAP, \
                  DEFAULT_TEST_RATE, POPULATION_WEIGHT_MODE, DEFAULT_TEMP_DIR, FOLD_NUM_DEFAULT, \
                  DEFAULT_CONF_THRES, WCS_IAM_APIKEY_ITEM, WCS_BASEURL_ITEM, \
                  WCS_CREDS_SECTION, CREATE_TEST_TRAIN_FOLDS_PATH, \
                  TRAIN_CONVERSATION_PATH, TEST_CONVERSATION_PATH, \
                  TEST_CLASSIFIER_PATH, TRAIN_CLASSIFIER_PATH, CREATE_PRECISION_CURVE_PATH, SPEC_FILENAME, \
                  delete_workspaces, KFOLD, BLIND_TEST, STANDARD_TEST, \
                  INTENT_METRICS_PATH, CONFUSION_MATRIX_PATH, \
                  WORKSPACE_PARSER_PATH, WORKSPACE_BASE_FILENAME, BASE_URL

# SECTIONS
DEFAULT_SECTION = 'DEFAULT'

MODE_ITEM = 'mode'
WORKSPACE_ID_ITEM = 'workspace_id'
INTENT_FILE_ITEM = 'intent_train_file'
ENTITY_FILE_ITEM = 'entity_train_file'
TEST_FILE_ITEM = 'test_input_file'
TRAIN_FILE_ITEM = 'train_input_file'
TEST_OUT_PATH_ITEM = 'test_output_path'
TEMP_DIR_ITEM = 'temporary_file_directory'
OUT_DIR_ITEM = 'output_directory'
FIGURE_PATH_ITEM = 'out_figure_path'
FOLD_NUM_ITEM = 'fold_num'
DO_KEEP_WORKSPACE_ITEM = 'keep_workspace_after_test'
PREVIOUS_BLIND_OUT_ITEM = 'previous_blind_out'
MAX_TEST_RATE_ITEM = 'max_test_rate'
WEIGHT_MODE_ITEM = 'weight_mode'
CONF_THRES_ITEM = 'conf_thres'
WORKSPACE_BASE_ITEM = 'workspace_base'
PARTIAL_CREDIT_TABLE_ITEM = 'partial_credit_table'
BLIND_FIGURE_TITLE = 'blind_figure_title'
WATSON_SERVICE = 'assistant'

# Max test request rate
MAX_TEST_RATE = DEFAULT_TEST_RATE

def validate_config(fields, section):
    for field in fields:
        if field not in section:
            raise ValueError(
                "Item '{}' is missing in config file".
                format(field))


def list_workspaces(iam_apikey, version, url):
    authenticator = IAMAuthenticator(iam_apikey)
    if WATSON_SERVICE != 'nlc':
        c = AssistantV1(
            version=version,
            authenticator=authenticator
        )
        c.set_service_url(url)
        return c.list_workspaces()
    else:
        c = NaturalLanguageClassifierV1(authenticator)
        c.set_service_url(url)
        return c.list_classifiers()


def kfold(fold_num, out_dir, intent_train_file, workspace_base_file, test_out_path,
          figure_path, keep_workspace, iam_apikey, url, version, weight_mode,
          conf_thres, partial_credit_table):
    FOLD_TRAIN = 'fold_train'
    FOLD_TEST = 'fold_test'
    WORKSPACE_SPEC = 'fold_workspace'
    WORKSPACE_NAME = 'workspace_name'
    TEST_OUT = 'test_out'

    print('Begin {} with following details:'.format(KFOLD.upper()))
    print('{}={}'.format(INTENT_FILE_ITEM, intent_train_file))
    print('{}={}'.format(WORKSPACE_BASE_ITEM, workspace_base_file))
    print('{}={}'.format(FIGURE_PATH_ITEM, figure_path))
    print('{}={}'.format(TEST_OUT_PATH_ITEM, test_out_path))
    print('{}={}'.format(OUT_DIR_ITEM, out_dir))
    print('{}={}'.format(FOLD_NUM_ITEM, fold_num))
    print('{}={}'.format(DO_KEEP_WORKSPACE_ITEM, BOOL_MAP[keep_workspace]))
    print('{}={}'.format(WEIGHT_MODE_ITEM, weight_mode))
    print('{}={}'.format(CONF_THRES_ITEM, conf_thres))
    print('{}={}'.format(WCS_BASEURL_ITEM, url))
    print('{}={}'.format(WA_API_VERSION_ITEM, version))
    print('{}={}'.format(PARTIAL_CREDIT_TABLE_ITEM, partial_credit_table))

    working_dir = os.path.join(out_dir, KFOLD)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    # Prepare folds
    if subprocess.run([sys.executable, CREATE_TEST_TRAIN_FOLDS_PATH,
                       '-i', intent_train_file, '-o', working_dir,
                       '-k', str(fold_num)],
                      stdout=subprocess.PIPE).returncode == 0:
        print('Created {} folds'.format(str(fold_num)))
    else:
        raise RuntimeError('Failure in folds creation')

    # Construct fold params
    fold_params = [{FOLD_TRAIN: os.path.join(working_dir, str(idx),
                                             TRAIN_FILENAME),
                    FOLD_TEST: os.path.join(working_dir, str(idx),
                                            TEST_FILENAME),
                    TEST_OUT: os.path.join(working_dir, str(idx),
                                           TEST_OUT_FILENAME),
                    WORKSPACE_SPEC: os.path.join(working_dir,
                                                 str(idx), SPEC_FILENAME),
                    WORKSPACE_NAME: '{}_{}'.format(KFOLD, str(idx))}
                   for idx in range(fold_num)]

    # Begin training
    train_processes_specs = {}
    for fold_param in fold_params:
        spec_file = open(fold_param[WORKSPACE_SPEC], 'w')
        if WATSON_SERVICE != 'nlc':
            train_module_path = TRAIN_CONVERSATION_PATH
        else:
            train_module_path = TRAIN_CLASSIFIER_PATH
        train_args = [sys.executable, train_module_path,
                      '-i', fold_param[FOLD_TRAIN],
                      '-n', fold_param[WORKSPACE_NAME],
                      '-a', iam_apikey,
                      '-l', url]
        if WATSON_SERVICE != 'nlc':
            train_args += ['-v', version,'-w', workspace_base_file]
        train_processes_specs[
            subprocess.Popen(train_args, stdout=spec_file)] = spec_file

    train_failure_idx = []
    for idx, (process, file) in enumerate(train_processes_specs.items()):
        if process.wait() == 0:
            file.close()
        else:
            train_failure_idx.append(idx)

    try:
        if len(train_failure_idx) != 0:
            raise RuntimeError(
                'Fail to train {} fold workspace'.format(','.join(
                    str(train_failure_idx))))

        print('Trained {} workspaces'.format(str(fold_num)))

        # Begin testing
        test_processes = []
        workspace_ids = []
        FOLD_TEST_RATE = int(MAX_TEST_RATE / fold_num)
        for fold_param in fold_params:
            workspace_id = None
            if WATSON_SERVICE != 'nlc':
                test_module_path = TEST_CONVERSATION_PATH
                id_tag = WORKSPACE_ID_TAG
            else:
                test_module_path = TEST_CLASSIFIER_PATH
                id_tag = CLASSIFIER_ID_TAG
            with open(fold_param[WORKSPACE_SPEC]) as f:
                workspace_id = json.load(f)[id_tag]
                workspace_ids.append(workspace_id)
            test_args = [sys.executable, test_module_path,
                         '-i', fold_param[FOLD_TEST],
                         '-o', fold_param[TEST_OUT],
                         '-a', iam_apikey, '-l', url,
                         '-t', UTTERANCE_COLUMN, '-g', GOLDEN_INTENT_COLUMN,
                         '-w', workspace_id, '-r', str(FOLD_TEST_RATE),
                         '-m']
            if partial_credit_table is not None:
                test_args += ['--partial_credit_table', partial_credit_table]
            if WATSON_SERVICE != 'nlc':
                test_args += ['-v', version]
            test_processes.append(subprocess.Popen(test_args))

        test_failure_idx_str = []
        for idx, process in enumerate(test_processes):
            if process.wait() != 0:
                test_failure_idx_str.append(str(idx))

        if len(test_failure_idx_str) != 0:
            raise RuntimeError('Fail to test {} fold workspace'.format(
                ','.join(test_failure_idx_str)))

        print('Tested {} workspaces'.format(str(fold_num)))

        test_out_files = [fold_param[TEST_OUT] for fold_param in fold_params]

        # Add a column for the fold number
        for idx, this_file in enumerate(test_out_files):
            this_df = pd.read_csv(this_file, quoting=csv.QUOTE_ALL, encoding='utf-8', \
                               keep_default_na=False)
            this_df['Fold Index'] = idx
            this_df.to_csv( this_file, encoding='utf-8', quoting=csv.QUOTE_ALL, index=False )


        # Union test out
        kfold_result_file = test_out_path
        pd.concat([pd.read_csv(file, quoting=csv.QUOTE_ALL, encoding=UTF_8,
                               keep_default_na=False)
                   for file in test_out_files]) \
          .to_csv(kfold_result_file,
                  encoding='utf-8', quoting=csv.QUOTE_ALL, index=False)
        print("Wrote k-fold result file to {}".format(kfold_result_file))

        classfier_names = ['Fold {}'.format(idx) for idx in range(fold_num)]

        plot_args = [sys.executable, CREATE_PRECISION_CURVE_PATH,
                     '-t', '{} Fold Test'.format(str(fold_num)),
                     '-o', figure_path, '-w', weight_mode,
                     '--tau', conf_thres, '-n'] + \
            classfier_names + ['-i'] + test_out_files

        if subprocess.run(plot_args).returncode != 0:
            raise RuntimeError('Failure in plotting curves')

        kfold_result_file_base = kfold_result_file[:-4]
        metrics_args = [sys.executable, INTENT_METRICS_PATH,
                     '-i', kfold_result_file,
                     '-o', kfold_result_file_base+".metrics.csv",
                     '--partial_credit_on', str(partial_credit_table is not None)]
        if subprocess.run(metrics_args).returncode != 0:
            raise RuntimeError('Failure in generating intent metrics')

        confusion_args = [sys.executable, CONFUSION_MATRIX_PATH,
                          '-i', kfold_result_file,
                          '-o', kfold_result_file_base+".confusion_args.csv"]
        if subprocess.run(confusion_args).returncode != 0:
            raise RuntimeError('Failure in generating confusion matrix')

    finally:
        if not keep_workspace:
            if WATSON_SERVICE != 'nlc':
                id_tag = WORKSPACE_ID_TAG
            else:
                id_tag = CLASSIFIER_ID_TAG
            workspace_ids = []
            for idx in range(fold_num):
                if idx not in train_failure_idx:
                    with open(fold_params[idx][WORKSPACE_SPEC]) as f:
                        workspace_id = json.load(f)[id_tag]
                        workspace_ids.append(workspace_id)

            delete_workspaces(iam_apikey, url, version, workspace_ids)


def blind(out_dir, intent_train_file, workspace_base_file, figure_path,
          test_out_path, test_input_file, previous_blind_out, workspace_id, keep_workspace,
          iam_apikey, url, version, weight_mode, conf_thres, partial_credit_table, figure_title):
    print('Begin {} with following details:'.format(BLIND_TEST.upper()))
    print('{}={}'.format(INTENT_FILE_ITEM, intent_train_file))
    print('{}={}'.format(WORKSPACE_BASE_ITEM, workspace_base_file))
    print('{}={}'.format(TEST_FILE_ITEM, test_input_file))
    print('{}={}'.format(PREVIOUS_BLIND_OUT_ITEM, previous_blind_out))
    print('{}={}'.format(FIGURE_PATH_ITEM, figure_path))
    print('{}={}'.format(TEST_OUT_PATH_ITEM, test_out_path))
    print('{}={}'.format(OUT_DIR_ITEM, out_dir))
    print('{}={}'.format(DO_KEEP_WORKSPACE_ITEM, BOOL_MAP[keep_workspace]))
    print('{}={}'.format(WEIGHT_MODE_ITEM, weight_mode))
    print('{}={}'.format(CONF_THRES_ITEM, conf_thres))
    print('{}={}'.format(WCS_BASEURL_ITEM, url))
    print('{}={}'.format(WA_API_VERSION_ITEM, version))
    print('{}={}'.format(PARTIAL_CREDIT_TABLE_ITEM, partial_credit_table))

    # Validate previous blind out format
    test_out_files = [test_out_path]
    classfier_names = ['New Classifier']

    if previous_blind_out is not None:
        df = pd.read_csv(previous_blind_out, quoting=csv.QUOTE_ALL,
                         encoding=UTF_8)
        header = list(df.columns.values)

        if INTENT_JUDGE_COLUMN not in header:
            raise ValueError(
                "'{}' column doesn't exist in {}.".format(
                    INTENT_JUDGE_COLUMN, previous_blind_out))

        test_out_files.append(previous_blind_out)
        classfier_names.append('Old Classifier')

    working_dir = os.path.join(out_dir, BLIND_TEST)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    if WATSON_SERVICE != 'nlc':
        workspace_spec_json = os.path.join(working_dir, SPEC_FILENAME)
        train_args = [sys.executable, TRAIN_CONVERSATION_PATH,
                      '-i', intent_train_file, '-n', 'blind test',
                      '-a', iam_apikey,
                      '-l', url, '-v', version,
                      '-w', workspace_base_file]
        with open(workspace_spec_json, 'w') as f:
            if subprocess.run(train_args, stdout=f).returncode == 0:
                print('Trained blind workspace')
            else:
                raise RuntimeError('Failure in training workspace')

        workspace_id = None
        with open(workspace_spec_json, 'r') as f:
            workspace_id = json.load(f)[WORKSPACE_ID_TAG]
    try:
        if WATSON_SERVICE != 'nlc':
            test_module_path = TEST_CONVERSATION_PATH
        else:
            test_module_path = TEST_CLASSIFIER_PATH
        test_args = [sys.executable, test_module_path,
                     '-i', test_input_file,
                     '-o', test_out_path, '-m',
                     '-a', iam_apikey, '-l', url,
                     '-t', UTTERANCE_COLUMN, '-g', GOLDEN_INTENT_COLUMN,
                     '-w', workspace_id,
                     '-r', str(MAX_TEST_RATE)]
        if partial_credit_table is not None:
            test_args += ['--partial_credit_table', partial_credit_table]
        if WATSON_SERVICE != 'nlc':
             test_args += ['-v', version]
        if subprocess.run(test_args).returncode == 0:
            print('Tested blind workspace')
        else:
            raise RuntimeError('Failure in testing blind data')

        if subprocess.run([sys.executable, CREATE_PRECISION_CURVE_PATH,
                           '-t', figure_title, '-w', weight_mode, '--tau',
                           conf_thres, '-o', figure_path,
                           '-n'] + classfier_names +
                          ['-i'] + test_out_files).returncode != 0:
            raise RuntimeError('Failure in plotting curves')

        blind_result_file = test_out_path
        blind_result_file_base = blind_result_file[:-4]
        metrics_args = [sys.executable, INTENT_METRICS_PATH,
                        '-i', blind_result_file,
                        '-o', blind_result_file_base+"_metrics.csv",
                        '--partial_credit_on', str(partial_credit_table is not None)]
        if subprocess.run(metrics_args).returncode != 0:
            raise RuntimeError('Failure in generating intent metrics')

        confusion_args = [sys.executable, CONFUSION_MATRIX_PATH,
                          '-i', blind_result_file,
                          '-o', blind_result_file_base+"_confusion.csv"]
        if subprocess.run(confusion_args).returncode != 0:
            raise RuntimeError('Failure in generating confusion matrix')
    finally:
        if not keep_workspace and WATSON_SERVICE != 'nlc':
            delete_workspaces(iam_apikey, url, version, [workspace_id])


def test(out_dir, intent_train_file, workspace_base_file, test_out_path,
         test_input_file, workspace_id, keep_workspace, iam_apikey, version, url):
    print('Begin {} with following details:'.format(STANDARD_TEST.upper()))
    print('{}={}'.format(INTENT_FILE_ITEM, intent_train_file))
    print('{}={}'.format(WORKSPACE_BASE_ITEM, workspace_base_file))
    print('{}={}'.format(TEST_FILE_ITEM, test_input_file))
    print('{}={}'.format(TEST_OUT_PATH_ITEM, test_out_path))
    print('{}={}'.format(OUT_DIR_ITEM, out_dir))
    print('{}={}'.format(DO_KEEP_WORKSPACE_ITEM, BOOL_MAP[keep_workspace]))
    print('{}={}'.format(WCS_BASEURL_ITEM, url))
    print('{}={}'.format(WA_API_VERSION_ITEM, version))

    # Validate test file
    extra_params = []
    test_input = pd.read_csv(test_input_file, quoting=csv.QUOTE_ALL,
                             encoding=UTF_8)
    header = list(test_input.columns.values)
    if UTTERANCE_COLUMN in header:
        extra_params += ['-t', UTTERANCE_COLUMN]
    else:
        if len(header) != 1:
            raise ValueError('Test input has unknown utterance column')

    # Run standard test
    working_dir = os.path.join(out_dir, STANDARD_TEST)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    if WATSON_SERVICE != 'nlc':
        workspace_spec_json = os.path.join(working_dir, SPEC_FILENAME)
        train_args = [sys.executable, TRAIN_CONVERSATION_PATH,
                      '-i', intent_train_file,
                      '-n', 'standard test', '-v', version,
                      '-a', iam_apikey, '-l', url,
                      '-w', workspace_base_file]
        with open(workspace_spec_json, 'w') as f:
            if subprocess.run(train_args, stdout=f).returncode == 0:
                print('Trained standard test workspace')
            else:
                raise RuntimeError('Failure in training workspace')

        workspace_id = None
        with open(workspace_spec_json, 'r') as f:
            workspace_id = json.load(f)[WORKSPACE_ID_TAG]
    try:
        if WATSON_SERVICE != 'nlc':
            test_module_path = TEST_CONVERSATION_PATH
        else:
            test_module_path = TEST_CLASSIFIER_PATH
        if WATSON_SERVICE != 'nlc':
             extra_params += ['-v', version]
        if subprocess.run([sys.executable, test_module_path,
                           '-i', test_input_file,
                           '-o', test_out_path, '-m',
                           '-a', iam_apikey, '-l', url,
                           '-w', workspace_id,
                           '-r', str(MAX_TEST_RATE)] + extra_params
                          ).returncode == 0:
            print('Tested workspace')
        else:
            raise RuntimeError('Failure in testing data')
    finally:
        if not keep_workspace and WATSON_SERVICE != 'nlc':
            delete_workspaces(iam_apikey, url, version, [workspace_id])


def func(args):
    """ Parse the config file and invoke corresponding method for test action.
    """
    config = configparser.ConfigParser()
    config.read(args.config_file)

    # Parse config.ini
    if WCS_CREDS_SECTION not in config:
        raise ValueError(
            "Section '{}' is missing in config file".format(WCS_CREDS_SECTION))

    # Validate WCS creds
    validate_config([WCS_IAM_APIKEY_ITEM],
                    config[WCS_CREDS_SECTION])

    iam_apikey = config[WCS_CREDS_SECTION][WCS_IAM_APIKEY_ITEM]
    url = None
    if WCS_BASEURL_ITEM in config[WCS_CREDS_SECTION]:
      url = config[WCS_CREDS_SECTION][WCS_BASEURL_ITEM]
    if url is None or url == "" or len(url) == 0:
      print("Using default url: {}".format(BASE_URL))
      url = BASE_URL
    version = config[WCS_CREDS_SECTION].get(WA_API_VERSION_ITEM, DEFAULT_WA_VERSION)

    # Check the url to see which watson service the current test is against
    # This variable will be used throughout to take the appropriate branch for NLC vs WA
    if 'natural-language-classifier' in url:
        global WATSON_SERVICE
        WATSON_SERVICE = 'nlc'

    # List workspaces to see whether the creds is valid.
    # SDK has no method for validation purpose
    list_workspaces(iam_apikey, version, url)

    print('Credentials are correct')

    default_section = config[DEFAULT_SECTION]

    # Main params validation - make sure required parameters are passed
    validate_config([MODE_ITEM, WORKSPACE_ID_ITEM], default_section)

    #TEMP_DIR_ITEM is legacy configuration variable, subsumed by OUT_DIR_ITEM
    temp_dir = default_section.get(TEMP_DIR_ITEM, DEFAULT_TEMP_DIR)
    out_dir  = default_section.get(OUT_DIR_ITEM, temp_dir)

    if WATSON_SERVICE != 'nlc':
        # Prepare folds
        if subprocess.run([sys.executable, WORKSPACE_PARSER_PATH,
                           '-i', default_section[WORKSPACE_ID_ITEM],
                           '-o', out_dir, '-v', version,
                           '-a', iam_apikey, '-l', url],
                          stdout=subprocess.PIPE).returncode == 0:
            print('Parsed workspace')
        else:
            raise RuntimeError('Failure in parsing workspace')

    intent_train_file = default_section.get(TRAIN_FILE_ITEM,os.path.join(out_dir, 'intent-train.csv'))
    workspace_base_file = os.path.join(out_dir, WORKSPACE_BASE_FILENAME)

    # Convert yes/no to boolean
    keep_workspace = False
    if DO_KEEP_WORKSPACE_ITEM in default_section:
        if default_section[DO_KEEP_WORKSPACE_ITEM].lower() == 'yes':
            keep_workspace = True
        elif default_section[DO_KEEP_WORKSPACE_ITEM].lower() != 'no':
            raise ValueError(
                "Item '{}' is neither 'yes' nor 'no'".
                format(DO_KEEP_WORKSPACE_ITEM))

    mode = default_section[MODE_ITEM].lower()  # Ignore case

    if MAX_TEST_RATE_ITEM in default_section:
        user_test_rate = default_section[MAX_TEST_RATE_ITEM]
        try:
            global MAX_TEST_RATE
            MAX_TEST_RATE = int(user_test_rate)
        except ValueError as e:
            print(e)
    print('Maximum testing rate: {}/cycle'.format(MAX_TEST_RATE))

    weight_mode          = default_section.get(WEIGHT_MODE_ITEM, POPULATION_WEIGHT_MODE).lower()
    conf_thres_str       = default_section.get(CONF_THRES_ITEM, str(DEFAULT_CONF_THRES))
    partial_credit_table = default_section.get(PARTIAL_CREDIT_TABLE_ITEM, None)
    figure_path          = default_section.get(FIGURE_PATH_ITEM, out_dir + "/" + mode + ".png")

    test_out_path   = default_section.get(TEST_OUT_PATH_ITEM, out_dir + "/" + mode + "-out.csv")
    if KFOLD == mode:
        fold_num = default_section.get(FOLD_NUM_ITEM, FOLD_NUM_DEFAULT)

        kfold(fold_num=int(fold_num),
              out_dir=out_dir,
              intent_train_file=intent_train_file,
              workspace_base_file=workspace_base_file,
              test_out_path=test_out_path,
              figure_path=figure_path,
              keep_workspace=keep_workspace,
              iam_apikey=iam_apikey, url=url,
              version=version,
              weight_mode=weight_mode, conf_thres=conf_thres_str,
              partial_credit_table=partial_credit_table)
    else:
        test_input_file = default_section.get(TEST_FILE_ITEM, out_dir + "/input.csv")

        if BLIND_TEST == mode:
            previous_blind_out = default_section.get(PREVIOUS_BLIND_OUT_ITEM, None)
            blind_figure_title = default_section.get(BLIND_FIGURE_TITLE,'Blind Test Results')
            blind(out_dir=out_dir,
                  intent_train_file=intent_train_file,
                  workspace_base_file=workspace_base_file,
                  test_input_file=test_input_file,
                  figure_path=figure_path,
                  test_out_path=test_out_path,
                  previous_blind_out=previous_blind_out,
                  workspace_id=default_section[WORKSPACE_ID_ITEM],
                  keep_workspace=keep_workspace,
                  iam_apikey=iam_apikey, url=url,
                  version=version,
                  weight_mode=weight_mode, conf_thres=conf_thres_str,
                  partial_credit_table=partial_credit_table,
                  figure_title=blind_figure_title)
        elif STANDARD_TEST == mode:
            test(out_dir=out_dir,
                 intent_train_file=intent_train_file,
                 workspace_base_file=workspace_base_file,
                 test_input_file=test_input_file,
                 test_out_path=test_out_path,
                 workspace_id=default_section[WORKSPACE_ID_ITEM],
                 keep_workspace=keep_workspace,
                 iam_apikey=iam_apikey,
                 version=version,
                 url=url)
        else:
            raise ValueError("Unknown mode '{}'".format(mode))


def create_parser():
    parser = ArgumentParser(
        description='Run assistant testing pipeline')
    parser.add_argument('-c', '--config_file', type=str,
                        required=True, help='Intent file')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
