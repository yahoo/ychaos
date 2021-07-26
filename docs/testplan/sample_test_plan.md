#### CPU Burn
```yaml
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

#### Disable Ping
```yaml
...
agents:
  - type: ping_disable
    config:
      duration: 60
      start_delay: 0
```

#### Traffic Block
```yaml
...
agents:
  - type: traffic_block
    config:
      duration: 60
      start_delay: 0
      hosts:
        - 'www.yahoo.com'
        - 'www.google.com'
```

#### Block Ports 
```yaml
...
agents:
  - type: block_ports
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
...
agents:
  - type: block_ports
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
...
agents:
  - type: block_dns
    config:
      start_delay: 0
      duration: 60
```

#### Block Traffic
```yaml
...
agents:
  - type: traffic_block
    config:
      start_delay: 0
      duration: 60
      hosts:
        - "yahoo.com"
        - "google.com"
```

#### Endpoint Certificate Validation
```yaml
...
agents:
  - type: urls
    config:
      expiry_threshold: 7 # check if cert expire date is more that 7days
      urls:
        - "www.yahoo.com"
        - "www.google.com"
```
!!! note ""
    For more information on attack agents [refer](/ychaos/agents/)

#### HTTP Request Verification Plugin
```yaml
...
verification:
  - delay_before: 10
  - state: 'STEADY'
  - type: 'http_request'
  - config:
      latency: 100
      urls:
        - 'api.nationalize.io'
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
...
verification:
  - delay_before: 10
  - state: 'STEADY'
  - type: 'sdv4'
  - config:
      sd_api_url: 'api.screwdriver.cd'
      pipeline_id: 123123 # SD pipeline id
      job_name: 'Run_FT' # SD job name
      sd_api_token: 'API token' # Refer Screwdriver Docs
attack:
    target_type: machine
    agents:
        - type: no_op
```
!!! note ""
    For more information on verification plugins [refer](/ychaos/verification/)


