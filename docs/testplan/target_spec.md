---
hide:
  - toc        # Hide table of contents
---

# Target Type and Configuration

The attack configuration defined in Testplan takes 2 required
attributes `target_type` and `target_config` that defines the type of 
target the tool is intended to attack. 

Each of the `target_type` defines what are the configuration attributes needed
for `target_config`. In other words, the schema of `target_config` depends upon
the type of target defined. This document provides schema and definition for
each of the target types available in the package.

## Machine (`machine`)

::: ychaos.testplan.attack.MachineTargetDefinition
    selection:
        filters:
        - "!"
    rendering:
        heading_level: 4
        attributes: False
        show_root_full_path: False
   
## Localhost (`self`)

::: ychaos.testplan.attack.SelfTargetDefinition