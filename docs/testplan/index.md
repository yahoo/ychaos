The test plan is a structured document in JSON/YAML format that
represents the configuration for the attack. It consists of various
properties starting from verification to the attack that is to be performed.

The test plan follows a Schema which is available [here]({{ data.git.schema_link }}).
You can also view a human readable documentation of the schema by visiting [here](schema/index.html)

## Validation

=== "Python"

    To validate a JSON/YAML test plan file, use the 
    [`TestPlanValidator.validate_file()`](../package_docs/testplan/validator.md) method. The method can
    take both JSON and YAML files as input and validate whether the file
    is a valid Test Plan or not.
    
    ```python
    from vzmi.ychaos.testplan.validator import TestPlanValidator
    TestPlanValidator.validate_file("/path/to/your/file.json")
    ```
    
    The above script on successful validation should not raise
    any exceptions. For an invalid test plan, the above code snippet
    should raise pydantic's ValidationError.
    
    To validate a dictionary, use the `TestPlanValidator.validate()`
    method.
    
    ```python
    from vzmi.ychaos.testplan.validator import TestPlanValidator
    data = dict()
    TestPlanValidator.validate(data)
    ```
    

=== "YChaos CLI"

    To validate a test plan file from the YChaos CLI, use the subcommand
    `validate` under `testplan`. The usage of the subcommand is given below.
    The CLI takes a list of space separated file/directory paths. If the
    path given is a valid directory, the CLI recursively finds YAML/JSON
    files inside the directory and validates each one of them.
    
    On successful validation, the CLI exits with a `exitcode=0` otherwise,
    exits with `exitcode=1`.
    
    ```
    $ ychaos testplan validate -h
    usage: ychaos testplan validate [-h] paths [paths ...]

    positional arguments:
      paths       Space separated list of file/directory paths to validate

    optional arguments:
      -h, --help  show this help message and exit
    ```
    
    ???+ "Example Run - Valid Test Plans"
    
        ```
        $ ychaos testplan validate tests/resources/testplans/valid/
        
        ───────────────────── YChaos, The resilience testing framework ──────────────────────

                     YChaos CLI configuration
        ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Configuration ┃ Value                           ┃
        ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
        │ _command_     │ ychaos ➡ testplan ➡ validate    │
        │ config        │ prod                            │
        │ paths         │ tests/resources/testplans/valid │
        │ verbose       │ 0                               │
        └───────────────┴─────────────────────────────────┘
        
        [18:15:30] Starting app                                                   main.py:125
                   Getting Test plans                                          validate.py:75
                   Validating Test plans                                       validate.py:86
        
        ✅ tests/resources/testplans/valid/testplan1.json
        ✅ tests/resources/testplans/valid/testplan1.yaml
        ✅ tests/resources/testplans/valid/testplan2.yaml
        
                   Exiting with exitcode=0                                        main.py:176
        ───────────────────────────────────────── ☀ ─────────────────────────────────────────
        ```
    
    ??? "Example Run - Invalid Test Plans"
    
        ```
        $ ychaos testplan validate \
            tests/resources/testplans/valid/ \
            tests/resources/testplans/valid/testplan4.json \
            tests/resources/testplans/invalid/
        
        ───────────────────── YChaos, The resilience testing framework ──────────────────────

                             YChaos CLI configuration
        ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Configuration ┃ Value                                          ┃
        ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
        │ _command_     │ ychaos ➡ testplan ➡ validate                   │
        │ config        │ prod                                           │
        │ paths         │ tests/resources/testplans/valid                │
        │               │ tests/resources/testplans/valid/testplan4.json │
        │               │ tests/resources/testplans/invalid              │
        │ verbose       │ 0                                              │
        └───────────────┴────────────────────────────────────────────────┘
        
        [18:16:08] Starting app                                                   main.py:125
                   Getting Test plans                                          validate.py:75
                   Validating Test plans                                       validate.py:86
        
        
        ❗ tests/resources/testplans/invalid/testplan1.yaml
        ╭───────────── Validation Error ──────────────╮
        │ 1 validation error for TestPlan             │
        │ verification -> 0 -> type                   │
        │   field required (type=value_error.missing) │
        ╰─────────────────────────────────────────────╯
        
        ✅ tests/resources/testplans/valid/testplan1.json
        ✅ tests/resources/testplans/valid/testplan1.yaml
        ✅ tests/resources/testplans/valid/testplan2.yaml
        🔍 tests/resources/testplans/valid/testplan4.json not found
        
                   Exiting with exitcode=1                                        main.py:176
        ───────────────────────────────────────── ☀ ─────────────────────────────────────────
        ```