#! /usr/bin/python
""" Train assistant instance with intents and entities
    Intent input schema (headerless):
    | utterance | intent |
    Entity input schema (headerless):
    | entity | value | synonym/pattern 0 | synonym/pattern 1 | ...
"""
import json
from time import sleep
import csv
import pandas as pd
from argparse import ArgumentParser
from watson_developer_cloud import AssistantV1

from utils import UTF_8, WCS_VERSION, \
                  UTTERANCE_COLUMN, INTENT_COLUMN, \
                  TIME_TO_WAIT, WORKSPACE_ID_TAG

ENTITY_COLUMN = 'entity'
ENTITY_VALUE_COLUMN = 'value'
EXAMPLES_COLUMN = 'examples'
ENTITY_VALUES_ARR_COLUMN = 'values'
SLEEP_INCRE = 10
INTENT_CSV_HEADER = [UTTERANCE_COLUMN, INTENT_COLUMN]
ENTITY_CSV_HEADER = [ENTITY_COLUMN, ENTITY_VALUE_COLUMN]


class TrainTimeoutException(Exception):
    """ To be thrown if training is timeout
    """
    def __init__(self, message):
        self.message = message


def to_examples(intent_group):
    """ Parse each row of intent group into a CreateIntent[]
    """
    res = []
    for _, row in intent_group.iterrows():
        if row['utterance']:  # Ignore empty examples
            res.append({'text': row['utterance']})

    return res


def to_entity_values(entity_group):
    """ Parse current entity group content into a CreateEntity[]
    """
    values = []
    for _, row in entity_group.iterrows():
        value = row[ENTITY_VALUE_COLUMN]
        synonyms = []
        patterns = []
        # Drop first two item and iterate the rest items (synonym or pattern)
        for _, val in row.drop([ENTITY_COLUMN, ENTITY_VALUE_COLUMN]) \
                .iteritems():
            if not pd.isnull(val):
                if val.startswith('/'):  # is pattern?
                    patterns.append(val[:-1][1:])
                else:
                    synonyms.append(val)
        # Construct CreateValue[]
        if len(synonyms) != 0:
            values.append({'value': value, 'synonyms': synonyms,
                           'type': 'synonyms'})
        elif len(patterns) != 0:
            values.append({'value': value, 'patterns': patterns,
                           'type': 'patterns'})
        else:
            values.append({'value': value})

    return values


def func(args):
    entities = None
    workspace_name = None
    workspace_description = None

    # First, group utterances by INTENT_COLUMN. In each intent group,
    # construct the CreateIntent[] and return as a cell of the series.
    # Convert the series into dataframe and restore the intent column
    # from index to an explicit column.
    intent_df = pd.read_csv(args.intentfile, quoting=csv.QUOTE_ALL,
                            encoding=UTF_8, header=None,
                            names=INTENT_CSV_HEADER, keep_default_na=False) \
                  .groupby(by=[INTENT_COLUMN]).apply(to_examples) \
                  .to_frame().reset_index(level=[INTENT_COLUMN]) \
                  .rename(columns={0: EXAMPLES_COLUMN})

    # Construct the CreateIntent[]
    intents = [{'intent': row[INTENT_COLUMN],
                'examples': row[EXAMPLES_COLUMN]}
               for _, row in intent_df.iterrows()]

    if args.entityfile is not None:
        # Read csv with unknown number of columns into dataframe
        rows = None
        with open(args.entityfile, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, quoting=csv.QUOTE_ALL)
            rows = list(reader)

        entity_df = pd.DataFrame(rows)

        # Rename 1st, 2nd column to ENTITY_COLUMN, ENTITY_VALUE_COLUMN.
        # Group rows by entity name. In each entity group,
        # construct the CreateEntity[] and return as a cell of the series.
        # Convert the series into dataframe and restore
        # the intent column from index to an explicit column.
        entity_df = entity_df.rename(
                    columns={0: ENTITY_COLUMN, 1: ENTITY_VALUE_COLUMN}) \
            .groupby(by=[ENTITY_COLUMN]).apply(to_entity_values).to_frame() \
            .reset_index(level=[ENTITY_COLUMN]) \
            .rename(columns={0: ENTITY_VALUES_ARR_COLUMN})

        # Construct the CreateEntity[]
        entities = [{'entity': row[ENTITY_COLUMN],
                     'values': row[ENTITY_VALUES_ARR_COLUMN]}
                    for _, row in entity_df.iterrows()]

    conv = AssistantV1(username=args.username, password=args.password,
                       version=WCS_VERSION)

    if args.workspace_name is not None:
        workspace_name = args.workspace_name
    if args.workspace_description is not None:
        workspace_description = args.workspace_description

    # Create workspace with provided content
    resp = conv.create_workspace(name=workspace_name,
                                 description=workspace_description,
                                 intents=intents, entities=entities)

    # Poke the training status every SLEEP_INCRE secs
    sleep_counter = 0
    while sleep_counter < TIME_TO_WAIT:
        resp = conv.get_workspace(workspace_id=resp[WORKSPACE_ID_TAG])
        if resp['status'] == 'Available':
            print(json.dumps(resp, indent=4))  # double quoted valid JSON
            return
        sleep_counter += 10
        sleep(10)

    raise TrainTimeoutException('Assistant training is timeout')


if __name__ == '__main__':
    PARSER = ArgumentParser(
        description='Train assistant instance with intents and entities')
    PARSER.add_argument('-i', '--intentfile', type=str, required=True,
                        help='Intent file')
    PARSER.add_argument('-e', '--entityfile', type=str, help='Entity file')
    PARSER.add_argument('-n', '--workspace_name', type=str,
                        help='Workspace name')
    PARSER.add_argument('-d', '--workspace_description', type=str,
                        help='Workspace description')
    PARSER.add_argument('-u', '--username', type=str, required=True,
                        help='Assistant service username')
    PARSER.add_argument('-p', '--password', type=str, required=True,
                        help='Assistant service password')
    ARGS = PARSER.parse_args()
    func(ARGS)
