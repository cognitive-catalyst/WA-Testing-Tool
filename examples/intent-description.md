# Description
Create a file of intent descriptions for your Watson Assistant workspace. The script outputs a csv file with the intent name and the description of that intent.

Example output:
```
intent, description
navigation, ask how to get somewhere
turn_on, turn something on
turn_off, turn something off
```

# Usage
Specify whether you would like to use a local workspace file or supply credentials to a live instance
```
usage: get_intent_description.py [-h] {remote,local} ...

Create Intent Descriptions file from workspace json

positional arguments:
  {remote,local}  help for subcommand
    remote        Watson Assistant Credentials
    local         Local workspace file
```


## Local Watson Assistant Workspace File
```console
$ python3 get_intent_description.py local path/to/workspace.json
```

```
usage: get_intent_description.py local [-h] [--output OUTPUT] json

positional arguments:
  json                  Path to workspace json file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file (default: intent_desc.csv)
```

## Remote Watson Assistant Workspace
```console
$ python3 get_intent_description.py remote -a <wa-iam-apikey> -w <wa-workspace-id>
```


```
usage: get_intent_description.py remote [-h] [--output OUTPUT] --iam_apikey APIKEY
                                        --workspace_id WORKSPACE_ID

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file (default: intent_desc.csv)

required arguments:
  --iam_apikey APIKEY, -a apikey  Watson Assistant IAM API key (default: None)
  --workspace_id WORKSPACE_ID, -w WORKSPACE_ID
                        Watson Assistant Workspace ID (default: None)

```
