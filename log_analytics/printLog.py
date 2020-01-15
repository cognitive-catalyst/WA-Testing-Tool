import json
import sys
import os

def printLog(path:str, id:str):
    jsonFile = open(path, 'r')
    data = json.load(jsonFile)

    if data.get(id):
        log_list = data[id]
        for log in log_list:
            req_time   = log['request_timestamp']
            rsp_time   = log['response_timestamp']
            input      = log['request']['input']['text']
            out_text   = log['response']['output']['text']
            out_route = ''
            out_method = ''
            if 'action' in log['response']['context']:
                if 'route' in log['response']['context']['action']:
                   out_route  = log['response']['context']['action']['route']
                   out_method = log['response']['context']['action']['method']
                else:
                   out_route = 'info'
                   out_method = str(log['response']['context']['action']['info'])

            print(req_time + '>>> ' + input)
            print(rsp_time + '<<< ' + str(out_text) + " [" + out_route + " " + out_method + "]")

    jsonFile.close()

if __name__ == '__main__':
    printLog(sys.argv[1], sys.argv[2])
