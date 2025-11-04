import os
import json
import pandas as pd
from pandas import ExcelWriter
from argparse import ArgumentParser

# Reading Watson Assistant log files in .json format, each log event is a JSON record.
# Return a list of Watson Assistant log events.
def readLogs(inputPath, conversation_id_key='response.context.conversation_id', custom_field_names_comma_separated=None):
    """Reads all log event .json files in `inputPath` and its subdirectories."""
    if(os.path.isdir(inputPath)):
        data = pd.DataFrame()
        print('Processing input directory {}'.format(inputPath))
        for root, dirs, files in os.walk(inputPath):
            dirs.sort()
            files.sort()
            for file in files:
                if file.endswith('.json'):
                    logFile = os.path.join(root, file)
                    fileData = readLogsFromFile(logFile, conversation_id_key, custom_field_names_comma_separated)
                    if fileData is not None and len(fileData) > 0:
                        data = pd.concat([data, fileData], ignore_index=True)
        return data
    else:
        return readLogsFromFile(inputPath, conversation_id_key, custom_field_names_comma_separated)

def readLogsFromFile(filename, conversation_id_key='response.context.conversation_id', custom_field_names_comma_separated=None):
    """Reads all log events from JSON file `filename`."""
    print('Processing input file {}'.format(filename))
    with open(filename) as json_file:
        data = json.load(json_file)

    if data is not None and len(data) > 0:
       #If using `getAllLogs.py` you just get the array, the raw Watson API produces a field called 'logs' which contains the array
       if 'logs' in data:
           data = data['logs']
       return extractConversationData(data, conversation_id_key, custom_field_names_comma_separated)
    else:
       return None

#------------------------------------------------------------------------

# deep_get reads an arbitrarily-nested key sequence from a dictionary.
# getCustomFields' `key_list` turns "request.context.somevariable" into ["request","context","somevariable"]
# The combination allows extraction of arbitrary key-value sequences from the log event.

def deep_get(dct, keys, default=None):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
        except TypeError:
            return default
        except IndexError:
            return default
    return dct

def getFieldShortName(field_name):
    """ Simplifies `field_name` in the exported dataframe by removing Watson Assistant prefixes """
    return field_name.replace('request.','')         \
                     .replace('response.','')        \
                     .replace('context.system.','')  \
                     .replace('skills.','')          \
                     .replace('main skill.','')      \
                     .replace('user_defined.','')    \
                     .replace('context.','')         \
                     .replace('actions skill.','')   \
                     .replace('skill_variables.','')

# Caches information about custom fields so they do not need to be re-calculated on every log event.
# Example dictionary format is `{'request.response.XYZ': {'name': 'XYZ', 'key_list': ['request', 'response', 'XYZ']}}``

def getCustomFields(custom_field_names):
    customFields = {}
    for field_original_name in custom_field_names:
        field_short_name = getFieldShortName(field_original_name)
        field_keys_list = field_original_name.split(".")
        customFields[field_original_name] =  {'name':field_short_name, 'key_list':field_keys_list}

    return customFields

