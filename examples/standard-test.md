# Standard Test without Ground Truth for Intents
## Story
The user wants to test a set of utterances against a trained Watson Assistant instance simply to get the intent and entity predictions.

## Prerequisite
There is one and only one column in `test_input_file.csv` containing the test utterances which is used for testing purpose.

## Input file
`config.ini`

```
[DEFAULT]
mode = TEST
workspace_id = 01234567-9ABC-DEF0-1234-56789ABCDEF0
test_input_file = ./data/test.csv
test_output_path = ./data/test-out.csv
temporary_file_directory = ./data
; Clean the workspaces after testing
keep_workspace_after_test = no


[ASSISTANT CREDENTIALS]
; If your WA environment provides username and password, configure them and leave iam_apikey empty
; If your WA environment provides iam_apikey, set the username value as: apikey and password value as: <the value of your apikey>
username = <wa username>
password = <wa password>
iam_apikey = <wa iam apikey>
url = https://gateway-wdc.watsonplatform.net/assistant/api

```
`test_input_file.csv`

| utterance   |
| ----------- |
| utterance 0 |

## Sample out
`test_output_path.csv`

| utterance   | predicted intent | confidence | detected entities                 | dialog response |
| ----------- | ---------------- | ---------- | --------------------------------- | --------------- |
| utterance 0 | intent 0         | 0.01       | entity 0:value 0;entity 1:value 1 | response 0      |
