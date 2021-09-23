# OpenTSDB Metrics Verification Plugin

The Metrics verification plugin allows the users of YChaos to verify the
state of the system using OpenTSDB Metrics. If a particular infrastructure is
sending the metrics to an OpenTSDB server, then YChaos can be used to request
the metrics and compare it with a particular comparison logic to assert if the system is
in an expected state

To view the configurations available for OpenTSDB Verification plugin, visit the
schema definition available [here][ychaos.testplan.verification.OpenTSDBVerification] in
package documentation.

!!! Tip
    OpenTSDB is a scalable Time Series Database. To know more about OpenTSDB, visit
    http://opentsdb.net/

## Example Testplans

1. A demo testplan

```yaml
description: A Demo Testplan
verification:
  - states:
      - STEADY
    type: tsdb
    config:
        url: https://tsdb.ychaos.yahoo.com/api/query
        criteria:
          # All the Criterion must pass for YChaos to mark the state as expected (Boolean AND)
          - aggregator: avg
            conditionals:
              # Any of the conditional can pass for YChaos to mark this criteria passed (Boolean OR)
              - comparator: ==
                value: 30.56
        
        # Refer to docs http://opentsdb.net/docs/build/html/api_http/query/index.html
        query: {
          "start": 1356998400,
          "end": 1356998460,
          "queries": [
            {
              "aggregator": "sum",
              "metric": "sys.cpu.0",
              "rate": "true",
              "tags": {
                "host": "*",
                "dc": "lga"
              }
            }
          ]
        }
        
attack:
    target_type: machine
    agents:
        - type: no_op
```
