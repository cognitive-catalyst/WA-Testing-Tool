# WxA Skill Analysis

A repository to analyze and search various aspects of a watsonx Assistant instance.

This becomes very useful in the final stages of a project. For example, you want to find the exact location (action + step) of all instances of particular variable when it's used in a condition. Or you want to find all places where a variable value is being assigned. This repository allows tasks to be complete in less than 10 minutes which otherwise could have taken hours.

## Table of Contents

- [Set Up](#set-up)
   * [Configuration](#configuration)
- [How to Use This Repository](#how-to-use-this-repository)
- [Command-Line Interface](#command-line-interface)
   * [Action Contents](#action-contents)
   * [Variable Usage](#variable-usage)
   * [Subaction Usage](#subaction-usage)
   * [Extension Usage](#extension-usage)
- [Software Development Kit](#software-development-kit)
   * [Class Methods of AssistantStaticAnalyzer](#class-methods-of-assistantstaticanalyzer)
   * [Looping Over Actions and Steps](#looping-over-actions-and-steps)
- [FAQ](#faq)
   * [My Assistant JSON Failed to Parse](#my-assistant-json-failed-to-parse)
   * [How Do I Report an Issue/Bug](#how-do-i-report-an-issuebug)
   * [I Have a Feature Request](#i-have-a-feature-request)

---

## Set Up

Optional but highly recommended to create a virtual environment.

```
conda create -n wxa-skill-analysis python=3.11 -c conda-forge
conda activate wxa-skill-analysis
```

Pip install the requirements
```
pip install -r requirements.txt
```

### Configuration

For the assistant that you wish to analyze, locate the assistant json file. This can be found in the `Actions` tab, `Global Settings` which is the gear icon in the top right, `Upload/Download` tab on the far right. Click `Download` and place the file in the folder `jsons`.

You may also review the file `config/config.py` with contais some default paths used by the CLI.

## How to Use This Repository

There are two ways to use this repository. The first is through the [Command-Line Interface](#command-line-interface) (CLI), which gives pre-defined functionality such as searching over actions, subactions, variables, extensions, and entities. The CLI returns all results as a simple CSV file, which can be further filtered and refined in Excel. I recommend first playing around with the CLI and its results to gain an understanding of the capabilities of this repository.

The second way to use this repository is as a [Software Development Kit](#software-development-kit) (SDK) if you want to integrate this code-base into your own custom scripts.

---

## Command-Line Interface

The Command-Line Interface (CLI) provides gives pre-defined functionality such as searching over actions, subactions, variables, extensions, and entities. All results are returned as a CSV file.

### Action Contents

Returns a CSV reporting the "contents" of the provided action(s), e.g. conditions, variables assignments, subactions, extensions, assistant responses, etc.

```
usage: action_contents.py [-h] [-v] [-s] [-e] [-r] [-i ASSISTANT_JSON_PATH] [-o OUTPUT_PATH] [actions ...]

Search for action contents inside an assistant

positional arguments:
  actions               List of actions names to search contents of.

options:
  -h, --help            show this help message and exit
  -v, --variables       If included, the output will include all variable usage inside the listed actions.
  -s, --subactions      If included, the output will include all subaction usage inside the listed actions.
  -e, --extensions      If included, the output will include all extension usage inside the listed actions.
  -r, --responses       If included, the output will include all text response inside the listed actions.
  -i ASSISTANT_JSON_PATH, --assistant_json_path ASSISTANT_JSON_PATH
                        Path to assistant json. If not included, the code will search for one in `jsons/`.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output directory where the results will be saved. If not included, the code default to `reports/`.
```

The columns of the CSV depend on what "contents" are included in the results (i.e. which flags you choose to include).
- Columns `action_id`, `action_title`, `step_id`, `step_title`, and `step_number` will always be present in the CSV.
- If `--variables` is included in the CLI, columns `source`, `variable`, `LHS`, `RHS`, `operation`, `SpEL expression`, `text`, `is_protected` will be present. `entity_id`, `subaction_id`, `response_type` will be included in the CSV
- If `--subactions` is included in the CLI, columns `subaction_id` and `subaction_title` will be included in the CSV
- If `--extensions` is included in the CLI, columns `extension_method` and `extension_path` will be included in the CSV
- If `--responses` is included in the CLI, columns `response_type`, `response_text`, `handler_type`, and `resolver_type` will be included in the CSV

#### Example 1
```
python -m cli.action_contents "Example Action"
```

This will give all contents of the provided action.

#### Example 2
```
python -m cli.action_contents "Example Action" --variables --responses
```

By adding the content flags, the output will only contain content of those types.

#### Example 3
```
python -m cli.action_contents "Example Action 1" "Example Action 2" --variables
```

We can also include a list of actions that we want to search on.

#### Example 4

```
python -m cli.action_contents --variables
```

If we include no actions, then it will search over all actions.

#### Example 5

```
python -m cli.action_contents
```

This gives the mega spreadsheet of all content in all actions.

### Variable Usage

Returns a CSV reporting the usage of the provided variable(s), e.g. conditions, context, extensions, etc.

```
usage: variable_usage.py [-h] [-i ASSISTANT_JSON_PATH] [-o OUTPUT_PATH] [variables ...]

Search for variable usage inside an assistant

positional arguments:
  variables             List of variable names to search for.

options:
  -h, --help            show this help message and exit
  -i ASSISTANT_JSON_PATH, --assistant_json_path ASSISTANT_JSON_PATH
                        Path to assistant json. If not included, the code will search for one in `jsons/`.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output directory where the results will be saved. If not included, the code default to `reports/`.
```

The CSV will contain the following columns: `variable`, `action_id`, `action_title`, `step_id`, `step_title`, `step_number`, `source`, `LHS`, `RHS`, `operation`, `SpEL expression`, `entity_id`, `is_protected`.

#### Example 1
```
python -m cli.variable_usage variable1 variable2
```

`variable1` and `variable2` are names of variables in the assistant.

#### Example 2
```
python -m cli.variable_usage
```

If no variable names are provided, then it will return the usage of all variables in the assistant (this could be a lot).

### Entity Usage

Returns a CSV reporting the usage of the provided entity(s).

```
usage: entity_usage.py [-h] [-d] [-i ASSISTANT_JSON_PATH] [-o OUTPUT_PATH] [entities ...]

Search for entity usage inside an assistant

positional arguments:
  entities              List of entity names to search for.

options:
  -h, --help            show this help message and exit
  -d, --definition_only
                        If included, the output will include the places where the entity was defined, not where it was used.
  -i ASSISTANT_JSON_PATH, --assistant_json_path ASSISTANT_JSON_PATH
                        Path to assistant json. If not included, the code will search for one in `jsons/`.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output directory where the results will be saved. If not included, the code default to `reports/`.
```

The CSV will contain the following columns: `entity`, `action_id`, `action_title`, `step_id`, `step_title`, `step_number`, `source`, `LHS`, `RHS`, `operation`, `SpEL expression`.

#### Example 1
```
python -m cli.entity_usage entity_id_1 entity_id_2
```

`entity_id_1` and `entity_id_2` are IDs of entities in the assistant.

#### Example 2
```
python -m cli.entity_usage
```

If no entities are provided, then it will return the usage of all entities in the assistant.


### Subaction Usage

Returns a CSV reporting the usage of the provided subaction(s).

```
usage: subaction_usage.py [-h] [-i ASSISTANT_JSON_PATH] [-o OUTPUT_PATH] [subactions ...]

Search for subaction usage inside an assistant

positional arguments:
  subactions            List of subactions names to search for.

options:
  -h, --help            show this help message and exit
  -i ASSISTANT_JSON_PATH, --assistant_json_path ASSISTANT_JSON_PATH
                        Path to assistant json. If not included, the code will search for one in `jsons/`.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output directory where the results will be saved. If not included, the code default to `reports/`.
```

The CSV will contain the following columns: `action_id`, `action_title`, `step_id`, `step_title`, `step_number`, `subaction_id`, `subaction_title`.

#### Example 1
```
python -m cli.subaction_usage subaction_id_1 "Subaction 2"
```

`subaction1` and `Subaction 2` are names or IDs of actions in the assistant. Notice that if a space is required then you must put it in quotes.

#### Example 2
```
python -m cli.subaction_usage
```

If no subactions are provided, then it will return the usage of all subaction in the assistant.

### Extension Usage

Returns a CSV reporting the usage of the provided extensions(s).

```
usage: extension_usage.py [-h] [-i ASSISTANT_JSON_PATH] [-o OUTPUT_PATH] [extensions ...]

Search for subaction usage inside an assistant

positional arguments:
  extensions            List of extensions names to search for.

options:
  -h, --help            show this help message and exit
  -i ASSISTANT_JSON_PATH, --assistant_json_path ASSISTANT_JSON_PATH
                        Path to assistant json. If not included, the code will search for one in `jsons/`.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output directory where the results will be saved. If not included, the code default to `reports/`.
```

The CSV will contain the following columns: `action_id`, `action_title`, `step_id`, `step_title`, `step_number`, `extension_method`, `extension_path`.

#### Example

```
python -m cli.extension_usage
```

This will return the usage of all extensions in the assistant.

Currently there is no good way to uniquely identify extensions in the assistant json becuase they don't provide the extension name. Thus, for now we can only query for all extension use. Typically this should not be an overwhelming amount. If you have any ideas, please open a GitHub issue.

---

## Software Development Kit

This repository can be used as a software development kit (SDK), where the main class is imported and integrated into your own custom scripts. An example of this can be found in the file [`main.py`](/main.py). This gives an example of how to correctly import and instantiate the called `AssistantStaticAnalyzer`. After making the appropriate updates to the file, you can run it with the following command.

```
python -m main
```

### Class Methods of `AssistantStaticAnalyzer`

All class methods have an optional parameter `return_as` which defaults to returning the results as a python list of dictionaries. If `return_as="csv"`, then the class method will return the results as a `pandas` DataFrame. If `return_as="json"`, then the class method will return the results as a JSON serialized string. [`main.py`](/main.py) shows an example of this usage.

#### Variables
- `get_all_variable_usage()`
- `search_for_variables(*list_of_variable_ids)`
- `get_all_variables_used_in_action(*list_of_action_titles_or_ids)`
- `variable_summary()`

#### Entities
- `get_all_entity_usage()`
- `search_for_entities(list_of_entity_ids)`
- `get_all_entities_used_in_action(*list_of_action_titles_or_ids)`

#### Subactions
- `get_all_subaction_usage()`
- `search_for_subactions(*list_of_subaction_titles_or_ids)`
- `get_all_subactions_used_in_action(*list_of_action_titles_or_ids)`

#### Extensions
- `get_all_extension_usage()`
- `get_all_extensions_used_in_action(*list_of_action_titles_or_ids)`

#### Responses
- `get_all_responses()`
- `get_all_responses_in_action(*list_of_action_titles_or_ids)`

#### Action Settings
- `get_all_action_settings()`
- `search_for_action_settings(*list_of_action_titles_or_ids)`

### Looping Over Actions and Steps

A common activity when writing custom scripts is to loop over actions and steps. The following code snippet shows how to do this
```python
import json
from src.assistant_static_analyzer import AssistantStaticAnalyzer

path_to_assistant_json = "./jsons/<filename>.json"    # <-- TODO: Add your variable name here
assistant_obj = json.load(open(path_to_assistant_json, 'r'))
analyzer = AssistantStaticAnalyzer(assistant_obj)

for action in analyzer.actions:
    action_id = action.ID
    action_title = action.title

    for step in action.steps:
        step_id = step.ID
        step_title = step.title
        step_number = step.step_number

        print(action_title, step_number, step_title)
```

If you find this SDK useful and would like to see more documentation, please open a GitHub issue.

---

## FAQ

### My Assistant JSON Failed to Parse

I have only tested this codebase on the select projects that I have been a part of. Watsonx Assistant is a complex tool and as such I have not found an exhaustive list of all possible things that I could encounter in the JSON. Please open a GitHub issue.

### How Do I Report an Issue/Bug

Please open a GitHub issue.

### I Have a Feature Request

Please open a GitHub issue.

### Is There More SDK Documentation?

For now you can consult the actual source code found in [`/src`](/src), which is reasonably structured. If you find the SDK useful and want more detailed documentation, please open a GitHub issue.
