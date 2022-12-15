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

""" Train NLU instance
    Classification input schema (headerless):
    | utterance | intent |
"""
import json
from time import sleep
import csv
import pandas as pd
from argparse import ArgumentParser
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from choose_auth import choose_auth

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

    authenticator = choose_auth(args)

    nlu = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    ) 
    nlu.set_service_url(args.url)
    nlu.set_disable_ssl_verification(eval(args.disable_ssl))
    
    classifier_name = "My Classifier"
    if args.classifier_name is not None:
        classifier_name = args.classifier_name

    if args.trainingFile is not None:
        #convert from csv to json 
        training_data_file = get_training_data_json_file(args.trainingFile)
    else:
        exit(-1)
    
    with open(training_data_file, 'r') as training_data:
        classifier = nlu.create_classifications_model(
                language='en',
                #default file format is json; should be able to use csv with the correct training_data_content_type parameter 
                training_data=training_data,
                training_data_content_type='application/json',
                name=classifier_name,
                model_version="1.0.1"
                ).get_result()

    resp = classifier
    # Poke the training status every SLEEP_INCRE secs
    sleep_counter = 0
    while sleep_counter < TIME_TO_WAIT:
        raw_resp = nlu.get_classifications_model(model_id=resp['model_id'])
        resp = raw_resp.get_result()
        #try status again 
        if resp['status'] == 'available':
            print(json.dumps(resp, indent=4))  # double quoted valid JSON
            return
        sleep_counter += SLEEP_INCRE
        sleep(SLEEP_INCRE)
    raise TrainTimeoutException('NLU training timeout')


def create_parser():
    parser = ArgumentParser(
        description='Train NLU instance')
    parser.add_argument('-i', '--trainingFile', type=str,
                        help='Training file')
    parser.add_argument('-a', '--iam_apikey', type=str, required=True,
                        help='NLU service iam api key')
    parser.add_argument('-n', '--classifier_name', type=str,
                        help='Classifier name')
    parser.add_argument('-l', '--url', type=str, default='https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                        help='URL to Watson NLU. Ex: https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
    parser.add_argument('--auth-type', type=str, default='iam',
                        help='Authentication type, IAM is default, bearer is required for CP4D.', choices=['iam', 'bearer'])
    parser.add_argument('--disable_ssl', type=str, default="False",
                        help="Disables SSL verification. BE CAREFUL ENABLING THIS. Default is False", choices=["True", "False"])
    return parser

def get_training_data_json_file(csv_data_filename):
    nlu_data = []

    json_data_filename = csv_data_filename + ".json"
    with open(csv_data_filename, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            text = row[0]
            labels = row[1:]
            # Convert the text and label in NLU training data JSON object
            data_dict = {
                'text': text,
                'labels': labels
            }
            nlu_data.append(data_dict)

    with open(json_data_filename, 'w', encoding='utf-8') as json_file:
        json.dump(nlu_data, json_file, indent=2)
    return json_data_filename

if __name__ == '__main__':  
    ARGS = create_parser().parse_args()
    func(ARGS)
