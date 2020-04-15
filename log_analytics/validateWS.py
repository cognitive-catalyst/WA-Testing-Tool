import json
import sys
import os
import argparse
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from waObjects import DialogNode,Workspace

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def getKeys(prefix, dictionary):
   keys = []
   for key, value in dictionary.items():
      if(isinstance(value, dict)):
         keys.extend(getKeys(prefix + key + ".", value))
      else:
         keys.append(prefix + key)
   return keys

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
    if text != "" and 'jump_to' != dialogNode.getNextStep() and 'skip_user_input' != dialogNode.getNextStep():
        vgwCommands = dialogNode.getVoiceGatewayCommands()
        if vgwCommands == None or len(vgwCommands) == 0:
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
    if text != "" and 'jump_to' != dialogNode.getNextStep() and 'skip_user_input' != dialogNode.getNextStep():
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

###
# Conditions should generally not look at input.text - using an entity and/or intent is cleaner
###
def verifyNoInputTextConditions(dialogNode:DialogNode):
    conditions = dialogNode.getConditions()
    if conditions is not None and 'input.text' in conditions and 'length' not in conditions:
        print("WARN:\t{}\tDirectly checks 'input.text'. Consider using an entity or intent in the condition instead. Full condition: `{}`".format(dialogNode.getId(), conditions))


###
# If a node does not play text it should send a context action or a jump
# Webhooks and other integrations are checked in the context.action
###
def verifyNoDeadEnd(dialogNode:DialogNode, workspace:Workspace):
    text = dialogNode.getText()
    if len(text) == 0 and \
      'jump_to' != dialogNode.getNextStep() and \
      'skip_user_input' != dialogNode.getNextStep() and \
      'returns' != dialogNode.getDigressionType() and \
      not dialogNode.isMCR():
        #Potential dead-end.  There are some difficult-to-be-certain cases within here:
        #1: Digression logic may prevent a dead-end
        parent = workspace.getParentNode(dialogNode)
        digressionFound = False if parent is None else (parent.getDigressionType() is not None)
        while parent is not None and not digressionFound:
            parent = workspace.getParentNode(parent)
            digressionFound = False if parent is None else (parent.getDigressionType() is not None)

        #2: Context variables may specify output text (Voice Gateway integration) or commands for an orchestrator, either of which is not dead-end
        #   An 'action' is a giveaway that the conversation does not stop here
        #   Note that digression nodes may not use context so this must be an independent test

        context = dialogNode.getContext()
        deadendCausedByContext = (context == None or 'action' not in context)

        if digressionFound:
            print("WARN:\t{}\tDoes not play text, set an action, perform a jump and is not configured for MCR.  Inspect the digression settings in this node's ancestry to ensure it is not a dead-end node.".format(dialogNode.getId()))
        elif deadendCausedByContext:
            print("WARN:\t{}\tDoes not play text, set an action, perform a jump, is not configured for MCR, and does not occur in a digression.  It may be a dead end node.".format(dialogNode.getId()))
        #else (nothing to do - not actually a dead-end)

def buildJumpReport(workspace, jumpReportFile, jumpLabel):
   getTargetTitles = (jumpLabel == 'Both' or jumpLabel == 'Title')
   idToTitleDict = {}
   jumps = []
   for dialogNode in workspace.getDialogNodes():
       if(getTargetTitles):
          idToTitleDict[dialogNode.getId()] = dialogNode.getTitle()
       if 'jump_to' == dialogNode.getNextStep():
           behavior = dialogNode.data['next_step']
           type = behavior['selector'] #'body' or 'condition'

           #By ID first
           source = dialogNode.getId()
           target = behavior['dialog_node']
           jump = {'source':source, 'type':type, 'target':target}
           jumps.append(jump)

   outFile = open(jumpReportFile, 'w')
   header = 'Source\tType\tTarget'
   outFile.write(header+'\n')
   for jump in jumps:
       source = jump['source']
       target = jump['target']
       if('Title' == jumpLabel):
          source = idToTitleDict[source]
          target = idToTitleDict[target]
       if('Both' == jumpLabel):
          source = source + ":" + idToTitleDict[source]
          target = target + ":" + idToTitleDict[target]

       line = '{}\t{}\t{}'.format(source, jump['type'], target)
       outFile.write(line+'\n')
   outFile.close()
   print('Wrote jump report file to {}'.format(jumpReportFile))

def buildContextVariableReport(workspace):
   context_variables=set()
   for dialogNode in workspace.getDialogNodes():
      context = dialogNode.getContext()
      if context is not None:
          list_variables = getKeys("", context)
          context_variables.update(list_variables)

   print("Full context variable list:")
   for key in sorted(context_variables):
      print(key)

def getWorkspaceJson(args):
  if args.file and args.file[0]:
    jsonFile = open(args.file[0], 'r')
    return json.load(jsonFile)
  if args.online:
    VERSION='2018-09-20'
    authenticator = IAMAuthenticator(args.iam_apikey[0])
    service = AssistantV1(
        version=VERSION,
        authenticator=authenticator
    )
    service.set_service_url(args.url)

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
    parser.add_argument('--jump_report', help='Filename to print a report of all jumps in the workspace')
    parser.add_argument('--jump_labels', help='When building jump report, label the nodes by `ID|Title|Both`', default='Both')
    parser.add_argument('--context_variables', help='Print list of all context variables used in workspace', dest='context_variables', action='store_true')
    parser.add_argument('-a', '--iam_apikey', nargs=1, type=str, help='Assistant service IAM api key')
    parser.add_argument('-l', '--url', type=str, help='URL to Watson Assistant. Ex: https://gateway-wdc.watsonplatform.net/assistant/api')
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
    jumpReportFile = args.jump_report
    jumpLabel = args.jump_labels

    workspace = Workspace(jsonData)
    print('Input workspace is called "{}" and contains {} dialog nodes'.format(workspace.getTitle(), len(workspace.getDialogNodes())))

    for dialog in workspace.getDialogNodes():
        if(voiceValidation):
            validateVoiceGatewayCommands(dialog, expectedVoiceGatewayCommands)
            validateSTTConfiguration(dialog)
        if(soeValidation):
            validateRoute(dialog, validSOERoutes)
        #Standard tests
        verifyNoDeadEnd(dialog, workspace)
        verifyNoInputTextConditions(dialog)

    if(jumpReportFile is not None):
        buildJumpReport(workspace, jumpReportFile, jumpLabel)

    if(args.context_variables is True):
        buildContextVariableReport(workspace)
