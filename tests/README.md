# WA-Testing-Tool - Integration Test
Script that executes a consolidated run against the following tests on run.py:
  - test_kfold - `KFOLD` K fold cross validation on training set,
  - test_blind - `BLIND` Evaluating a blind test, and
  - test_std - `TEST` Testing the WA against a list of utterances.
  - test_with_empty_args - Negative test with no arguments - Purposeful fail

## Features
- Relies on the run.py configuration file (config.ini).
- Single execution - test_run.py.
- Saves results of each run into a timedate stamped folder.

## Prerequisite
- Same as run.py - See it's README.md for specifics
- Watson Assistant service with at least 5 skills/workspaces

## Quick Start
1. Follow setup in run.py's README.md for required libraries, config, etc.
2. Run the process. `python3 test_run.py`
3. Review results in tests/test_<YYYYMMDD-HHMMSS>

## Caveats and Troubleshooting
1. Due to the complete execution of all available tests (KFOLD, BLIND, TEST), this script will be highly resource intensive.  It will consume a large amount of WA API calls.  A 'lite' service will suffice but will quickly consume monthly API allocation if executed multiple times.  If multiple runs are necessary, it is recommended to execute this script against the WA Standard level

2. Users on Lite plans are only able to create 5 workspaces.  They should set `FOLD_NUM_DEFAULT = 3` on their utils/__init__.py configuration file.

3. In case of interrupted execution, the tool may not be able to clean up the workspaces it creates.  In this case you will need to manually delete the extra workspaces.

4. Workspace ID is *not* the Skill ID.  In the Watson Assistant user interface, the Workspace ID can be found on the Skills tab, clicking the three dots (top-right of skill), and choosing View API Details.

5. SSL: [CERTIFICATE_VERIFY_FAILED] on Mac means you may need to initialize Python's SSL certificate store by running `Install Certificates.command` found in `/Applications/Python`.  See more [here](https://github.com/cognitive-catalyst/WA-Testing-Tool/issues/38)

# WA-Testing-Tool - Unit Test
The remaining tests in this folder are unit tests.  They need to be executed relative to the project root.

For example,

`python3 tests/test_workspaceParser.py`
