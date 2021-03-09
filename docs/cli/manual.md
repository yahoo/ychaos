# ychaos
```
usage: ychaos [-h] [-v] [-V] [--debug] [-c {dev,prod}]
              [--text-report TEXT_REPORT] [--html-report HTML_REPORT]
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
  -c {dev,prod}, --config {dev,prod}
                        Set YChaos CLI configuration (prod)

verbosity:
  -V, --verbose         Increase verbosity of logs (INFO)
  --debug               Enable debug mode

reports:
  --text-report TEXT_REPORT
                        Generate a text report from the YChaos execution
  --html-report HTML_REPORT
                        Generate a HTML report from YChaos execution

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
usage: ychaos testplan validate [-h] paths [paths ...]

positional arguments:
  paths       Space separated list of file/directory paths to validate

optional arguments:
  -h, --help  show this help message and exit

```
## ychaos manual
```
usage: ychaos manual [-h] [-f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Print YChaos CLI Manual to a file

```
## ychaos agent
```
usage: ychaos agent [-h] {attack} ...

positional arguments:
  {attack}
    attack    ychaos agent attack CLI

optional arguments:
  -h, --help  show this help message and exit

```
### ychaos agent attack
```
usage: ychaos agent attack [-h] -t TESTPLAN

optional arguments:
  -h, --help            show this help message and exit
  -t TESTPLAN, --testplan TESTPLAN
                        The testplan path. This can be relative path from
                        where the CLI is initiated

```
## ychaos verify
```
usage: ychaos verify [-h] -t TESTPLAN -s {steady,chaos,recovered}
                     [--dump-yaml DUMP_YAML] [--dump-json DUMP_JSON]
                     [--state-data STATE_DATA]

optional arguments:
  -h, --help            show this help message and exit
  -t TESTPLAN, --testplan TESTPLAN
                        The testplan path. This can be relative path from
                        where the CLI is initiated
  -s {steady,chaos,recovered}, --state {steady,chaos,recovered}
                        System state to verify
  --dump-yaml DUMP_YAML
                        Store the verification data in YAML format
  --dump-json DUMP_JSON
                        Store the verification data in JSON format
  --state-data STATE_DATA
                        The path of the verification data state file
                        (JSON/YAML)

```
