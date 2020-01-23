import sys
import os
import json
from argparse import ArgumentParser
import dateutil.parser
import datetime
from collections import defaultdict

def getLogs(filename):
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

def logStats(logs_by_id, first_turn_index, speech_confidence_variable, input_filename, to_reverse):
    #save_conversations_to_disk(logs_by_id)
    if speech_confidence_variable is None:
        first_turn_intent_stats(logs_by_id, first_turn_index, input_filename, to_reverse)
        all_turn_raw_stats(logs_by_id, first_turn_index, input_filename, to_reverse)
    else:
        first_turn_speech_stats(logs_by_id, first_turn_index, speech_confidence_variable, input_filename, to_reverse)
        all_turn_speech_stats(logs_by_id, first_turn_index, speech_confidence_variable, input_filename, to_reverse)

def first_turn_intent_stats(logs_by_id, first_turn_index, input_filename, to_reverse):
    raw_intent_turn_filename = input_filename[:-5] + "_raw-intent-turn.tsv"
    print('Writing intent details to ' + raw_intent_turn_filename)
    with open(raw_intent_turn_filename,'w') as raw_intent_file:
        writeOut(raw_intent_file, "Conversation ID\tIntent\tIntent Confidence\tUtterance")
        intent_accum = defaultdict(dict)
        for id in logs_by_id:
            if len(logs_by_id[id]) > first_turn_index:
                if to_reverse:
                    logs_by_id[id].reverse()
                log = logs_by_id[id][first_turn_index]
                if 'response' in log and 'intents' in log['response'] and len(log['response']['intents'])>0:
                    intent     = log['response']['intents'][0]['intent']
                    confidence = log['response']['intents'][0]['confidence']
                    intent_dict = intent_accum.get(intent, None)
                    if(intent_dict is None):
                        intent_dict = {'total':0, 'total_intent_confidence':0.0}
                    intent_dict['total'] += 1
                    intent_dict['total_intent_confidence'] += confidence
                    intent_accum[intent] = intent_dict
                    writeOut(raw_intent_file, "{}\t{}\t{}\t{}".format(id, intent, confidence, log['request']['input']['text']))

    out_file_name=input_filename[:-5] + "_first-turn-stats.tsv"
    print('Writing intent summary to ' + out_file_name)
    with open(out_file_name,'w') as ifile:
        writeOut(ifile,'Intent\tTotal\tIntent Confidence')
        for intent in intent_accum:
            intent_dict = intent_accum.get(intent)
            line = '{}\t{}\t{}'.format(intent, intent_dict['total'], intent_dict['total_intent_confidence'] / intent_dict['total'])
            writeOut(ifile, line)

def all_turn_raw_stats(logs_by_id, first_turn_index, input_filename, to_reverse):
    raw_intent_turn_filename = input_filename[:-5] + "_raw-all-turn.tsv"
    print('Writing all utterance details to ' + raw_intent_turn_filename)
    with open(raw_intent_turn_filename,'w') as raw_intent_file:
        writeOut(raw_intent_file, "Conversation ID\tIntent\tIntent Confidence\tUtterance\tDate\tTime")
        for id in logs_by_id:
            if to_reverse:
                logs_by_id[id].reverse()
            for log in logs_by_id[id]:
                intent = 'n/a'
                confidence = '0.0'
                dateStr    = log['request_timestamp']
                date       = dateutil.parser.parse(dateStr).strftime("%Y-%m-%d")
                time       = dateutil.parser.parse(dateStr).strftime("%H:%M:%S")
                if 'response' in log and 'intents' in log['response'] and len(log['response']['intents'])>0:
                    intent     = log['response']['intents'][0]['intent']
                    confidence = log['response']['intents'][0]['confidence']

                writeOut(raw_intent_file, "{}\t{}\t{}\t{}\t{}\t{}".format(id, intent, confidence, log['request']['input']['text'], date, time))

