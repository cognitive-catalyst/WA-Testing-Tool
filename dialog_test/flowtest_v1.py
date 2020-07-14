from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pandas as pd
import re
import json
import os

class FlowTestV1:
    """ Conversational Flow testing """

    anyFails = False

    templateColList = [
            'User Input',
            'Match Output','Match Intent','Match Entity',
            'Alternate Intents?','Intents Object','Entities Object','Context Variables','System Object'
            ]

    reportColList1 = ['User Input', 'Output Text',
                      'Match Output','Match Intent','Match Entity',
                      'Matched Output', 'Matched Intent', 'Matched Entity', 'Matched Context']
    reportColIntentList = ['Recall@']
    reportColList2 = ['Intent', 'Confidence', 'Entities',  'Alternate Intents', 'Conversation ID', 'Context'  ]

    # Have to do this to sort correctly.
    reportIntentList = ['Intent1', 'Confidence1', 'Intent2', 'Confidence2', 'Intent3', 'Confidence3', 'Intent4', 'Confidence4',
                        'Intent5', 'Confidence5', 'Intent6', 'Confidence6', 'Intent7', 'Confidence7', 'Intent8', 'Confidence8',
                        'Intent9', 'Confidence9', 'Intent10', 'Confidence10' ]

    def __init__(self, **kwargs):
        authenticator = IAMAuthenticator(kwargs.get("password"))
        self.ctk = AssistantV1(
            version=kwargs.get("version"),
            authenticator=authenticator
        )
        self.ctk.set_service_url(kwargs.get("url"))

    def reportFailure(self):
        print("************************* FAIL ****************************")
        self.anyFails = True

    def lastTestResult(self):
        if self.anyFails == False:
          print("******************** LAST TEST PASSED *********************")
        else:
          print("******************** LAST TEST FAILED *********************")
        self.anyFails = False

    def createBlankTemplate(self):
        """ Creates a blank dataframe flow template, that can be used to write your test scripts with. """
        df = pd.DataFrame(columns=list(self.templateColList))
        return df

    def createBlankReport(self, alternate_intents=False):
        """ Creates a blank report dataframe """
        df = pd.DataFrame(columns=list(self.reportColList1 + self.reportColList2),)

        if alternate_intents:
            df = self.createAlternateIntentsColumns(df)

        return df

    def createAlternateIntentsColumns(self, df):
        if 'Intent1' in df.columns:
            return df

        df = df.append(pd.DataFrame(columns=list(self.reportIntentList)))
        cols = list(self.reportColList1) + list(self.reportColList2) + list(self.reportIntentList)
        df.columns = cols
        return df

    def jsonDumpFlowTest(self,workspace_id=None, flow=None, user_goes_first=False, show_progress=True, alternate_intents=True, version="1.x"):
        """
        This will return an array of JSON records instead of a report
        :param workspace_id Required. The workspace to test against.
        :param flow Required. The dataframe containing the test information.
        """
        results = []
        context = {}
        default_intents = alternate_intents

        if user_goes_first:
            payload = { 'text': '' }
            r = self.ctk.message(workspace_id=workspace_id, input=payload, context=context)
            if version.startswith('2.'):
              r = r.get_result()
            context = r['context']
            results.append(r)

        for index, row in flow.iterrows():  # @UnusedVariable
            if show_progress:
                print('{} {}'.format(index, row['User Input']))

            if row.get('User Input','') == 'NEWCONVERSATION':
                context = {}
                if row.get('Context Variables','') != '':
                    cv = row['Context Variables']
                    if isinstance(cv,str):
                       cv = json.loads(cv)
                    context.update(cv)

                if user_goes_first:
                    payload = { 'text': '' }
                    r = self.ctk.message(workspace_id=workspace_id, input=payload, context=context)
                    if version.startswith('2.'):
                      r = r.get_result()
                    context = r['context']

                results.append(r)
            else:
                if len(row.get('Alternate Intents','')) == 0:
                    ai = default_intents
                else:
                    ai = row['Alternate Intents']

                payload = { 'text' : row['User Input'] }

                # Build context variables.
                if row.get('Context Variables','') != '':
                    cv = row['Context Variables']
                    if isinstance(cv,str):
                       cv = json.loads(cv)
                    context.update(cv)

                r = self.ctk.message(workspace_id=workspace_id, input=payload, context=context, alternate_intents=ai)
                if version.startswith('2.'):
                    r = r.get_result()
                context = r['context']
                results.append(r)

        return results

    def runFlowTest(self, workspace_id=None, flow=None,json_dump=False,alternate_intents=True, intent_per_row=False, user_goes_first=False, show_progress=True, version='1.x'):
        flow = flow.fillna('')
        if json_dump == True:
            return self.jsonDumpFlowTest(workspace_id, flow)

        context = {}
        default_intents = alternate_intents

        df = self.createBlankReport()
        if alternate_intents:
            df = self.createAlternateIntentsColumns(df)

        innerText = ''

        if user_goes_first:
                payload = { 'text': '' }
                r = self.ctk.message(workspace_id=workspace_id, input=payload, context=context)
                if version.startswith('2.'):
                    r = r.get_result()
                context = r['context']
                record = {
                    'User Input': '',
                    'Output Text': '\n'.join(r['output']['text']),
                    'Context': r['context']
                    }
                df = df.append(record,ignore_index=True)

        for index, row in flow.iterrows():  # @UnusedVariable
            if show_progress:
                print('{} {}'.format(index, row['User Input']))
            if row.get('User Input','') == 'NEWCONVERSATION':
                self.lastTestResult()
                workspace_id=os.environ["WORKSPACE_ID"]
                context = {}
                if row.get('Context Variables','') != '':
                    cv = row['Context Variables']
                    if isinstance(cv,str):
                       cv = json.loads(cv)
                    context.update(cv)

                if user_goes_first:
                    payload = { 'text': '' }
                    r = self.ctk.message(workspace_id=workspace_id, input=payload, context=context)
                    if version.startswith('2.'):
                      r = r.get_result()
                    context = r['context']

                df = df.append({
                    'User Input': 'NEWCONVERSATION',
                    'Context': context
                },ignore_index=True)
            else:
                if len(row.get('Alternate Intents','')) == 0:
                    ai = default_intents
                else:
                    ai = row['Alternate Intents']

                payload = { 'text' : row['User Input'] }

                # Build context variables.
                if row.get('Context Variables','') != '':
                    cv = row['Context Variables']
                    if isinstance(cv,str):
                       cv = json.loads(cv)
                    context.update(cv)

                r = self.ctk.message(workspace_id=workspace_id, input=payload, context=context, alternate_intents=ai)
                if version.startswith('2.'):
                    r = r.get_result()
                context = r['context']

                if 'text' in r['output']:
                  innerText = r['output']['text']
                if row.get('Match Output','') != '':
                    row['Match Output'] = '<br>'.join(row['Match Output'].splitlines())
                    ouput_pattern = row['Match Output']
                    ouput_pattern = re.escape(ouput_pattern) if not ouput_pattern.startswith('/') else ouput_pattern[1:-1]
                    matchedOutput = bool(re.search(ouput_pattern, '<br>'.join(innerText), re.MULTILINE))
                    if matchedOutput == False:
                      self.reportFailure()
                else:
                    matchedOutput = "n/a"
                if len(r['intents']) > 0 and 'Match Intent' in row:
                    matchedIntent = bool(re.search(row['Match Intent'], r['intents'][0]['intent']))
                    if matchedIntent == False:
                      self.reportFailure()
                else:
                    matchedIntent = "n/a"

                entity_string = ''
                if len(r['entities']) > 0:
                    for e in r['entities']:
                        entity_string = u'{} {}:{}{}'.format(entity_string, e['entity'], e['value'], e['location'])

                if row.get('Match Entity','') != '':
                    matchedEntity = bool(re.search('.*?{}.*?'.format(row['Match Entity']), entity_string))
                    if matchedEntity == False:
                      self.reportFailure()
                else:
                    matchedEntity = "n/a"

                # If your orchestrator ever changes Watson Assistant workspaces, detect and reflect that here
                # workspace_id = new_workspace_id
                # del context['system']
                # del context['action']
                # print('\tJumped to workspace {}'.format(workspace_id))

                record = {
                    'User Input': row['User Input'],
                    'Output Text': '<br>'.join(r['output']['text']),
                    'Alternate Intents': ai,
                    'Conversation ID': r['context']['conversation_id'],
                    'Context': r.get('context'),
                    'Match Output': row.get('Match Output'),
                    'Match Intent': row.get('Match Intent'),
                    'Match Entity': row.get('Match Entity'),
                    'Matched Output': matchedOutput,
                    'Matched Intent': matchedIntent,
                    'Matched Entity': matchedEntity,
                    #'Matched Context': matchedContext,
                    'Entities': entity_string
                    }

                if ai:
                    df = self.createAlternateIntentsColumns(df)
                    for i in range(0,len(r['intents'])):
                        record.update({
                            'Intent{}'.format(i+1): r['intents'][i]['intent'],
                            'Confidence{}'.format(i+1): r['intents'][i]['confidence']
                            })

                if len(r['intents']) > 0:
                    record.update({
                        'Intent': r['intents'][0]['intent'],
                        'Confidence': r['intents'][0]['confidence']
                        })

                df = df.append(record,ignore_index=True)

        self.lastTestResult()

        df = df.fillna('')
        if intent_per_row:
            return self.convertReportToIntentPerRow(df)

        return df

    def convertReportToIntentPerRow(self, report=None,input_all_lines=True):
        """
        Converts a Report file to row by Recall@ (Intent). Will do nothing if alternate_intents was never set.
        :param report The Dataframe containing the report
        """

        cols = list(self.reportColList1) + list(self.reportColIntentList) + list(self.reportColList2)
        df = pd.DataFrame(columns=list(cols))


        for index, row in report.iterrows():  # @UnusedVariable
            record = row

            for i in range(1,11):
                if input_all_lines == False and i > 1:
                    record['User Input'] = ''

                record['Recall@'] = i
                record['Intent'] = row['Intent{}'.format(i)]
                record['Confidence'] = row['Confidence{}'.format(i)]

                # Match against current.
                if record['Match Intent'] != '':
                    record['Matched Intent'] = bool(re.search(row['Match Intent'], record['Intent{}'.format(i)]))
                else:
                    record['Matched Intent'] = False

                df = df.append(record, ignore_index=True)


        for i in range(1,11):
            df = df.drop('Intent{}'.format(i),1)
            df = df.drop('Confidence{}'.format(i),1)

        return df
