# ychaos
```
usage: ychaos [-h] [-v] [-V] [--debug] [-c config] [--text-report path]
              [--html-report path] [--log-file path]
              {testplan,manual,agent,verify} ...

positional arguments:
  {testplan,manual,agent,verify}
    testplan            sub command for test plan operations
    manual              Print the manual for YChaos CLI
    agent               ychaos agent CLI
    verify              The verification subcommand of YChaos

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c config, --config config
                        Set YChaos CLI configuration (prod) (default: prod)

verbosity:
  -V, --verbose         Increase verbosity of logs (INFO) (default: 0)
  --debug               Enable debug mode (default: False)

reports:
  --text-report path    Generate a text report from the YChaos execution
                        (default: None)
  --html-report path    Generate a HTML report from YChaos execution (default:
                        None)
  --log-file path       The file to store application logs. Setting
                        `YCHAOS_LOG_FILE` environment variable instead of this
                        argument is also valid. (default: None)

```
## ychaos testplan
```
usage: ychaos testplan [-h] {validate} ...

positional arguments:
  {validate}
    validate  Validate YChaos Test plans

optional arguments:
  -h, --help  show this help message and exit

```
### ychaos testplan validate
```
usage: ychaos testplan validate [-h] path [path ...]

positional arguments:
  path        Space separated list of file/directory paths to validate

optional arguments:
  -h, --help  show this help message and exit

```
## ychaos manual
```
usage: ychaos manual [-h] [-f path]

optional arguments:
  -h, --help            show this help message and exit
  -f path, --file path  Print YChaos CLI Manual to a file (default: None)

```
## ychaos agent
```
usage: ychaos agent [-h] {attack} ...

positional arguments:
  {attack}
    attack    YChaos Agent Attack Subcommand

optional arguments:
  -h, --help  show this help message and exit

```
### ychaos agent attack
```
usage: ychaos agent attack [-h] -t path [--attack-report-yaml path]

optional arguments:
  -h, --help            show this help message and exit
  -t path, --testplan path
                        The testplan path. This can be relative path from
                        where the CLI is initiated (default: None)
  --attack-report-yaml path
                        File Path to store attack report in YAML format
                        (default: None)

```
## ychaos verify
```
usage: ychaos verify [-h] -t path [-s state] [--dump-yaml path]
                     [--dump-json path] [--state-data path]

optional arguments:
  -h, --help            show this help message and exit
  -t path, --testplan path
                        The testplan path. This can be relative path from
                        where the CLI is initiated (default: None)
  -s state, --state state
                        System state to verify (default: steady)
  --state-data path     The path of the verification data state file
                        (JSON/YAML) (default: None)

verification reports:
  --dump-yaml path      Store the verification data in YAML format (default:
                        None)
  --dump-json path      Store the verification data in JSON format (default:
                        None)

```
