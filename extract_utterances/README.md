## getUtteranceBeforeNode.py
This tool extracts user utterances from Watson Assistant logs.
The purpose of this tool is to find user utterances containing intents that can be analyzed further.

Given a list of intent-based utterances it is possible to
Test accuracy: Create a "blind" test file by adding a column with a "golden intent" for each utterance, then running WA-Testing-Tool in blind mode.
Improve training: Inspect utterances for new intents/entities that may need to be added.

*Prerequisite steps*

Gather the information needed to connect to your workspace (apikey, URL, and workspace ID)

Gather the node ID to analyze.  For each conversation that hits this node you will get the user utterance directly before this node fired.

*Execution steps*

You are required to provide:
* Arguments to connect to your workspace (apikey `-a`, workspace_id `-w`, and optionally url `-l`)

You may optionally provide
* A node ID to analyze (node_ID `-n`, default is `anything_else`)
* Output type (columns `-c`, `all` or `utterance`, default is `utterance`)
* Output filename (file `-o`, default is to print to screen)
* Maximum results (page limit `-p`, default is 100)

Example execution:

```
python getUtteranceBeforeNode.py -n node_1_1234567890123 -a 1111222233334444555566667777888899990000 -w 11111111-2222-3333-4444-555566667777 -l https://gateway-wdc.watsonplatform.net/assistant/api -c all -o output.tsv
```

You can print the help using the following command:

```
python getUtteranceBeforeNode.py -h
```
