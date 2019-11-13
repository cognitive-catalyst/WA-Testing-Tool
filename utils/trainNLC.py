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

""" Train NLC instance
    Classification input schema (headerless):
    | utterance | intent |
"""
import json
from time import sleep
import csv
import pandas as pd
from argparse import ArgumentParser
from ibm_watson import NaturalLanguageClassifierV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from __init__ import UTF_8, \
                  UTTERANCE_COLUMN, INTENT_COLUMN, \
                  TIME_TO_WAIT, CLASSIFIER_ID_TAG
SLEEP_INCRE = 10
CLASS_CSV_HEADER = [UTTERANCE_COLUMN, INTENT_COLUMN]


class TrainTimeoutException(Exception):
    """ To be thrown if training is timeout
    """
    def __init__(self, message):
        self.message = message

def func(args):
    classifier_name = ''
    classifier_description = ''
    classes = []
    language = 'en'
    counterexamples = []
    metadata = {}
    learning_opt_out = False

    authenticator = IAMAuthenticator(args.iam_apikey)
    nlc = NaturalLanguageClassifierV1(
        authenticator=authenticator
    )    
    nlc.set_service_url(args.url)
    
    classifier_name = "My Classifier"
    if args.classifier_name is not None:
        classifier_name = args.classifier_name
    metadata = {"name": classifier_name ,"language": "en"}
        
    if args.trainingFile is not None:
        with open(args.trainingFile, 'rb') as training_data:
            classifier = nlc.create_classifier(
                training_data=training_data,
                training_metadata=json.dumps(metadata)
                ).get_result()

    resp = classifier
    # Poke the training status every SLEEP_INCRE secs
    sleep_counter = 0
    while sleep_counter < TIME_TO_WAIT:
        raw_resp = nlc.get_classifier(classifier_id=resp[CLASSIFIER_ID_TAG])
        resp = raw_resp.get_result()
        if resp['status'] == 'Available':
            print(json.dumps(resp, indent=4))  # double quoted valid JSON
            return
        sleep_counter += SLEEP_INCRE
        sleep(SLEEP_INCRE)
    raise TrainTimeoutException('NLC training timeout')


def create_parser():
    parser = ArgumentParser(
        description='Train NLC instance')
    parser.add_argument('-i', '--trainingFile', type=str,
                        help='Training file')
    parser.add_argument('-a', '--iam_apikey', type=str, required=True,
                        help='NLC service iam api key')
    parser.add_argument('-n', '--classifier_name', type=str,
                        help='Classifier name')
    parser.add_argument('-l', '--url', type=str, default='https://gateway.watsonplatform.net/natural_language_classifier/api',
                        help='URL to Watson NLC. Ex: https://gateway.watsonplatform.net/natural_language_classifier/api')

    return parser

if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
