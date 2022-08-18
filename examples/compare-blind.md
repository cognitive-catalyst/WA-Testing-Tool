# Compare Blind Test results

## Story
Given two different blind test results, on the same input data set, compare & contrast the two different results.  Include an overall summary, an intent-wise summary, and details for each utterance that has different answers in the different tests.

## Workflow
As starting point, we assume the user has run two different [blind](blind.md) tests (which each create a .csv file) and has stored those .csv files with different names.  Most significantly, this tool needs the utterance-level detailed results (example: `blind-out.csv`)

User executes `compare-blind.py` providing the input filename for current and previous blind test results with `-c` and `-p` respectively.  The user also provides a base output filename with `-o`.

## Prerequisite
User must have two input .csv files containing utterance-level results from blind tests.

## Invocation
Assuming "current" input file at `data/blind-current-out.csv` and "previous" input file at `data/blind-previous-out.csv` created by WA-Testing-Tool blind tests and writing to `data/comparison.csv'.

```
python3 utils/compare-blind.py -c data/blind-current-out.csv -p data/blind-previous-out.csv -o data/comparison.csv
```

## Sample output
```
** Summarized results **
Current  : 481 of 637 correct
Previous : 478 of 637 correct
IMPROVED : 3 of 637

** Intent-specific results **
Computing intent summary comparison, saving to compare_intent_comparison.csv
IMPROVED  accuracy on 2 intents
REGRESSED accuracy on 0 intents
UNCHANGED accuracy on 1 intents

** Utterance-specific results **
IMPROVED  utterances: 37 total, saving to compare_improved_utterances.csv
REGRESSED utterances: 29 total, saving to compare_regressed_utterances.csv
Average confidence in correct   answer (current ): 0.871
Average confidence in correct   answer (previous): 0.860
Average confidence in incorrect answer (current ): 0.663
Average confidence in incorrect answer (previous): 0.635
```

`compare_intent_comparison.csv` example contents:

```
"intent","total","curr_correct","prev_correct","diff_correct","curr_correct_confidence","prev_correct_confidence","diff_correct_confidence","curr_incorrect_confidence","prev_incorrect_confidence","diff_incorrect_confidence"
"reset_password","238","196","203","-7","0.872","0.860","0.012","0.440","0.374","0.067"
"store_location","314","263","227","36","0.912","0.892","0.020","0.796","0.703","0.093"
```

`compare_improved_utterances.csv` example contents (`compare_regressed_utterances.csv` has similar format):
```
"utterance","golden intent","current_prediction","current_confidence","current_score","previous_prediction","previous_confidence","previous_score"
"where do i go to reset my password","reset_password","store_location","0.4428514242172241","0","reset_password","0.4460688531398773","1"
"what's the location of the password reset function","reset_password","store_location","0.4428514242172241","0","reset_password","0.4460688531398773","1"
```