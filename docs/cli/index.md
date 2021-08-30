# YChaos CLI

YChaos CLI provides a set of commands that can be run
from your console to perform various operations with YChaos.
Starting with the testplan validation and up to performing attack
is a part of YChaos CLI.

YChaos CLI's structure is defined below

```bash
ychaos --<GLOBAL_ARGUMENTS> [<SUBCOMMAND> --<SUBCOMMAND_ARGUMENTS>]...
```

1. The GLOBAL_ARGUMENTS refer to the arguments that mostly configures
how the YChaos CLI runs.
2. SUBCOMMAND refers to the individual operations that can be performed with
like `verify`, `testplan` etc. Each subcommand can contain commands under those.
3. The SUBCOMMAND_ARGUMENTS basically configures they way each subcommand
runs.
   
To view the usage of YChaos CLI visit the [documentation](manual.md) or
run `ychaos manual` on command line. To view the documentation of Individual
components of YChaos CLI, visit [package_docs](#)
