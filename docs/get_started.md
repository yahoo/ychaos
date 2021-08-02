This section of the document contains the steps to get started with YChaos.

1. Install ychaos 
    ```bash 
    pip install ychaos[chaos]
    ``` 
1. Create a valid test plan. (Refer Ychaos test plan [schema](/ychaos/testplan/))
1. Ensure the target hosts selected for testing have python3.6+ and pip3 package pre-installed
1. Execute the test plan 
    ```bash
    ychaos execute -t ./testplan.json
    ```
 
!!! note ""
    Final report, log file will be stored in the path specified in the test plan

#### Simple test plan configured to perform CPU burn for 60 seconds
```yaml
description: A simple test plan with CPU burn configured
attack:
  target_type: machine
  target_config:
    blast_radius: 100
    ssh_config:
      user: testUser
      password: testUserPassword
    hostnames:
    - mocktargethost.namespace.cloud
    report_dir: "./"
  agents:
  - type: cpu_burn
    config:
      start_delay: 0
      duration: 60

```

!!! note ""
    Ensure ssh user specified in test plan has access to the host. Ychaos supports private key or password based authentication for sshing to target hosts.
    