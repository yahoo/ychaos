# ychaos
```
usage: ychaos [-h] [-v] [-V] [-c {dev,prod}] {testplan,manual} ...

positional arguments:
  {testplan,manual}
    testplan            sub command for test plan operations
    manual              Print the manual for YChaos CLI

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -V, --verbose         Increase verbosity of logs (INFO)
  -c {dev,prod}, --config {dev,prod}
                        Set YChaos CLI configuration (prod)

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
