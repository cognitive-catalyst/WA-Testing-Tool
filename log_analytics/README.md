## Scripts to extract and analyze Watson Assistant logs
These scripts are intended to form a data pipeline for Watson Assistant log analysis.

For more information on Watson Assistant log analysis, check out the blog series "Analyzing and Improving a Watson Assistant Solution":
* [Part 1: Analytics Personas and Existing Solutions](https://medium.com/ibm-watson/analyzing-and-improving-a-watson-assistant-solution-part-1-analytics-personas-and-existing-9fbd2f0b7478)
* [Part 2: Foundational Components of Watson Assistant analysis](https://medium.com/ibm-watson/analyzing-and-improving-a-watson-assistant-solution-part-2-foundational-components-of-watson-6596518e7a28)
* [Part 3: Recipes for common analytic patterns](https://medium.com/ibm-watson/analyzing-and-improving-a-watson-assistant-solution-part-3-recipes-for-common-analytic-patterns-1edb4b1f2ef2)

# getAllLogs.py
Using a filter argument grabs a set of logs from Watson Assistant.  Specify the maximum number of log pages (`-n`) to retrieve and the maximum number of log entries per page (`-p`).

This utility uses the `list_logs` API when a workspace_id is passed, otherwise uses `list_all_logs` API which requires a language and one of `request.context.system.assistant_id`, `workspace_id`, or `request.context.metadata.deployment` in the filter (see https://cloud.ibm.com/apidocs/assistant/assistant-v1?code=python#list-log-events-in-all-workspaces)

The `filter` syntax is documented here: https://cloud.ibm.com/docs/services/assistant?topic=assistant-filter-reference#filter-reference

Example for one workspace:
```
python3 getAllLogs.py -a your_api_key -w your_workspace_id -l https://gateway.watsonplatform.net/assistant/api -c raw -n 20 -p 500 -o 10000_logs.json -f "response_timestamp>=2019-11-01,response_timestamp<2019-11-21"
```

Example for one assistant:
```
python3 getAllLogs.py -a your_api_key -l https://gateway.watsonplatform.net/assistant/api -c raw -n 20 -p 500 -o 10000_logs.json -f "language::en,response_timestamp>=2019-11-01,response_timestamp<2019-11-21,request.context.system.assistant_id::your_assistant_id"
```

The Watson Assistant team has put out a similar script at https://github.com/watson-developer-cloud/community/blob/master/watson-assistant/export_logs.py

# extractConversations.py
Takes a series of logs, extracts fields for analysis, builds a Pandas dataframe, and outputs it to a CSV file.  (The `extractConversationData` method can be called directly to build a DataFrame in memory.) The output contains the most frequently analyzed Watson Assistant log fields, some new fields to augment analysis, and custom fields that you specify.

The unique conversation identifier is provided with `-c`.  Note that if a single conversation spans multiple workspaces (skills), you cannot use `conversation_id` as the unique identifier.

Custom fields are specified with `-f`.  You can specifiy multiple custom fields as a comma-separated list, for example `-f response.context.STT_CONFIDENCE,response.context.action`.

Example for text-based assistants:
```
python3 extractConversations.py -i 10000_logs.json -o 10000_logs.csv -c "response.context.conversation_id"
```

Example for voice-based assistants using IBM Voice Gateway:
```
python3 extractConversations.py -i 10000_logs.json -o 10000_logs.csv -c "request.context.vgwSessionID"
```

# ConversationAnalysisRecipes.ipynb
This notebook demonstrates several log analytic functions, starting with downloading logs (via `getAllLogs.py`) and extracting fields of interest (via `extractConversations.py`), then demonstrating basic and intermediate analytic capabilities.

# intent_heatmap.py
Takes a tab-separated file (ie exported data frame from `ConversationAnalysisRecipes.ipynb`) and builds heat maps to help visualize the intent metrics.

```
python3 intent_heatmap.py -i first-turn-stats.tsv -o intent_conf.png -s "Total" -r "Intent Confidence" -l "Intent" -t "Classifier confidence by intent"
python3 intent_heatmap.py -i first-turn-stats.tsv -o stt_conf.png -s "Total" -r "STT Confidence" -l "Intent" -t "Speech confidence by intent"
```

# Other analyses
Several other types of analysis are possible with Watson Assistant log data.  The Watson Assistant development team has released [two notebooks](https://github.com/watson-developer-cloud/assistant-improve-recommendations-notebook) which help further analyze log data:
* Measure Notebook - The Measure notebook contains a set of automated metrics that help you monitor and understand the behavior of your system. The goal is to understand where your assistant is doing well vs where it isn’t, and to focus your improvement effort to one of the problem areas identified.
* Effectiveness Notebook - The Effectiveness notebook helps you understand relative performance of each intent and entity as well as the confusion between your intents. This information helps you prioritize your improvement effort.
* The [Dialog Skill Analysis](https://medium.com/ibm-watson/announcing-dialog-skill-analysis-for-watson-assistant-83cdfb968178) helps assess your Watson Assistant intent training data for patterns before you deploy.
* [Analyze chatbot classifier performance from logs](https://medium.com/ibm-watson/analyze-chatbot-classifier-performance-from-logs-e9cf2c7ca8fd) is a blog and video demonstrating how you can take utterances from logs and convert them into training and/or testing data.
* Beware of focusing too much on training accuracy - you should measure and be concerned about blind test accuracy.  See this two-part blog series on "Why Overfitting is a Bad Idea and How to Avoid It" with [Part 1: Overfitting in General](https://medium.com/ibm-watson/why-overfitting-is-a-bad-idea-and-how-to-avoid-it-part-1-overfitting-in-general-b8a3f9ffcf66) and [Part 2: Overfitting in Virtual Assistants](https://medium.com/ibm-watson/why-overfitting-is-a-bad-idea-and-how-to-avoid-it-part-2-overfitting-in-virtual-assistants-a30f4d999adc).

