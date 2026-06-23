# WxA Skill Analysis

A repository to analyze and search various aspects of a watsonx Assistant instance.

This becomes very useful in the final stages of a project. For example, you want to find the exact location (action + step) of all instances of particular variable when it's used in a condition. Or you want to find all places where a variable value is being assigned. This repository allows tasks to be complete in less than 10 minutes which otherwise could have taken hours.

## Table of Contents

- [Installation](#installation)
   * [Set Up a Development Environment](#set-up-a-development-environment)
   * [Configuration](#configuration)
- [How to Use This Repository](#how-to-use-this-repository)
- [Command-Line Interface](#command-line-interface)
   * [Quick Start](#quick-start)
   * [Alternative CLI Usage](#alternative-cli-usage)
   * [Common Options](#common-options)
   * [Available Commands](#available-commands)
      - [Assistant Metadata](#assistant-metadata)
      - [Action Analysis](#action-analysis)
      - [Variable Analysis](#variable-analysis)
      - [Entity Analysis](#entity-analysis)
      - [Intent Analysis](#intent-analysis)
      - [Extension & Subaction Analysis](#extension--subaction-analysis)
- [Software Development Kit](#software-development-kit)
   * [Basic Usage](#basic-usage)
   * [Output Formats](#output-formats)
   * [Available Analyzers and Methods](#available-analyzers-and-methods)
   * [Working with the Assistant Object](#working-with-the-assistant-object)
   * [Example: Custom Analysis Script](#example-custom-analysis-script)
   * [Advanced: Looping Over Actions and Steps](#advanced-looping-over-actions-and-steps)
- [FAQ](#faq)
   * [My Assistant JSON Failed to Parse](#my-assistant-json-failed-to-parse)
   * [How Do I Report an Issue/Bug](#how-do-i-report-an-issuebug)
   * [I Have a Feature Request](#i-have-a-feature-request)
   * [Is There More SDK Documentation?](#is-there-more-sdk-documentation)

---

## Installation

### Set Up a Development Environment

```bash
# Optional but highly recommended: create a virtual environment
conda create -n wxa-skill-analysis python=3.11 -c conda-forge
conda activate wxa-skill-analysis

# Clone the repository
git clone https://github.com/cognitive-catalyst/WA-Testing-Tool.git
cd WA-Testing-Tool/skill_analytics

# Install in editable mode with dependencies
pip install -e .
```

### Configuration

For the assistant that you wish to analyze, locate the assistant json file. This can be found in the `Actions` tab, `Global Settings` which is the gear icon in the top right, `Upload/Download` tab on the far right. Click `Download` and place the file in the folder `jsons`.

You may also review the file `config/config.py` with contais some default paths used by the CLI.

## How to Use This Repository

There are two ways to use this repository. The first is through the [Command-Line Interface](#command-line-interface) (CLI), which gives pre-defined functionality such as searching over actions, subactions, variables, extensions, and entities. The CLI returns all results as a simple CSV file, which can be further filtered and refined in Excel. I recommend first playing around with the CLI and its results to gain an understanding of the capabilities of this repository.

The second way to use this repository is as a [Software Development Kit](#software-development-kit) (SDK) if you want to integrate this code-base into your own custom scripts.

---

## Command-Line Interface

After installation, you can use the `wxa-analyze` command followed by a subcommand. The CLI provides pre-defined functionality for analyzing actions, variables, entities, extensions, and more. All results are returned as CSV or JSON files.

### Quick Start

View all available commands:
```bash
wxa-analyze --help
```

Get help for a specific command:
```bash
wxa-analyze action-metadata --help
```

### Alternative CLI Usage

You can also run commands directly using Python modules:
```bash
python -m cli --help
python -m cli.action_metadata --help
```

This approach provides the same functionality as the `wxa-analyze` command. Note that the  `-` will be replaced with `_`. However, the documentation will assume the usage of `wxa-analyze`.

### Common Options

All commands support these options:
- `-i, --assistant_json_path PATH` - Path to the watsonx Assistant JSON file (default: configured in `config/config.py`)
- `-o, --output_path PATH` - Directory where output files will be saved (default: configured in `config/config.py`)

### Available Commands

#### Assistant Metadata

**assistant-metadata** - Extract comprehensive metadata about the assistant including IDs, settings, and aggregated statistics:
```bash
wxa-analyze assistant-metadata
wxa-analyze assistant-metadata -i assistant.json -o ./reports
```
Output: JSON file with assistant-level information

#### Action Analysis

**action-metadata** - Extract metadata for all actions in the assistant:
```bash
wxa-analyze action-metadata
wxa-analyze action-metadata -i assistant.json -o ./reports
```
Output: CSV with action IDs, titles, and configuration details

**condition-usage** - Report all conditions used in action steps:
```bash
wxa-analyze condition-usage                    # All actions
wxa-analyze condition-usage action_1           # Single action
wxa-analyze condition-usage action_1 action_2  # Multiple actions
```
Output: CSV with condition expressions and their locations

**context-usage** - Report all context statements used in action steps:
```bash
wxa-analyze context-usage                    # All actions
wxa-analyze context-usage action_1           # Single action
wxa-analyze context-usage action_1 action_2  # Multiple actions
```
Output: CSV with context variable assignments

**customer-response-settings** - Extract customer response settings (prompts, retries, disambiguation) for action steps:
```bash
wxa-analyze customer-response-settings                    # All actions
wxa-analyze customer-response-settings action_1           # Single action
wxa-analyze customer-response-settings action_1 action_2  # Multiple actions
```
Output: CSV with response configuration details

**response-usage** - Report all customer response types used in action steps (text, options, dates, etc.):
```bash
wxa-analyze response-usage                    # All actions
wxa-analyze response-usage action_1           # Single action
wxa-analyze response-usage action_1 action_2  # Multiple actions
```
Output: CSV with response types and content

**validation-settings** - Extract validation settings (input validation rules) for action steps:
```bash
wxa-analyze validation-settings                    # All actions
wxa-analyze validation-settings action_1           # Single action
wxa-analyze validation-settings action_1 action_2  # Multiple actions
```
Output: CSV with validation rules and error messages

**step-summary** - Get a comprehensive summary of each step for specified actions:
```bash
wxa-analyze step-summary                    # All actions
wxa-analyze step-summary action_1           # Single action
wxa-analyze step-summary action_1 action_2  # Multiple actions
```
Output: CSV with detailed step information including conditions, context, responses, extensions, and resolvers

#### Variable Analysis

**variable-metadata** - Extract metadata for all variables defined in the assistant:
```bash
wxa-analyze variable-metadata                                    # All variable types
wxa-analyze variable-metadata --skill_variables                  # Only skill variables
wxa-analyze variable-metadata --step_variables                   # Only step variables
wxa-analyze variable-metadata --result_variables                 # Only result variables
wxa-analyze variable-metadata --system_variables                 # Only system variables
wxa-analyze variable-metadata --skill_variables --step_variables # Multiple types
```
Output: CSV with variable definitions, types, and scopes

**variable-usage** - Find where variables are used throughout the assistant:
```bash
wxa-analyze variable-usage                  # All variables
wxa-analyze variable-usage var1             # Single variable
wxa-analyze variable-usage var1 var2        # Multiple variables
wxa-analyze variable-usage --metadata       # Include variable metadata
```
Output: CSV with variable usage locations and context

#### Entity Analysis

**entity-metadata** - Extract metadata for all entities defined in the assistant:
```bash
wxa-analyze entity-metadata
wxa-analyze entity-metadata -i assistant.json -o ./reports
```
Output: CSV with entity IDs, types, values, and fuzzy matching settings

**entity-usage** - Find where entities are used throughout the assistant:
```bash
wxa-analyze entity-usage                    # All entities
wxa-analyze entity-usage sys-date           # Single entity
wxa-analyze entity-usage sys-date sys-time  # Multiple entities
wxa-analyze entity-usage --metadata         # Include entity metadata
```
Output: CSV with entity usage locations

#### Intent Analysis

**intent-usage** - Find where intents are used in action conditions and step handlers:
```bash
wxa-analyze intent-usage                    # All actions
wxa-analyze intent-usage action_1           # Single action
wxa-analyze intent-usage action_1 action_2  # Multiple actions
```
Output: CSV with intent references and their locations

#### Extension & Subaction Analysis

**extension-usage** - Find all custom extension calls in the assistant:
```bash
wxa-analyze extension-usage
wxa-analyze extension-usage -i assistant.json -o ./reports
```
Output: CSV with extension methods, paths, and invocation locations

**subaction-usage** - Find all subaction invocations in the assistant:
```bash
wxa-analyze subaction-usage
wxa-analyze subaction-usage -i assistant.json -o ./reports
```
Output: CSV with subaction IDs, titles, and where they are called

---

## Software Development Kit

This repository can be used as a software development kit (SDK), where you can import the models and analyzers into your own custom scripts for programmatic access to assistant analysis.

### Basic Usage

```python
import json
from src.models.assistant import Assistant
from src.analyzers import (
    ActionAnalyzer,
    AssistantAnalyzer,
    EntityAnalyzer,
    IntentAnalyzer,
    ResolverAnalyzer,
    VariableAnalyzer
)

# Load assistant JSON
with open("path/to/assistant.json", 'r') as f:
    assistant_dict = json.load(f)

# Create Assistant object
assistant = Assistant.from_dict(assistant_dict)

# Create analyzers
action_analyzer = ActionAnalyzer(assistant)
variable_analyzer = VariableAnalyzer(assistant)
entity_analyzer = EntityAnalyzer(assistant)
intent_analyzer = IntentAnalyzer(assistant)
resolver_analyzer = ResolverAnalyzer(assistant)
assistant_analyzer = AssistantAnalyzer(assistant)
```

### Output Formats

All analyzer methods support a `return_as` parameter that controls the output format:
- `return_as="python"` (default) - Returns a Python list of dictionaries
- `return_as="dataframe"` - Returns a pandas DataFrame

Example:
```python
# Get as Python list
results = variable_analyzer.get_variable_usage(return_as="python")

# Get as pandas DataFrame
df = variable_analyzer.get_variable_usage(return_as="dataframe")
```

### Available Analyzers and Methods

#### AssistantAnalyzer
- `assistant_metadata(return_as="python")` - Get comprehensive assistant metadata

#### ActionAnalyzer
- `action_metadata(return_as="python")` - Get metadata for all actions
- `condition_usage(*action_ids, return_as="python")` - Get all conditions used in steps
- `context_usage(*action_ids, return_as="python")` - Get all context statements
- `customer_response_settings(*action_ids, return_as="python")` - Get customer response settings
- `response_usage(*action_ids, return_as="python")` - Get all response types used
- `step_summary(*action_ids, return_as="python")` - Get comprehensive summary of each step
- `validation_settings(*action_ids, return_as="python")` - Get validation settings

#### VariableAnalyzer
- `get_variable_metadata(include_skill_variables=True, include_step_variables=True, include_result_variables=True, include_system_variables=True, return_as="python")` - Get metadata for all variables
- `get_variable_usage(*variable_ids, return_as="python")` - Find where variables are used
- `get_variables_by_type(variable_type, return_as="python")` - Get variables of a specific type

#### EntityAnalyzer
- `entity_metadata(return_as="python")` - Get metadata for all entities
- `entity_usage(*entity_ids, return_as="python")` - Find where entities are used

#### IntentAnalyzer
- `intent_usage(*action_ids, return_as="python")` - Find where intents are used

#### ResolverAnalyzer
- `subaction_usage(return_as="python")` - Find all subaction invocations
- `extension_usage(return_as="python")` - Find all extension calls

### Working with the Assistant Object

The `Assistant` object provides direct access to all assistant components:

```python
# Access actions
for action_id, action in assistant.actions.items():
    print(f"Action: {action.title} ({action.id})")
    
    # Access steps within an action
    for i, step in enumerate(action.steps):
        print(f"  Step {i+1}: {step.title} ({step.id})")

# Access variables
for var_id, variable in assistant.skill_variables.items():
    print(f"Skill Variable: {variable.id}")

for var_id, variable in assistant.step_variables.items():
    print(f"Step Variable: {variable.id}")

for var_id, variable in assistant.result_variables.items():
    print(f"Result Variable: {variable.id}")

  for var_id, variable in assistant.system_variables.items():
    print(f"System Variable: {variable.id}")

# Access entities
for entity_id, entity in assistant.entities.items():
    print(f"Entity: {entity.id}")

# Access intents
for intent_id, intent in assistant.intents.items():
    print(f"Intent: {intent.id}")
```

### Example: Custom Analysis Script

```python
import json
from src.models.assistant import Assistant
from src.analyzers import VariableAnalyzer

# Load assistant
with open("assistant.json", 'r') as f:
    assistant_dict = json.load(f)
assistant = Assistant.from_dict(assistant_dict)

# Analyze variable usage
variable_analyzer = VariableAnalyzer(assistant)

# Get usage of specific variables
usage_df = variable_analyzer.get_variable_usage(
    "customer_name",
    "order_id",
    return_as="dataframe"
)

# Save to CSV
usage_df.to_csv("variable_usage_report.csv", index=False)

# Get all skill variables
skill_vars = variable_analyzer.get_variable_metadata(
    include_skill_variables=True,
    include_step_variables=False,
    include_result_variables=False,
    include_system_variables=False,
    return_as="dataframe"
)

print(f"Found {len(skill_vars)} skill variables")
```

### Advanced: Looping Over Actions and Steps

```python
from src.models.assistant import Assistant

# Load and parse assistant
assistant = Assistant.from_dict(assistant_dict)

# Loop through all actions and steps
for action in assistant.actions.values():
    print(f"Action: {action.title} (ID: {action.id})")
    
    # Access action-level properties
    print(f"  Intent: {action.intent.id}")
    print(f"  Number of steps: {len(action.steps)}")
    
    # Loop through steps
    for i, step in enumerate(action.steps):
        print(f"  Step {i+1}: {step.title} (ID: {step.id})")
        
        # Access step properties
        if step.question:
            print(f"    Has question: {step.question.response_type}")
        if step.resolver:
            print(f"    Resolver: {step.resolver.__class__.__name__}")
```

If you find this SDK useful and would like to see more documentation, please open a GitHub issue.

---

## FAQ

### My Assistant JSON Failed to Parse

I have only tested this codebase on the select projects that I have been a part of. Watsonx Assistant is a complex tool and as such I have not found an exhaustive list of all possible things that I could encounter in the JSON. If you run into any errors, please open a GitHub issue.

### How Do I Report an Issue/Bug

Please open a GitHub issue.

### I Have a Feature Request

Please open a GitHub issue.

### Is There More SDK Documentation?

For now you can consult the actual source code found in [`/src`](/src), which is reasonably structured and well-typed. If you find the SDK useful and want more detailed documentation, please open a GitHub issue.