##------------------------------------------------------------------------
def logToRecord(log, customFields):
        record = {}
        record['conversation_id']          = log['response']['context']['conversation_id']
        #Location of dialog_turn_counter varies by WA version
        if 'system' in log['response']['context']:
            if 'dialog_turn_counter' in log['response']['context']['system']:
                record['dialog_turn_counter']  = log['response']['context']['system']['dialog_turn_counter']
            else:
                record['dialog_turn_counter']  = log['request']['context']['system']['dialog_turn_counter']
        elif 'global' in log['response']['context'] and 'dialog_turn_counter' in log['response']['context']['global']:
            record['dialog_turn_counter'] = log['response']['context']['global']['dialog_turn_counter']
        elif 'system' in log['request']['context'] and 'dialog_turn_counter' in log['request']['context']['system']:
            record['dialog_turn_counter']  = log['request']['context']['system']['dialog_turn_counter']
        else:
            record['dialog_turn_counter'] = None

        record['request_timestamp']        = log.get('request_timestamp', None)
        record['response_timestamp']       = log.get('response_timestamp', None)

        if 'text' in log['request']['input']:
            record['input.text']           = log['request']['input']['text']

        if 'text' in log['response']['output']:
            record['output.text']          = ' '.join(filter(None,log['response']['output']['text'])).replace('\r','').replace('\n','')
            # Options (button/responses), assumed to come after a descriptive text element
            if 'generic' in log['response']['output'] and len(log['response']['output']['generic']) > 1 and 'options' in log['response']['output']['generic'][1]:
                record['output.text'] += f" options:["
                for option in log['response']['output']['generic'][1]['options']:
                    labelText = option["label"]
                    record['output.text'] += f'"{labelText}",'
                record['output.text'] += "]"
            # Disambiguation: Needs to loop over `response.output.generic[].title` and each of `response.output.generic[i].suggestions[].label`
            if 'generic' in log['response']['output'] and len(log['response']['output']['generic']) > 0 and 'suggestions' in log['response']['output']['generic'][0]:
                record['output.text'] += f"{log['response']['output']['generic'][0]['title']}: "
                for suggestion in log['response']['output']['generic'][0]['suggestions']:
                    labelText = suggestion["label"]
                    record['output.text'] += f'"{labelText}",'
                record['output.text'] += ""

        if 'intents' in log['response'] and (len(log['response']['intents']) > 0):
            record['intent']               = log['response']['intents'][0]['intent']
            if 'confidence' in log['response']['intents'][0]:
                record['intent_confidence']    = log['response']['intents'][0]['confidence']
        if 'output' in log['response'] and 'intents' in log['response']['output'] and (len(log['response']['output']['intents']) > 0):
            record['intent']               = log['response']['output']['intents'][0]['intent']
            if 'confidence' in log['response']['output']['intents'][0]:
                record['intent_confidence']    = log['response']['output']['intents'][0]['confidence']

        if 'entities' in log['response'] and len(log['response']['entities']) > 0:
            record['entities']             = tuple ( log['response']['entities'] )
        if 'output' in log['response'] and 'entities' in log['response']['output'] and len(log['response']['output']['entities']) > 0:
            record['entities']             = tuple ( log['response']['output']['entities'] )

        if 'nodes_visited' in log['response']['output']:
            record['nodes_visited']        = tuple (log['response']['output']['nodes_visited'])
        elif 'debug' in log['response']['output'] and 'nodes_visited' in log['response']['output']['debug']:
            record['nodes_visited']        = tuple (log['response']['output']['debug']['nodes_visited'])
        elif 'debug' in log['response']['output'] and 'turn_events' in log['response']['output']['debug']:
            record['nodes_visited']        = getNodesVisited(log['response']['output']['debug']['turn_events'])
        else:
            record['nodes_visited']        = ()
        
        #Single variable in v1, multiple choices in v2
        if 'system' in log['response']['context'] and 'branch_exited_reason' in log['response']['context']['system']:
            record['branch_exited_reason'] = log['response']['context']['system']['branch_exited_reason']

        for field in customFields:
            key, value                     = customFields[field]['name'], customFields[field]['key_list']
            record[key]                    = deep_get(log, value)
        
        return record

def getNodesVisited(turn_events):
    nodes_visited = list()
    for turn_event in turn_events:
        if 'source' in turn_event and 'event' in turn_event and 'step_visited' == turn_event['event']:
            action = turn_event['source'].get('action', None)
            step   = turn_event['source'].get('step', None)
            if step is None:
                nodes_visited.append(action)
            else:
                nodes_visited.append(f"{action}_{step}")

    return nodes_visited

