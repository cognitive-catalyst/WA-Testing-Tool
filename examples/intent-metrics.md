# Intent classification summary metrics

## Story
Given an existing set of intent testing results, the user wants to determine the performance of each intent, particularly the 'precision' (positive predictive value), 'recall' (true positive rate), and 'f-score'.  From this performance the user can decide which intents need further training or revision.

## Workflow
There are two starting possibilities:

1) The user has run existing [k-folds](kfold.md) or [blind](blind.md) test which creates a summary .csv file

2) The user has a separate analysis which creates a .csv file with "golden" and "predicted" columns

User executes `intentmetrics.py` providing an input filename and output filename.  If using workflow 2, the user provides the names of the golden and predicted column header names with `-g` and `-t` respectively.
The summary is written to the output filename.

## Prerequisite
User must have an input .csv file containing at least two column headers representing "golden" and "predicted" filenames.

## Invocation
Workflow #1
Assuming input file at `data/test-out.csv` created by other tools in this repository and writing to `test-out-metrics.csv'.

```
python3 utils/intentmetrics.py -i data/test-out.csv -o data/test-out-metrics.csv
```

Workflow #2
Assuming input file at `data/golden_vs_predicted.csv` and writing to `data/golden_vs_predicted_metrics.csv`.  Since a different tool has created the input file we need to specify the names of the golden and predicted column headers which otherwise default to "golden intent" and "predicted intent".


`data/golden_vs_predicted.csv` example contents

```
"predicted","golden"
"intent1","intent1"
"intent1","intent2"
"intent1","intent2"
"intent2","intent2"
"intent2","intent2"
```

Invoke via:
```
python3 utils/intentmetrics.py -i data/golden_vs_predicted.csv -o data/golden_vs_predicted-metrics.csv -t "predicted" -g "golden"
```

## Sample output
Assuming the small example file `data/golden_vs_predicted.csv` above, this CSV is generated
```
"intent","number of samples","recall","precision","f-score"
"intent1","1","1.0","0.3333333333333333","0.5"
"intent2","3","0.3333333333333333","1.0","0.6666666666666666"
```

This mode also generates a treemap where:
* SIZE of box relates to number of samples for that intent
* COLOR of box relates to the accuracy for that intent

The treemap is organized such that the worst performing intents (by f-score) are located towards the top-right and the best performing are towards the bottom left.

Using a [larger example file](../resources/example-kfold-test-out-union.csv) we get the following treemap:

![Example treemap](../resources/treemap.png)
