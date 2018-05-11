# WA-Testing-Tool
Scripts that run against Watson Assistant for K fold validation on training set, testing on blind test, and draw precision curves for comparison.

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
; Provide either workspace_json_dump or (intent_train_file and entity_train_file)
workspace_json_dump = ./data/workspace-sample.json
intent_train_file = ./data/intent_train_file.csv
; Optional if you don't have entities to load into WCS
entity_train_file = ./data/entity_train_file.csv
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
; Threshold of confidence
conf_thres = 0.2


[ASSISTANT CREDENTIALS]
username = <wa username>
password = <wa password>
```


`intent_train_file.csv` - Training set of Assistant intents. Same as the format of WCS intents import.

| utterance (implicit) | intent (implicit) |
| -------------------- | ----------------- |
| utterance 0          | intent 0          |
| utterance 1          | intent 0          |
| utterance 2          | intent 1          |

`entity_train_file.csv` (optional) - Training set of Assistant entities. Same as the format of WCS entities import.

| entity name (implicit) | value (implicit) | synonym/pattern 0 (implicit) | ... | synonym/pattern n (implicit) |
| ---------------------- | ---------------- | ---------------------------- | --- | ---------------------------- |
| entity 0               | value 0          | synonym                      | ... | synony                       |
| entity 0               | value 1          | /pattern 0/                  | ... | /pattern n/                  |
| entity 1               | value 2          | /patter  0/                  | ... | /patter  n/                  |

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

## Architecture

![Script Flow](resources/script-architecture.png)

## Caveats
Due to different coverage among service plans, user may need to adjust `max_test_rate` accordingly to avoid network connection error.
