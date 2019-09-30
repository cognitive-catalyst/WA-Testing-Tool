# Long tail classification intent scoring

## Story
Given an existing set of intent testing results, and a short-tail/long-tail chat bot, the user wants to determine which utterances are routed to short-tail intents and which are routed to long tail intents.  (Typically, Watson Assistant answers short-tail questions and Watson Discovery answers long-tail questions.  Commonly, a question is deemed "long tail" if the intent classification result has low confidence.)

## Workflow
There are two starting possibilities:

1) The user has run existing [k-folds](kfold.md), [test](standard-test.md), or [blind](blind.md) test which creates a summary .csv file

2) The user has a separate analysis which creates a .csv file with "golden", "predicted", and "confidence" columns

User executes `longtailscoring.py` providing an input filename and output filename.  If using workflow 2, the user provides the names of the golden, predicted, and confidence column header names with `-g`, `-t`, and `-c` respectively.
The summary is written to the output filename.

The user may also set a confidence threshold (tau) with `-l` and a long-tail intent name with `-n`

## Prerequisite
User must have an input .csv file containing at least three column headers representing "golden", "predicted", and "confidence" columns.

## Invocation
Workflow #1
Assuming input file at `data/blind-out.csv` created by other tools in this repository and writing to `blind-out-metrics.csv'.

```
python3 utils/longtailscoring.py -i data/blind-out.csv -o data/blind-out-metrics.csv
```

Workflow #2
Assuming input file at `data/golden_vs_predicted.csv` and writing to `data/golden_vs_predicted_metrics.csv`.  Since a different tool has created the input file we need to specify the names of the golden, predicted, and confidence column headers which otherwise default to "golden intent", "predicted intent", and "confidence".


`data/golden_vs_predicted.csv` example contents

```
"predicted","golden","conf"
"intent1","intent1","0.9"
"intent1","intent2","0.4"
"intent1","intent2","0.8"
"intent2","intent2","0.6"
"intent2","intent2","0.7"
```

Invoke via:
```
python3 utils/longtailscoring.py -i data/golden_vs_predicted.csv -o data/golden_vs_predicted-metrics.csv -t "predicted" -g "golden" -c "conf" -l 0.5 -n "out_of_scope"
```

## Sample output
```
"predicted","golden","conf"
"intent1","intent1"
"intent1","out_of_scope"
"intent1","intent2"
"intent2","intent2"
"intent2","intent2"
```
