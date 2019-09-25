# K Fold Cross Validation Use Case

## Story
Given an existing training set of utterances mapped to intents, the user wants to perform a 5 fold cross validation and visualize the precision at different percentage of questions being answered.

## Workflow
By starting `run.py` with provided `config.ini`, `createTestTrainFolds.py` will create 5 folders with each fold's training and testing data under the `temporary_file_directory`. Then, `trainConversation.py` is going to training 5 workspaces and save the workspace infomation under the folds' folders. `testConversation.py` will be invoked right after the previous step is completed and save the test output into corresponding fold folders. Finally, the `createPrecisionCurve.py` will read the test outputs and save to `out_figure_path`.

Further, reports are generated for an [intent metrics summary](intent-metrics.md) and a [confusion matrix](confusion-matrix.md).  These include additional summaries and visualizations that help determine the strength and weaknesses of the training set.

## Prerequisite
User's workspace must allow to create 5 more workspaces. For 'lite' plans, use 3 folds instead (`fold_num=3`)

## Input file
`config.ini`

```
[DEFAULT]
mode = KFOLD
workspace_id = 01234567-9ABC-DEF0-1234-56789ABCDEF0
temporary_file_directory = ./data
out_figure_path= ./data/figure.png
; number of folds
fold_num = 5
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

## Sample output
![KFold curves](../resources/kfold-curves.png)
