## validateWS.py
This is a syntax validator for Watson Assistant workspaces (skills) that integrate with a Service Orchestration Engine (SOE) or a Voice Gateway.  SOEs and Voice Gateway have syntax constructs that are not natively validated by Watson Assistant.  This tool examines a Watson Assistant workspace and prints error and warning conditions.

*Prerequisite steps*

Gather the information needed to connect to your workspace.  You can run the tool against a local copy of the workspace or can use the remote copy.

Export the Watson Assistant workspace you wish to validate: https://developer.ibm.com/tutorials/learn-how-to-export-import-a-watson-assistant-workspace/
Or gather the IAM apikey, URL, and workspace ID.

*Execution steps*
You are required to provide:
* Arguments to find your workspace (either `-f` or the `-o` set)
* At least one validation group (either `-s` or `-g`)

A local file is referenced with "`-f` your_filename_here".

An online connection to the workspace is referenced with "`-o` `--apikey` your_apikey_here `--url` your_url_here `--workspace_id` your_workspace_id_here".

To validate a workspace against an SOE contract, invoke with `-s`.  You can optionally specify the legal "route" values with `--soe_route`

```
python3 validateWS.py -f your_workspace_file.json -s --soe_route "TTS,OPT_OUT,UI,SOE,API,None"
```

To validate a workspace against IBM Voice Gateway syntax, invoke with `-g`.  You can optionally specify the expected voice gateway commands that should be present on any playback nodes with `--voice_gateway_commands`

```
python3 validateWS.py -f your_workspace_file.json -g --voice_gateway_commands "vgwActSetSTTConfig,vgwActPlayText"
```

Note that you can simultaneously validate against SOE contract and IBM Voice Gateway syntax by specifying both `-s` and `-g` options.
