import json
import sys
import os
import argparse
from watson_developer_cloud import AssistantV1

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def cleanValue(value:str):
    try:
        value = value.replace('</voice-transformation></speak>','')
        value = value.replace("<speak version='1.0'>",'')
        value = value.replace("<voice-transformation type='Custom' rate='25%'>",'')
        value = value.replace("<voice-transformation type='Custom' rate='35%'>",'')
        value = value.replace("\t",'')
        value = value.replace("\n",'')
        value = value.replace("    ",'')
        return value;
    except:
        return ""

class DialogNode:
    def __init__(self, jsonObject:json):
      self.data = jsonObject

    def getId(self):
        return self.data['dialog_node']

    def getTitle(self):
        return self.data['title']

    def getContext(self):
        return self.data.get('context')

    def getNextStep(self):
        if 'next_step' in self.data:
            if 'behavior' in self.data['next_step']:
                return self.data['next_step']['behavior']
        return None

    def getRoute(self):
        dialog_node = self.data
        if 'context' in dialog_node:
            if 'action' in dialog_node.get('context'):
                if 'route' in dialog_node.get('context').get('action'):
                    #print(json.dumps(dialog_node, indent=4, separators=(',', ': '), sort_keys=True))
                    try:
                        route = dialog_node.get('context').get('action').get('route')
                        return route
                    except:
                        print("ERROR:\t{}\tHas invalid action object".format(self.getId()))
        return None

    def getVoiceGatewayCommands(self):
        dialog_node = self.data
        vgw_action_list = []
        if 'output' in dialog_node:
            output_node = dialog_node.get('output')
            if 'vgwActionSequence' in output_node:
                for vgwNode in output_node['vgwActionSequence']:
                    try:
                        command = vgwNode['command']
                        vgw_action_list.append(command)
                    except:
                        print("ERROR:\t{}\tHas invalid vgwActionSequence command".format(self.getId()))
        return vgw_action_list

    def getText(self):
        dialog_node = self.data
        text = ""
        if 'output' in dialog_node:
            output_node = dialog_node.get('output')

            #first way to get text
            if 'text' in output_node:
                if 'values' in output_node['text']:
                    for value in output_node['text']['values']:
                        text = text + cleanValue(value)
                        textSource = "output text values"
                else:
                    text = text + cleanValue(output_node['text'])
                    textSource = "output text"
            #second way to get text
            if 'generic' in output_node:
                for generic in output_node['generic']:
                    if 'values' in generic:
                        for value in generic['values']:
                            text = text + cleanValue(value['text'])
                            textSource = "output generic values"

            #third way to get text - and how to get the other configs too
            if 'vgwActionSequence' in output_node:
                for vgwNode in output_node['vgwActionSequence']:
                    if 'parameters' in vgwNode:
                        if 'text' in vgwNode['parameters']:
                            #vgwActPlayText takes precedence, so reset any other text you see
                            #text = ""
                            for value in vgwNode['parameters']['text']:
                                if('[COPY.OUTPUT.TEXT.ARRAY]' != value):
                                    text = ""
                                text = text + cleanValue(value)
                                textSource = "vgwActPlayText"
        return text

class Workspace:
    def __init__(self, jsonData):
        self.data = jsonData

    def getTitle(self):
        return self.data['name']

    def getDialogNodes(self):
        enabled_node_list = []
        dialog_node_list = self.data['dialog_nodes']
        for dialog_node in dialog_node_list:
            if dialog_node.get('disabled') == True or dialog_node.get('disabled') == 'true':
                continue
            enabled_node_list.append(DialogNode(dialog_node))
        return enabled_node_list

def validateRoute(dialogNode:DialogNode, valid_routes:list):
    route = dialogNode.getRoute()
    if route not in valid_routes:
        print("WARN:\t{}\tHas invalid route '{}'".format(dialogNode.getId(), route))

# Command definition at https://www.ibm.com/support/knowledgecenter/en/SS4U29/api.html
# List as of Version 1.0.0.3, extracted from website on June 20 2019
legalVoiceGatewayCommands = ['vgwActPlayText','vgwActPlayUrl','vgwActHangup','vgwActSendSMS','vgwActSetSTTConfig','vgwActSetTTSConfig','vgwActSetConversationConfig','vgwActSetWVAConfig','vgwActTransfer','vgwActSendSIPInfo','vgwActCollectDTMF','vgwActPauseDTMF','vgwActUnPauseDTMF','vgwActExcludeFromTTSCache','vgwActPauseSTT','vgwActUnPauseSTT','vgwActDisableSTTDuringPlayback','vgwActEnableSTTDuringPlayback','vgwActDisableSpeechBargeIn','vgwActEnableSpeechBargeIn','vgwActDisableDTMFBargeIn','vgwActEnableDTMFBargeIn','vgwActForceNoInputTurn','vgwActEnableTranscriptionReport','vgwActDisableTranscriptionReport','vgwActAddCustomCDRData','vgwActSetTenantType']

###
# If a node plays text without doing a WA jump, it should use these Voice Gateway commands
###
def validateVoiceGatewayCommands(dialogNode:DialogNode, expectedVoiceGatewayCommands:list):
    text = dialogNode.getText()
    if text != "" and 'jump_to' != dialogNode.getNextStep():
        vgwCommands = dialogNode.getVoiceGatewayCommands()
        if vgwCommands == None:
            print("WARN:\t{}\tDoes not contain any Voice Gateway commands".format(dialogNode.getId()))
        else:
            for expected_command in expectedVoiceGatewayCommands:
                if expected_command not in vgwCommands:
                    print("WARN:\t{}\tDoes not contain command '{}'".format(dialogNode.getId(), expected_command))
            for command in vgwCommands:
                if command not in legalVoiceGatewayCommands:
                    print("WARN:\t{}\tContains command '{}' which is not in known commands list".format(dialogNode.getId(), command))

