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


import argparse
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
import csv

from __init__ import BASE_URL

WA_API_VERSION = '2017-05-26'


def add_output_arg(parser):
    parser.add_argument(
        '--output', '-o',
        help='Output file',
        default='intent_desc.csv'
    )


def get_remote_workspace(args):
    authenticator = IAMAuthenticator(args.password)
    conv = AssistantV1(
        version=WA_API_VERSION,
        authenticator=authenticator
    )
    conv.set_service_url(args.url)

    workspace = conv.get_workspace(args.workspace_id, export=True)
    write_output(workspace, args.output)


def get_local_workspace(args):
    with open(args.json, 'r') as f:
        workspace = json.load(f)

    write_output(workspace, args.output)


def write_output(workspace_json, output_file):
    intents = workspace_json.result['intents']

    keys = ['intent', 'description']
    with open(output_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')

        writer.writeheader()
        writer.writerows(intents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create Intent Descriptions file from workspace json',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(help='help for subcommand')

    # Create parser for remote Watson Assistant instance
    credentials_parser = subparsers.add_parser(
        'remote',
        help='Watson Assistant Credentials',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_output_arg(credentials_parser)

    requiredNamed = credentials_parser.add_argument_group('required arguments')
    requiredNamed.add_argument(
        '--user', '-u',
        help='Watson Assistant Username',
        required=True
    )
    requiredNamed.add_argument(
        '--password', '-p',
        help='Watson Assistant Password',
        required=True
    )
    requiredNamed.add_argument(
        '--workspace_id', '-w',
        help='Watson Assistant Workspace ID',
        required=True
    )
    requiredNamed.add_argument(
        '--url', '-l',
        help='Watson Assistant Url',
        default='https://gateway.watsonplatform.net/assistant/api'
    )
    credentials_parser.set_defaults(func=get_remote_workspace)

    # Create parser for a local workspace json file
    local_parser = subparsers.add_parser(
        'local',
        help='Local workspace file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_output_arg(local_parser)
    local_parser.add_argument('json', help='Path to workspace json file')
    local_parser.set_defaults(func=get_local_workspace)

    args = parser.parse_args()
    args.func(args)
