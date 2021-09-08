# Python Module Verification Plugin

YChaos allows users to write their own plugins for verification and
use it with YChaos infrastructure. You can use the `python_module` verification
plugin for this purpose.

You can write your own python file with the program logic of what you want
to be verified and configure the testplans in the below fashion.

To view the schema of the configurations available for the plugin, 
visit [Verification Plugin][ychaos.testplan.verification.PythonModuleVerification] in
package documentation.

```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
      - CHAOS
    type: python_module
    config:
        path: /path/to/your/python/file.py
        executable: /usr/bin/python
        # You can ignore this to use `sys.executable`
        arguments: 
            - "--argument1 value1"
            - "--argument2 value2"
attack:
    target_type: machine
    agents:
        - type: no_op
```

With the above testplan, you can run the [`verify`](../../cli/manual.md#ychaos-verify) subcommand of YChaos
to run your custom python script with some arguments and YChaos
will check for the return value of the script to assert that the system
state is as expected.

!!! note
    Here is a sample YChaos CLI command that can be used
    with the above testplan
    ```bash
    ychaos verify -t testplan.yaml --state STEADY
    ```

