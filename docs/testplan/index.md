The test plan is a structured document in JSON/YAML format that
represents the configuration for the attack. It consists of various
properties starting from verification to the attack that is to be performed.

The test plan follows a Schema which is available [here]({{ data.git.schema_link }}).
You can also view a human readable documentation of the schema by visiting [here](schema/index.html)

## Validation

=== "Python"

    To validate a JSON/YAML test plan file, use the 
    `TestPlanValidator.validate_file()` method. The method can
    take both JSON and YAML files as input and validate whether the file
    is a valid Test Plan or not
    
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

    {{ data.general.todo }}