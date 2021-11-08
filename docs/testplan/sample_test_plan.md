This section of the document contains some example testplans for you to get started quickly on the project
#### CPU Burn
```yaml
description: Increase CPU utilisation on all the cores for 60 seconds for a target host
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
        start_delay: 10 # Start Burn CPU with 10s delay
        duration: 60 # Burn CPU for 60s
```

```yaml
description: Increase CPU utilisation on all the cores for 60 seconds on local machine
attack:
  target_type: self
  agents:
    - type: cpu_burn
      config:
        duration: 60 # Burn CPU for 60s
```

#### Disable Ping
```yaml
description: Disable ping response for 60 seconds
attack:
  target_type: machine
  agents:
    - type: disable_ping
      config:
        duration: 60
        start_delay: 0
```

#### Block Ports 
```yaml
description: Block inbound and outbound connections on port 80 and 8080 for 60 seconds
attack:
  target_type: machine
  agents:
    - type: iptables_block
      config:
        start_delay: 0
        duration: 60
        incoming_ports:
          - 80
          - 8080
        destination_ports:
          - 80
          - 8080
```

#### Block Endpoints 
```yaml
description: Block incoming and outgoing connections for the hostnames for 60 seconds
attack:
  target_type: machine
  agents:
    - type: iptables_block
      config:
        start_delay: 0
        duration: 60
        incoming_endpoints:
          - "203.0.113.0"
          - "https://yahoo.com:443"
        outgoing_endpoints:
          - "203.0.113.0"
          - "https://yahoo.com:443"
```

#### Block DNS Requests
```yaml
description: Block DNS requests for 60 seconds
attack:
  target_type: machine
  agents:
    - type: dns_block
      config:
        start_delay: 0
        duration: 60
```

#### Block Traffic
```yaml
description: Block Requests to hostnames for 60 seconds
attack:
  target_type: machine
  agents:
    - type: traffic_block
      config:
        start_delay: 0
        duration: 60
        hosts:
          - "https://api.screwdriver.cd"
          - "https://api.nationalize.io"
```

#### Endpoint Certificate Validation
```yaml
description: Verify endpoint cert expire date
attack:
  target_type: machine
  agents:
    - type: server_cert_validation
      config:
        expiry_threshold: 7 # check if cert expire date is more that 7days
        urls:
          - "https://www.techcrunch.com"
          - "https://www.aol.com"
```
!!! note ""
    For more information on attack agents [refer](/ychaos/agents/)

#### HTTP Request Verification Plugin
```yaml
description: Verify Steady state by checking Request latency is below 100ms
verification:
  - delay_before: 10000
    states:
      - 'STEADY'
    type: 'http_request'
    config:
      latency: 100
      urls:
        - 'https://api.nationalize.io'
      method: 'GET'
      params:
        name: 'india'
      status_codes:
        - 200
      count: 10
attack:
    target_type: machine
    agents:
        - type: no_op
```

#### Screwdriver V4 Verification Plugin
```yaml
description: Use Screwdriver job to verify Steady state   
verification:
  - delay_before: 10000
    states:
      - 'STEADY'
    type: 'sdv4'
    config:
      sd_api_url: 'https://api.screwdriver.cd'
      pipeline_id: 123123 # SD pipeline id
      job_name: 'Run_FT' # SD job name
      sd_api_token: # Refer Screwdriver Docs
        type : env
        id: SD_API_TOKEN
attack:
    target_type: machine
    agents:
        - type: no_op
```
!!! note ""
    For more information on verification plugins [refer](/ychaos/verification/)
