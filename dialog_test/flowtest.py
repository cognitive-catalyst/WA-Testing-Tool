import json
import os
import sys
import flowtest_v1
import pandas as pd

DATA_FOLDER='tests'
OUTPUT_FOLDER='results'
url_default="https://gateway.watsonplatform.net/assistant/api"
PASSWORD=os.environ["ASSISTANT_PASSWORD"]
WA_URL=os.environ.get("ASSISTANT_URL", url_default)
workspace_id=os.environ["WORKSPACE_ID"]
conversation_version="2018-09-20"

def getWatsonSDKVersion():
    #Move to ibm-watson from watson-developer-cloud automatically moved to the newer API signature
    return "2.x"

def validateArguments():
    if(len(sys.argv) < 2):
        print("ERROR: Required arguments: test filename (tab-separated file)")
        exit(-1)

    if len(PASSWORD) < 5:
        print ('No valid ASSISTANT_PASSWORD specified in environment (password is your IAM apikey)')
        sys.exit(-3)

    if len(workspace_id) < 5:
        print ('No valid WORKSPACE_ID specified in environment')
        sys.exit(-4)

    if "ASSISTANT_URL" not in os.environ:
        global url_default
        print('No valid ASSISTANT_URL specified in environment')
        print('Defaulting to: ' + url_default)

def initialize():
    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

def processPath(inputPath:str):
    watsonSDKVersion = getWatsonSDKVersion()

    if(os.path.exists(inputPath) == False):
        print('Cannot read test(s) from path: {}'.format(inputPath))
        sys.exit(-5)

    success = True
    if(os.path.isfile(inputPath)):
        print('Processing single input file {}'.format(inputPath))
        success = processFile(inputPath, watsonSDKVersion)

    if(os.path.isdir(inputPath)):
        print('Processing input directory {}'.format(inputPath))
        for root, dirs, files in os.walk(inputPath):
            for file in files:
                    if file.endswith('.tsv'):
                        testFile = os.path.join(root, file)
                        print(testFile)
                        success = processFile(testFile, watsonSDKVersion) and success

    rc = 0 if success else -1
    sys.exit(rc)


def processFile(flowfile:str, watsonSDKVersion:str):
    basefilename = os.path.basename(flowfile).split('.')[0]

    if flowfile.endswith("json"):
       flow = json.load(open(flowfile))
       flow = pd.DataFrame(flow)
    else:
       flow = pd.read_csv(flowfile, delimiter='\t' )

    # This bit widens the output on screen.
    pd.set_option('display.max_columns', 10000)
    pd.set_option('display.width', 10000)

    #print('Flow to run:')
    #print(flow)
    #print()

    ft = flowtest_v1.FlowTestV1(password=PASSWORD, version=conversation_version, url=WA_URL)

    # print('Creating blank template: ')
    # blank_flow = ft.createBlankTemplate()
    # print(blank_flow)
    # print()

    # print('Creating blank report')
    # report = ft.createBlankReport(alternate_intents=True)
    # print(report)
    # print()

    print()
    print('Running Conversational Flow: {} ({})'.format(flowfile, len(flow)))
    results = ft.runFlowTest(workspace_id=workspace_id, flow=flow, show_progress=True, version=watsonSDKVersion)
    print()
    #Full esults are hard to read, instead we let step by step progress report failures as they happen
    #print('Results:')
    #print(results)
    #print()

    filename = os.path.join(OUTPUT_FOLDER, '{}_report.tsv'.format(basefilename))
    print('Writing full test results to: {}'.format(filename))
    results.to_csv(filename, sep='\t', encoding='utf-8')
    print()

    #Can also run this way
    #print('Running Conversational Flow as JSON: {} ({})'.format(flowfile, flow.shape[0]))
    #results = ft.runFlowTest(workspace_id=workspace_id, flow=flow, show_progress=True,json_dump=True)
    #print()
    #print('Results:')
    #for r in results:
    #        print(r)
    #print()

    # Json is a list. So you save differently.
    filename = os.path.join(OUTPUT_FOLDER, '{}_report.json'.format(basefilename))
    with open(filename, 'w', encoding='utf-8') as file_handler:
        compact = results.to_json(orient='records')
        readable = json.dumps(json.loads(compact), indent=2)
        file_handler.write(readable)


    #print('Report in by intent structure')
    #print(ft.convertReportToIntentPerRow(results,input_all_lines=False))

    success = results[['Matched Output', 'Matched Intent', 'Matched Entity']].replace(to_replace=['', 'n/a'], value=True)
    return success.all().all()

def main():
    scrapeConversation(sys.argv[2], sys.argv[1])


if __name__ == '__main__':
    validateArguments()
    initialize()
    processPath(sys.argv[1])
