# Blind Set Testing
## Story
Given an training set of Assistant intents with optional entities set, the user wants to test its performance by using a blind set.

## Workflow
Unlike k fold process, no separate folds will be created. Only one workspace is going to be trained using all of the training set. After the testing, both the test output and the `previous_test_out` are feed into `createPrecisionCurve.py` for plotting curves.

## Input file
`config.ini`

```
[DEFAULT]
mode = BLIND
workspace_id = 01234567-9ABC-DEF0-1234-56789ABCDEF0
test_input_file = ./data/test.csv
; optional
previous_blind_out = ./data/previous_blind_out.csv
test_output_path = ./data/test-out.csv
temporary_file_directory = ./data
; Figure path for kfold and blind test
out_figure_path= ./data/figure.png
; Clean the workspaces after testing
keep_workspace_after_test = no


[ASSISTANT CREDENTIALS]
username = <wa username>
password = <wa password>

```

`test_input_file` - Blind test set.

`previous_blind_out` - (Optional) Test output from previous blind test result.


## Sample output
![Blind curves](../resources/blind-curves.png)
