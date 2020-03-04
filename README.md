# WA-Testing-Tool
Scripts that run against Watson Assistant for
  - `KFOLD` K fold cross validation on training set,
  - `BLIND` Evaluating a blind test, and
  - `TEST` Testing the WA against a list of utterances.

In the case of a k-fold cross validation, or a blind set, the tool will output
a [precision curve](precision_curve.md), in addition to per-intent precision and recall rates, and a confusion matrix.

## Features
- Easy to setup in one configuration file.
- Save the state when Assistant service is down in the middle of processing.
- Able to resume from where it stops using modularized scripts.

## Prerequisite
- Python 3.6.4 +
- Mac users: you may need to initialize Python's SSL certificate store by running `Install Certificates.command` found in `/Applications/Python`.  See more [here](https://github.com/cognitive-catalyst/WA-Testing-Tool/issues/38)
- Git client


## Quick Start
Pre-work: Make sure to cd into the location of a projects folder, where you will clone this github repo.  Within the folder, cd into the WA-Testing-Tool folder. 
1. Install code  `git clone https://github.com/cognitive-catalyst/WA-Testing-Tool.git`
2. Install dependencies `pip3 install --upgrade -r requirements.txt`
3. Set up parameters properly in configuration file (ex: `config.ini`). Use `config.ini.sample` to bootstrap your configuration.
  a. In your terminal, copy the config file into a new one, `cp config.ini.sample config.ini`
  b. Open the config.ini file in your favorite text editor, edit and save the following information with your actual credentials: 
      API Key
      url
      workspace_id
  c. Set the mode and the mode-specific parameters.
4. Run the process. `python3 run.py -c config.ini` or `python3 run.py -c <path to your config file>`

## Quick Update
If you have already installed this utility use these steps to get the latest code.
1. Upgrade dependencies `pip3 install --upgrade -r requirements.txt`
2. Update to latest code level `git pull`

## Input Files
`config.ini` - Configuration file for `run.py`.
This is formatted differently for each mode.  Review the Examples below to explore the possible modes and how each is configured.

`test_input_file.csv` - Test set for blind testing and standard test.

For blind test with golden intent used for comparison:

| utterance            | golden intent                            |
| -------------------- | ---------------------------------------- |
| utterance 0          | intent 0                                 |
| utterance 1          | intent 0                                 |
| utterance 2          | intent 1                                 |

For standard test, the input must only have one column or error will be thrown:

| utterance            |
| -------------------- |
| utterance 0          |
| utterance 1          |
| utterance 2          |


## Examples
There are a variety of ways to use this tool.  Primarily you will execute a k-folds, blind, or standard test.
### Core execution modes
[Run k-fold cross-validation](examples/kfold.md)

[Run blind test](examples/blind.md)

[Run standard test without ground truth](examples/standard-test.md)

### Extended modes (executed by default)
[Generate precision/recall for classification test](examples/intent-metrics.md)

[Generate confusion matrix for classification test](examples/confusion-matrix.md)

### Extended modes
[Generate description for intents](examples/intent-description.md)

[Generate long-tail classification results](examples/long-tail-scoring.md)

[Unit test dialog flows](dialog_test/README.md)

[Run syntax validation patterns on a workspace](validate_workspace/README.md)

[Extract and analyze Watson Assistant log data](log_analytics/README.md)

## Testing Natural Language Classifier
This tool can also be used to test a trained Natural Language Classifier (NLC). The configuration is similar to testing Watson Assistant except:
1. Use the NLC URL in the `url` parameter (ex: `https://api.us-south.natural-language-classifier.watson.cloud.ibm.com`)
2. Specify the `<classifier_id>` in the `workspace_id` parameter in the configuration
3. Since NLC does not support downloading training data, the original training data must be provided if run in 'kfold' mode (using the `train_input_file` parameter)

## General Caveats and Troubleshooting
1. Due to different coverage among service plans, user may need to adjust `max_test_rate` accordingly to avoid network connection error.

2. Users on Lite plans are only able to create 5 workspaces.  They should set `fold_num=3` on their k-fold configuration file.

3. In case of interrupted execution, the tool may not be able to clean up the workspaces it creates.  In this case you will need to manually delete the extra workspaces.

4. Workspace ID is *not* the Skill ID.  In the Watson Assistant user interface, the Workspace ID can be found on the Skills tab, clicking the three dots (top-right of skill), and choosing View API Details.

5. SSL: [CERTIFICATE_VERIFY_FAILED] on Mac means you may need to initialize Python's SSL certificate store by running `Install Certificates.command` found in `/Applications/Python`.  See more [here](https://github.com/cognitive-catalyst/WA-Testing-Tool/issues/38)

6. "This utility used to work and now it doesn't." Upgrade to latest dependencies with `pip3 install --upgrade -r requirements.txt` and latest code with `git pull`.

7. If you get a Python module loading error, confirm that you are using matching pip and python version, ie `pip3` and `python3` or `pip` and `python`.
