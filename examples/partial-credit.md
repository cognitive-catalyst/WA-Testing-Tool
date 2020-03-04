# Partial Credit Intent Scoring

## Story
A user wants more than one predicted intent to be considered as correct in the blind or k-fold tests. An input file is used where the correct golden intent is mapped to other intents that are partially or fully correct.

This is primarily true in the case of similar or overlapping intents. Users may wish to give the system "credit" for picking one intent out of a multi-intent utterance.

## Prerequisite

Partial credit intent scoring is optional and if needed can be used in [blind](blind.md) or a [ k-fold](kfold.md) tests.

User must have an input .csv file containing at least three column headers representing "Golden Intent", "Partial Credit Intent", "Partial Credit Intent Score" columns.

"Golden Intent" is an intent from WA. "Partial Credit Intent" is another intent in WA that should be considered correct in place of the Golden Intent using a score of 1 for fully correct, or a score in the range 0 to 1 for considering as partially correct. The score is configured in the column "Partial Credit Intent Score".

Example:
Given a golden intent "intent1", predicted intents "Intent5" or "Intent6" are considered equally correct as "intent1" and configured with a score 1. Predicted "Intent7" is considered only 0.75 correct and configured with a score .75.

Similarly, golden intents "Intent2" and "Intent3" have other intents that are considered correct with scores 0.5 and .75 respectively.

The input file format:

```
"Golden Intent","Partial Credit Intent","Partial Credit Intent Score"
"intent1","intent5","1"
"intent1","intent6","1"
"intent1","intent7",".5"
"intent2","intent10",".5"
"intent3","intent12",".75"
"intent1_and_intent2","intent1","1.0"
"intent1_and_intent2","intent2","1.0"
```

The user must set the path to the partial credit input file in their configuration file (ie config.ini).

```
; (Optional for blind and kfold) Path to Partial Credit Table
partial_credit_table = partial-credit-table.csv
```

Sample output (ie <mode>-out.csv)
If the partial credit input file is configured the score value in range 0 to 1 is given to the utterances. If partial credit input file is not used then the values are 1 and 0s.  Note that utterances 3, 4, 7, and 9 have different scoring due to use of partial credit.

```
"utterance","golden intent","predicted intent","score","does intent match"
"utterance1","intent1","intent1","1","yes"
"utterance2","intent1","intent19","0","no"
"utterance3","intent1","intent5","1","no"
"utterance4","intent1","intent7",".5","no"
"utterance5","intent2","intent2","1","yes"
"utterance6","intent2","intent18","0","no"
"utterance7","intent2","intent10",".5","no"
"utterance8","intent3","intent14","0","no"
"utterance9","intent3","intent12",".75","no"
```


The calculations for accuracy metrics take into account the score, i.e., consider accuracy based on golden intents or their partial or full correct alternative intents.
