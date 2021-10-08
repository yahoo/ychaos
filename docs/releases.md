# Changelog

## Version 0.x.x

### Version 0.4.0

1. Add `SelfTargetExecutor`, that runs the agents on the same machine from where 
YChaos is triggerred by [Alfin S Thomas](https://github.com/AlfinST)

### Version 0.3.0

1. Add Disk Fill Agent by [Lakshmi Kannan](https://github.com/lakshmi-k05)

1. Fix importing non-required PyOpenSSL module by [Shashank Sharma](https://github.com/shashankrnr32)
and [Vijay Babu](https://github.com/vijaybabu4589)

1. Dependabot integration to the repository by [Irfan Mohammad ](https://github.com/nafri-irfan96)

1. Integrate codespell to the repository by [Shashank Sharma](https://github.com/shashankrnr32)

1. Add No-Color Docs to FAQ by [Shashank Sharma](https://github.com/shashankrnr32)

1. Python3.10 validation in CI build by [Shashank Sharma](https://github.com/shashankrnr32)

1. Fix importing not-needed PyOpenSSL dependency by [Shashank Sharma](https://github.com/shashankrnr32)

1. Add Callable Mapping to Hooks by [Shashank Sharma](https://github.com/shashankrnr32)

1. Add documentation for HTTP Request & SDv4 verification plugin by [Shashank Sharma](https://github.com/shashankrnr32)

1. refactor delay_before after checking state by [Alfin S Thomas](https://github.com/AlfinST)

1. Handle dump yaml/json File not found error by [Sushil Karimbumkara](https://github.com/sushilkar)

1. Implement and documentation of OpenTSDB Verification Plugin by [Shashank Sharma](https://github.com/shashankrnr32)

### Version 0.2.0

1. Fix throwing error when a verification plugin implementation is not found or in development stage
by [Shashank Sharma](https://github.com/shashankrnr32)

1. Remove the requirement of virtualenv package on remote host by using venv by [Alfin S Thomas](https://github.com/AlfinST)

### Version 0.1.0

1. Add documentation to YChaos by [Shashank Sharma](https://github.com/shashankrnr32)
   
1. Minor Bug Fixes for MachineTarget Executor by [Alfin S Thomas](https://github.com/AlfinST), [Shashank Sharma](https://github.com/shashankrnr32)

1. Add Machine Target Executor to connect to targets and execute attack by Shashank Sharma

1. Add Coordinator module by [Vijay Babu](https://github.com/vijaybabu4589)

1. Introduce Event Hooks for circling back useful information from core components to client 
code (CLI) by [Shashank Sharma](https://github.com/shashankrnr32)

1. Add System state verification to YChaos by [Shashank Sharma](https://github.com/shashankrnr32)

    - Add Python Module Verification Module.
    - Add HTTP Verification Plugin.
    - Add `verify` subcommand to YChaos CLI.
    - Add Screwdriver job verification to YChaos (Beta).

1. Add Chaos Agent Definition to YChaos by [Shashank Sharma](https://github.com/shashankrnr32)

    - Add system agents.
    - Add Ping disable agent.
    - Add IPTables block agent by [Rahul R](https://github.com/r-r-2)
    - Add Traffic block agent.
    - Add DNS Block agent.
    - Add Contrib agent that enables users to write their own agents.

1.  Add CLI subcommands for testplan validation, manual, agent to YChaos by 
    [Shashank Sharma](https://github.com/shashankrnr32), [Vijay Babu](https://github.com/vijaybabu4589)

1. Add Testplan Schema and schema documentation to YChaos by [Shashank Sharma](https://github.com/shashankrnr32)

1. Other improvements (CI/Documentation/Package/Dev)
   
   - Add Optional dependency handler by [Shashank Sharma](https://github.com/shashankrnr32)
   - Add Logging module for YChaos by [Vijay Babu](https://github.com/vijaybabu4589)
   - Add Log Agent Lifecycle decorator by [Shashank Sharma](https://github.com/shashankrnr32)
   - Allow custom log file via CLI by [Shashank Sharma](https://github.com/shashankrnr32)
