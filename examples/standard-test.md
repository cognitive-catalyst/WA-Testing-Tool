# Standard Test without Ground Truth for Intents
## Story
The user wants to test a set of utterances against a trained Watson Assistant instance simply to get the intent and entity predictions.

## Prerequisite
There is one and only one column in `test_input_file.csv` containing the test utterances which is used for testing purpose.

## Input file
`config.ini` (fill in your `iam_apikey`, `url`, and `workspace_id` at minimum. (Older instances use a url like "https://gateway-wdc.watsonplatform.net/assistant/api")

```
[ASSISTANT CREDENTIALS]
iam_apikey = <wa iam apikey>
url = https://api.us-east.assistant.watson.cloud.ibm.com
version=2019-02-28

[DEFAULT]
mode = test
workspace_id = 01234567-9ABC-DEF0-1234-56789ABCDEF0

; optional - defaults shown here
;output_directory = ./data
;test_input_file = ./data/input.csv
;test_output_path = ./data/test-out.csv
;keep_workspace_after_test = no
```

Sample `test_input_file.csv`

| utterance   |
| ----------- |
| utterance 0 |

## Sample out
`test_output_path.csv`

| utterance   | predicted intent | confidence | detected entities                 | dialog response |
| ----------- | ---------------- | ---------- | --------------------------------- | --------------- |
| utterance 0 | intent 0         | 0.01       | entity 0:value 0;entity 1:value 1 | response 0      |
