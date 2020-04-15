import json

class DialogNode:
    def __init__(self, jsonObject:json):
      self.data = jsonObject

    def getId(self):
        return self.data['dialog_node']

    def getPreviousSibling(self):
        if 'previous_sibling' in self.data:
            return self.data['previous_sibling']
        return None

    def getParent(self):
        if 'parent' in self.data:
            return self.data['parent']
        return None

    def getTitle(self):
       try:
           return self.data['title']
       except:
           try:
                return self.data['conditions']
           except:
                return DialogNode.getId(self)

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

    def isMCR(self):
        '''Is this node a multi-condition response node'''
        dialog_node = self.data
        if 'metadata' in dialog_node:
            if '_customization' in dialog_node.get('metadata'):
                if 'mcr' in dialog_node.get('metadata').get('_customization'):
                    #print(json.dumps(dialog_node, indent=4, separators=(',', ': '), sort_keys=True))
                    try:
                        mcr = dialog_node.get('metadata').get('_customization').get('mcr')
                        return mcr
                    except:
                        print("ERROR:\t{}\tHas invalid action object".format(self.getId()))
        return False

    def getConditions(self):
        if 'conditions' in self.data:
            return self.data['conditions']
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
                    if 'title' in generic:
                       text = text + cleanValue(generic['title'])
                       textSource = "output generic title"
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

    def getDigressionType(self):
        if 'digress_in' in self.data:
            return self.data['digress_in']
        return None

class Workspace:
    def __init__(self, jsonData):
        self.data = jsonData
        self.nodeMap = {}

    def lazyInitNodeMap(self):
        #Lazy init for future calls
        if self.nodeMap == {}:
            node_list = self.getDialogNodes()
            for node in node_list:
                self.nodeMap[node.getId()] = node

    def getParentNode(self, node):
        if node.getParent() is None:
            return None

        self.lazyInitNodeMap()

        parent = self.nodeMap.get(node.getParent(), None)
        return parent

    def getTitle(self):
        return self.data['name']

    def getDialogNode(self, nodeId):
        self.lazyInitNodeMap()
        if nodeId in self.nodeMap:
            return self.nodeMap[nodeId]
        return None

    def getDialogNodes(self):
        enabled_node_list = []
        dialog_node_list = self.data['dialog_nodes']
        for dialog_node in dialog_node_list:
            if dialog_node.get('disabled') == True or dialog_node.get('disabled') == 'true':
                continue
# Commented out lines prevent extraction of folders
#             if 'type' not in dialog_node or dialog_node.get('type') != 'standard':
#                 continue
            enabled_node_list.append(DialogNode(dialog_node))
        return enabled_node_list

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