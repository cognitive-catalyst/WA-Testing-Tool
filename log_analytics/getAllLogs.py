import json
from argparse import ArgumentParser
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import dateutil.parser
import datetime
import time

DEFAULT_WCS_VERSION='2018-09-20'
DEFAULT_PAGE_SIZE=500
DEFAULT_NUMBER_OF_PAGES=20

def getAssistant(iam_apikey, url, version=DEFAULT_WCS_VERSION):
    '''Retrieve Watson Assistant SDK object'''
    authenticator = IAMAuthenticator(iam_apikey)
    c = AssistantV1(
        version=version,
        authenticator=authenticator
    )
    #c.set_disable_ssl_verification(True) #TODO: pass disable_ssl parameter here
    c.set_service_url(url)
    return c

def getLogs(iam_apikey, url, workspace_id, filter, page_size_limit=DEFAULT_PAGE_SIZE, page_num_limit=DEFAULT_NUMBER_OF_PAGES, version=DEFAULT_WCS_VERSION):
    '''Public API for script, connects to Watson Assistant and downloads all logs'''
    service = getAssistant(iam_apikey, url, version)
    return getLogsInternal(service, workspace_id, filter, page_size_limit, page_num_limit)

def getLogsInternal(assistant, workspace_id, filter, page_size_limit=DEFAULT_PAGE_SIZE, page_num_limit=DEFAULT_NUMBER_OF_PAGES):
    '''Fetches `page_size_limit` logs at a time through Watson Assistant log API, a maximum of `page_num_limit` times, and returns array of log events'''
    cursor = None
    pages_retrieved = 0
    allLogs = []
    noMore = False

    while pages_retrieved < page_num_limit and noMore != True:
        if workspace_id is None:
            #all - requires a workspace_id, assistant id, or deployment id in the filter
            output = assistant.list_all_logs(sort='-request_timestamp', filter=filter, page_limit=page_size_limit, cursor=cursor)
        else:
            output = assistant.list_logs(workspace_id=workspace_id, sort='-request_timestamp', filter=filter, page_limit=page_size_limit, cursor=cursor)

        #Hack for API compatibility between v1 and v2 of the API - v2 adds a 'result' property on the response.  v2 simplest form is list_logs().get_result()
        output = json.loads(str(output))
        if 'result' in output:
           logs = output['result']
        else:
           logs = output

        if 'pagination' in logs and len(logs['pagination']) != 0:
            cursor = logs['pagination'].get('next_cursor', None)
            #Do not DOS the list_logs function!
            time.sleep(3.0)
        else:
            noMore = True

        if 'logs' in logs:
           allLogs.extend(logs['logs'])
           pages_retrieved = pages_retrieved + 1
           print("Fetched {} log pages with {} total logs".format(pages_retrieved, len(allLogs)))
        else:
           return None

    #Analysis is easier when logs are in increasing timestamp order
    allLogs.reverse()

    return allLogs

def writeLogs(logs, output_file, output_columns="raw"):
    '''
    Writes log output to file system or screen.  Includes three modes:
    `raw`: logs are written in JSON format
    `all`: all log columns useful for intent training are written in CSV format
    `utterance`: only the `input.text` column is written (one per line)
    '''
    file = None
    if output_file != None:
       file = open(output_file,'w')

       print("Writing {} logs to {}".format(len(logs), output_file))

    if 'raw' == output_columns:
       writeOut(file, json.dumps(logs,indent=2))
       if file is not None:
           file.close()
       return

    if 'all' == output_columns:
        writeOut(file, 'Utterance\tIntent\tConfidence\tDate\tLast Visited')

    for log in logs:
       utterance    = log['request' ]['input']['text']
       intent       = 'unknown_intent'
       confidence   = 0.0
       date         = 'unknown_date'
       last_visited = 'unknown_last_visited'
       if 'response' in log and 'intents' in log['response'] and len(log['response']['intents'])>0:
          intent     = log['response']['intents'][0]['intent']
          confidence = log['response']['intents'][0]['confidence']
          dateStr    = log['request_timestamp']
          date       = dateutil.parser.parse(dateStr).strftime("%Y-%m-%d")
          if 'nodes_visited' in log['response']['output'] and len (log['response']['output']['nodes_visited']) > 0:
             last_visited = log['response']['output']['nodes_visited'][-1]

       if 'all' == output_columns:
          output_line = '{}\t{}\t{}\t{}\t{}'.format(utterance, intent, confidence, date, last_visited)
       else:
          #assumed just 'utterance'
          output_line = utterance

       writeOut(file, output_line)

    if output_file != None:
       file.close()

def writeOut(file, message):
    if file != None:
        file.write(message + '\n')
    else:
        print(message)

def create_parser():
    parser = ArgumentParser(description='Extracts Watson Assistant logs from a given workspace')
    parser.add_argument('-c', '--output_columns', type=str, help='Which columns you want in output, either "utterance", "raw", or "all" (default is "raw")', default='raw')
    parser.add_argument('-o', '--output_file', type=str, help='Filename to write results to')
    parser.add_argument('-w', '--workspace_id', type=str, help='Workspace identifier')
    parser.add_argument('-a', '--iam_apikey', type=str, required=True, help='Assistant service iam api key')
    parser.add_argument('-f', '--filter', type=str, required=True, help='Watson Assistant log query filter')
    parser.add_argument('-v', '--version', type=str, default=DEFAULT_WCS_VERSION, help="Watson Assistant version in YYYY-MM-DD form.")
    parser.add_argument('-n', '--number_of_pages', type=int, default=DEFAULT_NUMBER_OF_PAGES, help='Number of result pages to download (default is {})'.format(DEFAULT_NUMBER_OF_PAGES))
    parser.add_argument('-p', '--page_limit', type=int, default=DEFAULT_PAGE_SIZE, help='Number of results per page (default is {})'.format(DEFAULT_PAGE_SIZE))
    parser.add_argument('-l', '--url', type=str, default='https://gateway.watsonplatform.net/assistant/api',
                        help='URL to Watson Assistant. Ex: https://gateway-wdc.watsonplatform.net/assistant/api')

    return parser

if __name__ == '__main__':
   ARGS = create_parser().parse_args()

   service = getAssistant(ARGS.iam_apikey,ARGS.url,ARGS.version)
   logs    = getLogsInternal(service, ARGS.workspace_id, ARGS.filter, ARGS.page_limit, ARGS.number_of_pages)
   writeLogs(logs, ARGS.output_file, ARGS.output_columns)