def validateSTTConfiguration(dialogNode:DialogNode):
    text = dialogNode.getText()
    if text != "" and 'jump_to' != dialogNode.getNextStep():
        #There are different ways to provide the STT customization variables, but there should be a vgwActSetSTTConfig action
        if 'output' in dialogNode.data and 'vgwActionSequence' in dialogNode.data['output']:
          vgwActionNodes = dialogNode.data['output']['vgwActionSequence']
          sttConfigFound = False
          for vgwNode in vgwActionNodes:
            if vgwNode['command'] == 'vgwActSetSTTConfig':
              sttConfigFound = True
              if 'parameters' in vgwNode:
                if 'config' not in vgwNode['parameters']:
                  print("WARN:\t{}\tDoes not provide config parameters to vgwActSetSTTConfig".format(dialogNode.getId()))
                print
              else:
                print("WARN:\t{}\tDoes not provide any parameters to vgwActSetSTTConfig".format(dialogNode.getId()))
              # Can detect customization_id directly here if specific variables are used
              #lm_id = vgwNode['parameters']['config']['customization_id']
              #if lm_id is None:
              #  print("WARN:\t{}\tDoes not contain STT language model customization ID".format(dialogNode.getId()))

          #This is a duplicate warning
          #if sttConfigFound != True:
          #  print("WARN:\t{}\tDoes not contain vgwActSetSTTConfig command".format(dialogNode.getId()))

        # #One specific project stored all customization in the dialog context as an object, then passed this object to the config
        # context = dialogNode.getContext()
        # if context != None and 'STT_CONFIG' in context:
        #     try:
        #         lm_id = context.get('STT_CONFIG').get('customization_id')
        #         am_id = context.get('STT_CONFIG').get('acoustic_customization_id')
        #         if lm_id is None:
        #             print("WARN:\t{}\tIs missing STT language model customization ID".format(self.getId()))
        #         if am_id is None:
        #             print("WARN:\t{}\tIs missing STT acoustic model customization ID".format(self.getId()))
        #     except:
        #         print("ERROR:\t{}\tHas invalid STT_CONFIG section".format(self.getId()))

def getWorkspaceJson(args):
  if args.file and args.file[0]:
    jsonFile = open(args.file[0], 'r')
    return json.load(jsonFile)
  if args.online:
    VERSION='2018-09-20'
    service = AssistantV1(username=args.username[0], password=args.password[0], version=VERSION, url=args.url[0])

    #Note: export=True is rate-limited, see https://cloud.ibm.com/apidocs/assistant?code=python#get-information-about-a-workspace
    response=service.get_workspace(workspace_id=args.workspace_id[0], export=True)

    #Check for v1 vs v2 syntax
    result_attr = getattr(response, "get_result", None)
    if callable(result_attr):
      response=response.get_result()

    return json.loads(json.dumps(response))

  sys.stderr.write('Invalid configuration, did not specify a workspace file or an online connection\n')
  sys.exit(2)

###
# Example usage
#   python validateWS.py -f my_workspace_json_file.json -s -g --voice_gateway_commands "vgwActSetSTTConfig,vgwActPlayText"
###
if __name__ == '__main__':
    parser = ArgParser(description='Validates a workspace against a set of rules')
    parser.add_argument('-f', '--file', nargs=1, type=str, help='Filepath to exported Watson Assistant workspace JSON file.')
    #store_true means there is no associated argument except the flag itself
    parser.add_argument('-o', '--online', action='store_true', help='Connect to Watson Assistant instance and extract workspace from online instance')
    parser.add_argument('-g', '--voice', action='store_true', help='Enables Voice Gateway response validation')
    parser.add_argument('-s', '--soe', action='store_true', help='Enables SOE response validation')
    parser.add_argument('--voice_gateway_commands', help='Comma-separated list of Voice Gateway commands expected on each text response node. Ex: "vgwActSetSTTConfig,vgwActPlayText"', default='vgwActSetSTTConfig,vgwActPlayText')
    parser.add_argument('--soe_routes', help='Comma-separated list of SOE action routes. Ex: "SOE,API,None"', default='SOE,API,None')
    parser.add_argument('-u', '--username', nargs=1, type=str, help='Username to Watson Assistant.')
    parser.add_argument('-p', '--password', nargs=1, type=str, help='Password to Watson Assistant.')
    parser.add_argument('-r', '--url', nargs=1, type=str, help='URL to Watson Assistant. Ex: https://gateway-wdc.watsonplatform.net/assistant/api')
    parser.add_argument('-w', '--workspace_id', nargs=1, type=str, help='ID of the Watson Assistant workspace')

    args = parser.parse_args()

    jsonData = getWorkspaceJson(args)
    soeValidation = args.soe
    voiceValidation = args.voice
    expectedVoiceGatewayCommands = args.voice_gateway_commands.split(',')
    validSOERoutes = args.soe_routes.split(',')
    if 'None' in validSOERoutes:
      validSOERoutes.remove('None')
      validSOERoutes.append(None)

    workspace = Workspace(jsonData)
    print('Input workspace is called "{}" and contains {} dialog nodes'.format(workspace.getTitle(), len(workspace.getDialogNodes())))

    for dialog in workspace.getDialogNodes():
        if(voiceValidation):
            validateVoiceGatewayCommands(dialog, expectedVoiceGatewayCommands)
            validateSTTConfiguration(dialog)
        if(soeValidation):
            validateRoute(dialog, validSOERoutes)
