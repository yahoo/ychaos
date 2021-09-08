# HTTP Request Verification Plugin

The HTTP Request Verification plugin is defined to make request calls to a particular endpoint
and verify that the response from the server reaches the controller within an expected latency.
This can be used to measure the latency of the server before, during and post the attack to montior
the behaviour of your service during the phases of chaos testing.

The plugin provides a number of configurations like Auth, Certificate, Headers etc. To view the schema of the
configurations available for the plugin, visit [Verification Plugin][ychaos.testplan.verification.HTTPRequestVerification] in
package documentation.

!!! Note
    YChaos does not log any basic auth credentials/bearer tokens used during configurations.

## Example Testplans

This section provides some example testplans with HTTP request plugins configured.

1. Testplan with `http_request` plugin configured that calls `https://yourawesomeservice1.com:4443/path` and `https://yourawesomeservice2.com:4443/path`
with a set of query params 3 times and verifies if the latency is within `1000ms`
```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
    type: http_request
    config:
        urls:
            - https://yourawesomeservice1.com:4443/path
            - https://yourawesomeservice2.com:4443/path
        params:
            key1: "value1"
            key2: "value2"
        count: 3
        # Number of HTTP calls to be made to these endpoints
        latency: 1000
        # If your services return a valid response with latency>1000ms
        # the verification fails.
attack:
    target_type: machine
    agents:
        - type: no_op
```

2. Testplan with `http_request` plugin configured that calls `https://yourawesomeservice1.com:4443/path`
with a set of query params 3 times and verifies if the latency is within `1000ms` but ignores the
validity of the SSL certificate presented by the server.
```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
    type: http_request
    config:
        urls:
            - https://yourawesomeservice1.com:4443/path
        count: 3
        latency: 1000
        verify: False
        # Ignores the Validity of SSL certificate presented by the server
attack:
    target_type: machine
    agents:
        - type: no_op
```

3. Testplan with `http_request` plugin configured that calls `https://yourawesomeservice1.com:4443/path`
3 times with certain basic Auth credentials and verifies if the latency is within `1000ms`
```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
    type: http_request
    config:
        # Provide Basic Auth credentials in the form of username, Environment variable
        basic_auth: 
            - username
            - type: env
              id: PASSWORD
        urls:
            - https://yourawesomeservice1.com:4443/path
        count: 3
        latency: 1000
attack:
    target_type: machine
    agents:
        - type: no_op
```

4. Testplan with `http_request` plugin configured that calls `https://yourawesomeservice1.com:4443/path`
3 times and verifies if the latency is within `1000ms` and verifies if the status code is either `200(OK)/302(FOUND)`
```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
    type: http_request
    config:
        urls:
            - https://yourawesomeservice1.com:4443/path
        count: 3
        latency: 1000
        status_codes: [200, 302]
attack:
    target_type: machine
    agents:
        - type: no_op
```
