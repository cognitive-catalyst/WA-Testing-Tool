import os
import sys
import json
from argparse import ArgumentParser
from collections import defaultdict

def getLogs(inputPath):
    if(os.path.isdir(inputPath)):
        data = []
        print('Processing input directory {}'.format(inputPath))
        for root, dirs, files in os.walk(inputPath):
            dirs.sort()
            files.sort()
            for file in files:
                if file.endswith('.json'):
                    logFile = os.path.join(root, file)
                    fileData = getLogsFromFile(logFile)
                    data.extend(fileData)
        return data
    else:
        return getLogsFromFile(inputPath)

def getLogsFromFile(filename):
    print('Processing input file {}'.format(filename))
    with open(filename) as json_file:
        data = json.load(json_file)

    return data

def deep_get(dct, keys, default=None):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
    return dct

def logStats(logs, conversation_id_key, output_file):
    file = None

    conversation_key_keys = conversation_id_key.split(".")
    logs_by_id = defaultdict(list)

    for log in logs:
       id = deep_get(log, conversation_key_keys)
       if id is not None:
           logs_by_id.setdefault(id, [])
           logs_by_id[id].append(log) #If log is sorted earliest to latest
           #logs_by_id[id].insert(0, log) #If log is sorted latest to earliest

    print("Sorting conversations by request_timestamp")
    for id in logs_by_id:
        logs_by_id[id].sort(key=lambda x: x.get('request_timestamp'))

    print("Writing output file {}".format(output_file))
    with open(output_file, "w") as file:
        file.write(json.dumps(logs_by_id, indent=2))

    print("Wrote output file {}".format(output_file))

def create_parser():
    parser = ArgumentParser(description='Correlates Watson Assistant logs by a conversation identifier')
    parser.add_argument('-i', '--input_file', default='input.json', required=True, type=str, help='Filename containing JSON logs')
    parser.add_argument('-o', '--output_file', default='input_by_conversation.json', type=str, help='Filename to write results to')
    parser.add_argument('-c', '--conversation_id', default="response.context.conversation_id", type=str, help='Key of conversation unique identifier')

    return parser

if __name__ == '__main__':
   ARGS = create_parser().parse_args()

   logs    = getLogs(ARGS.input_file)
   logStats(logs, ARGS.conversation_id, ARGS.output_file)
