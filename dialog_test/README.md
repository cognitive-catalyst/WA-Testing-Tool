# Watson Assistant Dialog Testing


Prerequisites:
* Python 3.x
* Watson Developer Cloud SDK (1.x or 2.x)

## Running the tests
You will need to set three environment variables: ASSISTANT_PASSWORD, WORKSPACE_ID and ASSISTANT_URL.  The WORKSPACE_ID should be the first workspace the test executes against.  The ASSISTANT_PASSWORD is your IAM apikey.
This is done with the `export` command on Mac/Linux shell or `SET` in Windows

Run a sample test as follows:
```
python3 flowtest.py tests/Customer_Care_Test.tsv
```

Run all tests in a directory (and it's subdirectories) as follows:
```
python3 flowtest.py tests
```

Check the `results` folder for test output.  If any MATCH column has a 'FALSE' value, the test has failed.
Additionally, each test will print a single PASS or FAIL marker to standard out upon completion.

## Building tests with configuration
Build test files in the tests subfolder.  Each test should be a tab separated file or a JSON file.

For a tab-separated file, the column headers are the following ("Turn number" is NOT specified as a column header)
(Turn number) User Input      Match Output    Match Intent    Match Entity    Alternate Intents       Intents Object  Entities Object Context Variables       System Object

For a JSON test file, the file contents are an array of JSON objects.  For example:
```
[
  {
    "Turn": "0",
    "Context Variables": {
      "user_type": "GOLD"
    }
  },
  {
    "Turn": "1",
    "User Input": "I need to reset my password",
    "Match Output": "I can help you reset your password"
  }
]
```

All fields are optional

* Match Output indicates a substring that must be present in the Watson Assistant response. It is not necessary to provide the full output string. Regular Expressions can be enclosed with forward slashes (e.g. `/The reservation is for *. PM/`). `<br>` can be used to join lines when specifyig multiline ouputs (e.g. `The reservation is for 6 guests<br>What day would you like to come in?`).

If the User Input column is exactly 'NEWCONVERSATION' (no quotes) then a new conversation is started.  This allows multiple tests in the same file.
