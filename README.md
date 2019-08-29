# WA-Testing-Tool
Scripts that run against Watson Assistant for 
  - `KFOLD` K fold cross validation on training set,
  - `BLIND` Evaluating a blind test, and
  - `TEST` Testing the WA against a list of utterances.

In the case of a k-fold cross validation, or a blind set, the tool will output
a [precision curve](precision_curve.md), in addition to per-intent true positive
and positive predictive value rates, and a confustion matrix.

## Features
- Easy to setup in one configuration file.
- Save the state when Assistant service is down in the middle of processing.
- Able to resume from where it stops using modularized scripts.

## Prerequisite
- *nix OS (Recommend)
- Python 3.6.4 +

## Quick Start
1. Install dependencies `pip install -r requirements.txt`
2. Set up parameters properly in `config.ini`.
3. Run the process. `python run.py -c <path to config.ini>`

## Input File
`config.ini` - Configuration file for `run.py`. Below is the template.

```
[DEFAULT]
; KFOLD, BLIND or TEST
mode = <one of the three options above>
; workspace_id or workspace JSON of target testing instance
workspace_id = 01234567-9ABC-DEF0-1234-56789ABCDEF0
; Test input file for blind and standard test
test_input_file = ./data/test.csv
; Previous blind test out
previous_blind_out = ./data/previous_blind_out.csv
; Test output path for blind and standard test
test_output_path = ./data/test-out.csv
; All temporary files/states will be stored here
temporary_file_directory = ./data
; Figure path for kfold and blind test
out_figure_path= ./data/figure.png
; number of folds
fold_num = 5
; Keep or delete the workspaces after testing. Use 'yes' or 'no'
keep_workspace_after_test = no
; POPULATION, EQUAL or WEIGHT_FILE
weight_mode = population
; Test request rate
max_test_rate = 100
; Threshold of confidence used for plotting the precision curve
conf_thres = 0.2
; Partial Credit Table
partial_credit_table = ./data/partial-credit-table.csv


[ASSISTANT CREDENTIALS]
; If your WA environment provides username and password, configure them and leave iam_apikey empty
; If your WA environment provides iam_apikey, set the username value as: apikey and password value as: <the value of your apikey>
username = <wa username> | apikey
password = <wa password> | <wa apikey>
iam_apikey =             | <wa apikey>
; Set the base URL for your WA environment
url = https://gateway.watsonplatform.net/assistant/api
```

`previous_blind_out.csv` (optional) - Test output from the previous classifier, which uses the same blind set as these in `test_input_file`.

| confidence           | does intent match |
| -------------------- | ----------------- |
| 0.01                 | yes               |
| 0.90                 | no                |
| 0.09                 | yes               |

`test_input_file.csv` - Test set for blind testing and standard test.

For blind test with golden intent used for comparison:

| utterance            | golden intent                            |
| -------------------- | ---------------------------------------- |
| utterance 0          | intent 0                                 |
| utterance 1          | intent 0                                 |
| utterance 2          | intent 1                                 |

For standard test, the input must only have one column or error will be thrown:

| utterance (implicit) |
| -------------------- |
| utterance 0          |
| utterance 1          |
| utterance 2          |


## Examples
[Run k fold validation](examples/kfold.md)

[Run blind test](examples/blind.md)

[Run standard test without ground truth](examples/standard-test.md)

[Generate description for intents](examples/intent-description.md)

[Generate precision/recall for classification test](examples/intent-metrics.md)

[Generate confusion matrix for classification test](examples/confusion-matrix.md)

[Generate long-tail classification results](examples/long-tail-scoring.md)

## Caveats
Due to different coverage among service plans, user may need to adjust `max_test_rate` accordingly to avoid network connection error.
