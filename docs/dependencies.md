# Package Dependencies

## Installation Dependencies

To install the latest version of the package, run

```bash
pip install ychaos
```

The above command will install the package and also all
the required dependencies of the project.

| Project Dependencies | Project Link                                     | License Type        | License URL                                                          |
| -------------------- | ------------------------------------------------ | --------------------| -------------------------------------------------------------------- |
| pydantic             | [LINK](https://github.com/samuelcolvin/pydantic) | MIT                 | [LINK](https://github.com/samuelcolvin/pydantic/blob/master/LICENSE) |
| rich                 | [LINK](https://github.com/willmcgugan/rich)      | MIT                 | [LINK](https://github.com/willmcgugan/rich/blob/master/LICENSE)      |
| pyyaml               | [LINK](https://github.com/yaml/pyyaml)           | MIT                 | [LINK](https://github.com/yaml/pyyaml/blob/master/LICENSE)           |
| psutil  *            | [LINK](https://github.com/giampaolo/psutil)      | BSD-3-Clause        | [LINK](https://github.com/giampaolo/psutil/blob/master/LICENSE)
| pyOpenSSL *          | [LINK](https://github.com/pyca/pyopenssl)        | Apache 2.0          | [LINK](https://github.com/pyca/pyopenssl/blob/main/LICENSE)

^* Optional dependencies

----

## Test and Code Analysis dependencies (for developers only)

The following section contains the dependencies required for the
development of the project. All these dependencies are bundled in a
separate configuration called "debug"

To install all the dependencies at once you can run

```bash
pip install -e ".[debug]"
```

Or you can also make use of the bash script available in the `develop`
directory,

```bash
./develop/make.sh
```

### Unittest

| Project Dependencies | Project Link                                           | License Type         | License URL                                                                |
| -------------------- | -----------------------------------------------        | -------------------- | -------------------------------------------------------------------        |
| mockito              | [LINK](https://github.com/kaste/mockito-python)        | MIT                  | [LINK](https://github.com/kaste/mockito-python/blob/master/LICENSE)        |
| pytest               | [LINK](https://github.com/pytest-dev/pytest)           | MIT                  | [LINK](https://github.com/pytest-dev/pytest/blob/master/LICENSE)           |
| pytest-cov           | [LINK](https://github.com/pytest-dev/pytest-cov)       | MIT                  | [LINK](https://github.com/pytest-dev/pytest-cov/blob/master/LICENSE)       |
| pytest-timeout       | [LINK](https://github.com/pytest-dev/pytest-timeout)   | MIT                  | [LINK](https://github.com/pytest-dev/pytest-timeout/blob/master/LICENSE)   |
| cryptography         | [LINK](https://github.com/pyca/cryptography)           | Apache/BSD           | [LINK](https://github.com/pyca/cryptography/blob/main/LICENSE)             |

### Code styling and validation

| Project Dependencies | Project Link                            | License Type | License URL                                                 |
| -------------------- | --------------------------------------- | ------------ | ----------------------------------------------------------- |
| black                | [LINK](https://github.com/psf/black)    | MIT          | [LINK](https://github.com/psf/black/blob/master/LICENSE)    |
| flake8               | [LINK](https://github.com/PyCQA/flake8) | MIT          | [LINK](https://github.com/psf/black/blob/master/LICENSE)    |
| isort                | [LINK](https://github.com/PyCQA/isort)  | MIT          | [LINK](https://github.com/PyCQA/isort/blob/develop/LICENSE) |

### Code Analysis

| Project Dependencies | Project Link                            | License Type | License URL                                                 |
| -------------------- | --------------------------------------- | ------------ | ----------------------------------------------------------- |
| mypy                 | [LINK](https://github.com/python/mypy)  | MIT          | [LINK](https://github.com/python/mypy/blob/master/LICENSE)  |
| bandit               | [LINK](https://github.com/PyCQA/bandit) | Apache 2.0   | [LINK](https://github.com/PyCQA/bandit/blob/master/LICENSE) |

## Documentation build/publish dependencies

| Project Dependencies          | Project Link                                                          | License Type | License URL                                                                                |
| --------------------          | ------------------------------------------------------                | ------------ | -----------------------------------------------------------------------------              |
| mkdocs                        | [LINK](https://github.com/mkdocs/mkdocs)                              | BSD-2-Clause | [LINK](https://github.com/mkdocs/mkdocs/blob/master/LICENSE)                               |
| mkdocs-material               | [LINK](https://github.com/squidfunk/mkdocs-material/)                 | MIT          | [LINK](https://github.com/squidfunk/mkdocs-material/blob/master/LICENSE)                   |
| mkdocs-awesome-pages-plugin   | [LINK](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)    | MIT          | [LINK](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin/blob/master/LICENSE.md)  |
| mike                          | [LINK](https://github.com/jimporter/mike)                             | BSD-3-Clause | [LINK](https://github.com/jimporter/mike)                                                  |
