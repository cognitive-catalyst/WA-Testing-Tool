# Standard Test without Ground Truth for Intents
## Story
The user wants to run against a trained instance simply to get the prediction.

## Prerequisite
The is one and only one column in `test_input_file.csv`, which is used for testing purpose.

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
username = <wa username>
password = <wa password>

```
`test_input_file.csv`

## Sample out
`test_output_path.csv`

| utterance   | predicted intent | confidence | detected entities                 | dialog response |
| ----------- | ---------------- | ---------- | --------------------------------- | --------------- |
| utterance 0 | intent 0         | 0.01       | entity 0:value 0;entity 1:value 1 | response 0      |
