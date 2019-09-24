import sys
import json
from argparse import ArgumentParser
from watson_developer_cloud import AssistantV1

WCS_VERSION='2018-09-20'
DEFAULT_PAGE_LIMIT=100

def getAssistant(iam_apikey, url):
    c = AssistantV1(iam_apikey=iam_apikey, version=WCS_VERSION, url=url)
    return c


def getLogs(assistant, workspace_id, node_id, page_limit):
    filter = 'response.output.nodes_visited::{}'.format(node_id)
    output = assistant.list_logs(workspace_id=workspace_id, sort='-request_timestamp', filter=filter, page_limit=page_limit)

    #Hack for API compatibility between v1 and v2 of the API - v2 adds a 'result' property on the response.  v2 simplest form is list_logs().get_result()
    output = json.loads(str(output))
    if 'result' in output:
       logs = output['result']
    else:
       logs = output

    if 'logs' in logs:
       return logs['logs']
    else:
       return None

def outputLogs(logs, output_columns, output_file):
    if output_file != None:
       file = open(output_file,'w')

    for log in logs:
       utterance  = log['request' ]['input']['text']
       intent     = 'unknown'
       confidence = 0.0
       if 'response' in log and 'intents' in log['response'] and len(log['response']['intents'])>0:
          intent     = log['response']['intents'][0]['intent']
          confidence = log['response']['intents'][0]['confidence']

       if 'all' == output_columns:
          output_line = '{}\t{}\t{}'.format(utterance, intent, confidence)
       else:
          #assumed just 'utterance'
          output_line = utterance

       if output_file != None:
          file.write(output_line + '\n')
       else:
          print(output_line)

    if output_file != None:
       file.close()

def create_parser():
    parser = ArgumentParser(description='Gathers user inputs that led to a given dialog node')
    parser.add_argument('-n', '--node_id', type=str, help='ID of the node where you want the user input that directly led to this node, default is "anything_else"', default='anything_else')
    parser.add_argument('-c', '--output_columns', type=str, help='Which columns you want in output, either "utterance" or "all" (default is "utterance")', default='utterance')
    parser.add_argument('-o', '--output_file', type=str, help='Filename to write results to')
    parser.add_argument('-w', '--workspace_id', type=str, help='Workspace identifier', required=True)
    parser.add_argument('-a', '--iam_apikey', type=str, required=True, help='Assistant service iam api key')
    parser.add_argument('-p', '--page_limit', type=int, default=DEFAULT_PAGE_LIMIT, help='Number of results downloaded per page (default is 1 page with max {} results in that page)'.format(DEFAULT_PAGE_LIMIT))
    parser.add_argument('-l', '--url', type=str, default='https://gateway.watsonplatform.net/assistant/api',
                        help='URL to Watson Assistant. Ex: https://gateway-wdc.watsonplatform.net/assistant/api')

    return parser

if __name__ == '__main__':
   ARGS = create_parser().parse_args()

   service = getAssistant(ARGS.iam_apikey,ARGS.url)
   logs    = getLogs(service, ARGS.workspace_id, ARGS.node_id, ARGS.page_limit)
   outputLogs(logs, ARGS.output_columns, ARGS.output_file)
