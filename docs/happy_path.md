
1. Install ychaos 
    ```bash 
    pip install ychaos[chaos]
    ``` 
1. Create a valid test plan. (Refer ychaos test plan [schema](/ychaos/testplan/))
1. Target hosts selected for testing must have python3.6+, pip3 and virtualenv package pre-installed
1. Run 
    ```bash
    ychaos execute -t ./testplan.json
    ```
 
>Final report, log file will be stored in the path specified in the test plan

#### Simple test plan configured to perform CPU burn for 60 seconds
```json
{
    "description": "A simple test plan with CPU burn configured",
    "attack": {
        "target_type": "machine",
        "target_config": {
            "blast_radius": 100,
            "ssh_config": {
                "user": "testUser",
                "password": "testUserPassword"
            },
            "hostnames": ["target hosts"],
            "report_dir":  "./"
        },
        "agents": [
            {
                "type": "cpu_burn",
                "config": {
                    "start_delay": 0,
                    "duration": 60
                }
            }
        ]
    }
}
```

Note: ychaos supports private key or password based authentication for sshing to target hosts.