def extractConversationData(logs, conversation_id_key='response.context.conversation_id', custom_field_names_comma_separated=None):
    # Parse custom field names from argument list
    if custom_field_names_comma_separated is None:
        custom_field_names = []
    else:
        custom_field_names = custom_field_names_comma_separated.split(',')

    # Determine conversation primary key and make sure we extract it from log records
    if conversation_id_key == 'response.context.conversation_id':
        primarySortField = 'conversation_id'
    else:
        primarySortField = getFieldShortName(conversation_id_key)
        if conversation_id_key not in custom_field_names:
            custom_field_names.insert(0, conversation_id_key)

    customFields = getCustomFields(custom_field_names)

    # Summarize each Watson Assistant log event into a more workable conversational record
    conversation_records_list = [logToRecord(log, customFields) for log in logs]
    df = pd.DataFrame(conversation_records_list)

     #converting date fields. 
    
    df['request_timestamp']  = pd.to_datetime(df['request_timestamp'])
    df['response_timestamp'] = pd.to_datetime(df['response_timestamp'])
    if 'intent_confidence' in df:
        df['intent_confidence'] = pd.to_numeric(df["intent_confidence"], errors='coerce')
        df['intent_confidence'] = df['intent_confidence'].fillna(0.0)
        df[df['intent_confidence']=='']=0.0

    # Lastly sort by conversation ID, and then request, so that the logs become readable. 
    df = df.sort_values([primarySortField, 'request_timestamp'], ascending=[True, True]).reset_index(drop=True)
    
    # cleaning up dataframe. Removing NaN
    df = df.fillna('')

    # Augment the data frame with additional derived columns useful for analysis
    df = augment_previous_nodes_visited(df, primarySortField)
    df = augment_conversation_and_message_times(df, primarySortField)
    df = augment_sequence_numbers(df, primarySortField)
    df = augment_previous_output_text(df, primarySortField) #Shows what bot said (previous output.text) to which user responded (input.text)

    df = reorder_columns(df)

    return df

def reorder_columns(df):
    df = move_col_before_col(df, "input.text", "prev_output.text")
    df = move_col_before_col(df, "request_timestamp", "duration_ms")
    return df

def move_col_before_col(df, col1:str, col2:str):
    cols = list(df.columns)
    if col1 not in cols or col2 not in cols:
        print(f"WARNING: Both '{col1}' and '{col2}' must be in the DataFrame columns, to reorder them.")
        return df

    # Remove col2 from its current position
    cols.remove(col2)

    # Find the index of col1
    index = cols.index(col1)

    # Insert col2 just before col1
    cols.insert(index, col2)

    # Reorder the DataFrame
    return df[cols]

def augment_previous_nodes_visited(inputDF:pd.DataFrame, conversation_sort_key:str) -> pd.DataFrame:
    '''
    Several analyses require comparing the previous response node_visited to the current request objects
    This method supports those analyses by creating a `prev_nodes_visited` field shifted from the original `nodes_visited` field.
    To correlate a request.input field with response.nodes_visited of the previous request, use the new `prev_nodes_visited` field instead.
    '''
    df = inputDF.copy()
    df['prev_nodes_visited'] = df.groupby(conversation_sort_key)['nodes_visited'].shift(1).fillna('')
    
    return df

def augment_previous_output_text(inputDF:pd.DataFrame, conversation_sort_key:str) -> pd.DataFrame:
    '''
    Several analyses require comparing the previous response node_visited to the current request objects
    This method supports those analyses by creating a `prev_output.text` field shifted from the original `output.text` field.
    To correlate a request.input field with response.output.text of the previous request, use the new `prev_output.text` field instead.
    '''
    df = inputDF.copy()
    df['prev_output.text'] = df.groupby(conversation_sort_key)['output.text'].shift(1).fillna('')
    
    return df

def augment_conversation_and_message_times(inputDF:pd.DataFrame, conversation_sort_key:str) -> pd.DataFrame:
    '''
    Each conversation log has an absolute request and response timestamp.
    We wish to create timestamps relative to the start of the conversation session.

    This method adds new fields to every record in the data frame:
    `conversation_start`: The start time of the conversation under review
    `message_start`: The time the user started this message, relative to the beginning of the conversation
    `message_end`: The time the user sent this message, relative to the beginning of the conversation
    
    There are two special considerations:
    1: The user does not speak in turn 0, so all the relative timestamps should be 0:00
    2: Watson Assistant compute time is between request_timestamp and response_timestamp,
       therefore user response time is betweeen previous response_timestamp and current request_timestamp
    '''
    df = inputDF.copy()
    
    #Warning - this changes the 'type' of the conversation_start column
    df['conversation_start'] = df.groupby(conversation_sort_key)['request_timestamp'].transform('min')

    #Pairs each log with the response time of the previous log
    df['last_message_end'] = df.groupby(conversation_sort_key)['response_timestamp'].shift(1)
    
    #A 'min' last_message_end is required or else later arithmetic fails
    base_timestamp = df['conversation_start'].min()
    df['last_message_end'] = df['last_message_end'].fillna(pd.to_datetime(base_timestamp))

    #Need to match up types on conversation_start and last_message_end or later arithmetic fails
    df['last_message_end'] = pd.to_datetime(df['last_message_end'],utc=True)
    
    #TurnStart == LastTurnEnd except for the first turn of each conversation, which uses conversation_start
    df['absolute_message_start'] = df[['conversation_start','last_message_end']].max(axis=1)

    #The arithmetic we were actually interested in. Optionally add `.apply(lambda x:str(x)[7:18])` at on each result for cleaner formatting
    df['message_start'] = df['absolute_message_start'] - df['conversation_start']
    df['message_end']   = df['request_timestamp'] - df['conversation_start']
    df['duration_ms'] = df['message_end'] - df['message_start']
    df['duration_ms'] = df['duration_ms'].apply(lambda x: x.total_seconds()*1000 if pd.notna(x) else 0)

    return df.drop(['last_message_end', 'absolute_message_start'], axis=1)

