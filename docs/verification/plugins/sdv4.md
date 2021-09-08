# Screwdriver Build Verification Plugin

Screwdriver is an open source build platform designed for Continuous Delivery by Yahoo. A CI/CD pipeline
can be configured with a particular job that will be triggered remotely from YChaos and the status of the
build is verified to ensure the system is in expected state. As a user of YChaos, you can configure
your own scripts to run inside the Screwdriver build.

To view the schema of the configurations available for the plugin, visit [Verification Plugin][ychaos.testplan.verification.SDv4Verification]
in package documentation.

!!! Note
    To know more about Screwdriver CI/CD visit the official site of [Screwdriver](https://screwdriver.cd/)

## Example Testplan

This section provides some example testplans with Screwdriver Build configured.

```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
      - CHAOS
    type: sdv4
    config:
        pipeline_id: 7419
        # Configure a Job `verify_ychaos_state` in Pipeline 1032344
        job_name: verify_ychaos_state
        # For self hosted build cluster, provide your API URL
        # Eg: https://api.screwdriver.mycompany.com
        sd_api_url: https://api.cd.screwdriver.cd
        sd_api_token:
          type: env
          id: SD_API_TOKEN
attack:
    target_type: machine
    agents:
        - type: no_op
```