def first_turn_speech_stats(logs_by_id, first_turn_index, speech_confidence_variable, input_filename, to_reverse):
    stt_confidence_key_keys = speech_confidence_variable.split(".")

    raw_intent_turn_filename = input_filename[:-5] + "_raw-intent-turn.tsv"
    print('Writing intent details to ' + raw_intent_turn_filename)
    with open(raw_intent_turn_filename,'w') as raw_intent_file:
        writeOut(raw_intent_file, "Conversation ID\tIntent\tIntent Confidence\tSpeech Confidence\tUtterance")
        intent_accum = defaultdict(dict)
        for id in logs_by_id:
            if to_reverse:
                logs_by_id[id].reverse()
            
            if len(logs_by_id[id]) > first_turn_index:
                log = logs_by_id[id][first_turn_index]
                if 'response' in log and 'intents' in log['response'] and len(log['response']['intents'])>0:
                    intent     = log['response']['intents'][0]['intent']
                    confidence = log['response']['intents'][0]['confidence']
                    stt_conf = float(deep_get(log, stt_confidence_key_keys, '0.0'))
                    intent_dict = intent_accum.get(intent, None)
                    if(intent_dict is None):
                        intent_dict = {'total':0, 'total_intent_confidence':0.0, 'total_stt_confidence':0.0}
                    intent_dict['total'] += 1
                    intent_dict['total_intent_confidence'] += confidence
                    intent_dict['total_stt_confidence']    += stt_conf
                    intent_accum[intent] = intent_dict
                    writeOut(raw_intent_file, "{}\t{}\t{}\t{}\t{}".format(id, intent, confidence, stt_conf, log['request']['input']['text']))

    out_file_name=input_filename[:-5] + "_first-turn-stats.tsv"
    print('Writing intent summary to ' + out_file_name)
    with open(out_file_name,'w') as ifile:
        writeOut(ifile,'Intent\tTotal\tIntent Confidence\tSTT Confidence')
        for intent in intent_accum:
            intent_dict = intent_accum.get(intent)
            line = '{}\t{}\t{}\t{}'.format(intent, intent_dict['total'], intent_dict['total_intent_confidence'] / intent_dict['total'], intent_dict['total_stt_confidence'] / intent_dict['total'])
            writeOut(ifile, line)

def all_turn_speech_stats(logs_by_id, first_turn_index, speech_confidence_variable, input_filename, to_reverse):
    stt_confidence_key_keys = speech_confidence_variable.split(".")

    raw_intent_turn_filename = input_filename[:-5] + "_raw-all-turn.tsv"
    print('Writing all utterance details to ' + raw_intent_turn_filename)
    with open(raw_intent_turn_filename,'w') as raw_intent_file:
        writeOut(raw_intent_file, "Conversation ID\tIntent\tIntent Confidence\tSpeech Confidence\tUtterance\tDate\tTime")
        for id in logs_by_id:
            if to_reverse:
                logs_by_id[id].reverse()
            for log in logs_by_id[id]:
                intent = 'n/a'
                confidence = '0.0'
                stt_conf = float(deep_get(log, stt_confidence_key_keys, '0.0'))
                dateStr    = log['request_timestamp']
                date       = dateutil.parser.parse(dateStr).strftime("%Y-%m-%d")
                time       = dateutil.parser.parse(dateStr).strftime("%H:%M:%S")
                if 'response' in log and 'intents' in log['response'] and len(log['response']['intents'])>0:
                    intent     = log['response']['intents'][0]['intent']
                    confidence = log['response']['intents'][0]['confidence']

                writeOut(raw_intent_file, "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(id, intent, confidence, stt_conf, log['request']['input']['text'], date, time))

def save_conversations_to_disk(logs_by_id):
    #Pre-req: mkdir `conversations`
    os.mkdir("conversations")
    for id in logs_by_id:
        with open("conversations/" + id + ".json", "w") as one_call_file:
            writeOut(one_call_file, json.dumps(logs_by_id.get(id), indent=2))
            print("conversations/" + id + ".json")


def writeOut(file, message):
    if file != None:
        file.write(message + '\n')
    else:
        print(message)

def create_parser():
    parser = ArgumentParser(description='Gathers statistics on Watson Assistant logs')
    parser.add_argument('-i', '--input_file', default='input.json', required=True, type=str, help='Filename containing JSON logs, each key is a conversation ID and each value is a list of logs for that converstation')
    parser.add_argument('-f', '--first_turn_index', default=0, type=int, required=True, help="0-based index for which conversation turn is the first where user sends a message (not system internal message)")
    parser.add_argument('-s', '--speech_confidence_variable', default=None, type=str, help="Name of context variable containing Speech to Text confidence (omit this variable for chat-only assistants)")
    parser.add_argument('-r', '--reverse', default=False, dest='reverse', action='store_true', help="Specify to reverse-sort the conversation logs")

    return parser

if __name__ == '__main__':
   ARGS = create_parser().parse_args()

   logs    = getLogs(ARGS.input_file)
   logStats(logs, ARGS.first_turn_index, ARGS.speech_confidence_variable, ARGS.input_file, ARGS.reverse)