def augment_sequence_numbers(inputDF:pd.DataFrame, conversation_sort_key:str) -> pd.DataFrame:
    '''
    For multi-skill conversation the dialog_turn_number field is not directly usable as it is relative to a single workspace.

    This method adjusts `dialog_turn_number` according to the entire conversation.

    Additionally this method sets `conversation_length` on each record which is equal to the total length of the conversation
    '''
    df = inputDF.copy()

    # Sets the `dialog_turn_number` across all workspaces within a conversation
    df['dialog_turn_number'] = df.groupby(conversation_sort_key).cumcount() + 1
    
    # Sets the length of the conversation
    df['conversation_length'] = df.groupby(conversation_sort_key)['dialog_turn_number'].transform('max')

    # Marks if a turn is the last in the conversation
    df['is_final_turn'] = df['dialog_turn_number']  == df.groupby(conversation_sort_key)['dialog_turn_number'].transform('max')

    return df

def writeFrameToFile(df, output_file):
    print("Writing output file {}".format(output_file))
    if(output_file.endswith(".pkl")):
        df.to_pickle(output_file)
    elif output_file.endswith(".xlsx"):
        with ExcelWriter(output_file, engine='openpyxl') as writer:
            df['request_timestamp']  = pd.to_datetime(df['request_timestamp'] ).dt.tz_localize(None)
            df['response_timestamp'] = pd.to_datetime(df['response_timestamp']).dt.tz_localize(None)
            df['conversation_start'] = pd.to_datetime(df['conversation_start']).dt.tz_localize(None)
            
            # Format timedelta columns for Excel display
            if 'message_start' in df.columns:
                df['message_start'] = df['message_start'].apply(lambda x: str(x).split('.')[0] if pd.notna(x) else '00:00:00')
            if 'message_end' in df.columns:
                df['message_end'] = df['message_end'].apply(lambda x: str(x).split('.')[0] if pd.notna(x) else '00:00:00')
            
            df.to_excel(writer, index=False, sheet_name='Messages')
            worksheet = writer.sheets['Messages']

            # Auto-adjust column widths
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(0.8*length,25)


    else:
        df.to_csv(output_file,index=False)
    print("Wrote output file {}".format(output_file))

##------------------------------------------------------------------------

def create_parser():
    parser = ArgumentParser(description='Parses Watson Assistant logs and extracts most relevant fields for conversation analysis')
    parser.add_argument('-i', '--input_file', required=True, default='input.json', type=str, help='Filename or directory containing JSON logs')
    parser.add_argument('-o', '--output_file', required=True, default='conversations.csv', type=str, help='Filename to write CSV results to')
    parser.add_argument('-c', '--conversation_id', default="response.context.conversation_id", type=str, help='Key of conversation unique identifier')
    parser.add_argument('-f', '--custom_fields', help='Comma-separated list of fully qualified variable name to extract from log (ex: "response.context.my_variable,response.context.my_other_variable")')    

    return parser

if __name__ == '__main__':
   ARGS = create_parser().parse_args()

   logRecords  = readLogs(ARGS.input_file, ARGS.conversation_id, ARGS.custom_fields)
   writeFrameToFile(logRecords, ARGS.output_file)
