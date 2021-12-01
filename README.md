
<!-- TODO Add other badges (codecov, chat, etc.) -->
[![CI Pipeline](https://cd.screwdriver.cd/pipelines/7419/badge)](https://cd.screwdriver.cd/pipelines/7419/)
[![codecov](https://codecov.io/gh/yahoo/ychaos/branch/main/graph/badge.svg?token=UA7QNZ6QOQ)](https://codecov.io/gh/yahoo/ychaos)
![Python Support](https://img.shields.io/pypi/pyversions/ychaos)
[![PyPi](https://img.shields.io/pypi/status/ychaos)](https://pypi.org/project/ychaos/)
[![Code Style](https://img.shields.io/badge/codestyle-black-black)](https://black.readthedocs.io/en/stable/index.html)
[![Documentation](https://img.shields.io/badge/Documentation-latest-blue)](https://yahoo.github.io/ychaos)
[![License](https://img.shields.io/github/license/yahoo/ychaos)](https://github.com/yahoo/ychaos/blob/main/LICENSE)

# ychaos

YChaos is a self-serving chaos testing toolkit designed to
provide users with all the capabilities of doing an end to end resilience
testing of your service. YChaos is designed to give users a framework
to validate, verify and attack your system to simulate real life
failures that might cause outages in your service.

To get started with YChaos, refer to the [documentation](https://yahoo.github.io/ychaos)

## Table of contents

1. [Background](#background)
1. [Install](#install)
1. [Usage](#usage)
1. [Maintainers](#maintainers)
1. [License](#license)

## Background

The most important aspect of maintaining a web service on cloud
infrastructure is to make it resilient from failures. Most of
these failures are unexpected and are not tested while development.
The service which is capable of handling an unexpected failure passes the
criteria of a resilient service.

YChaos provides a self-serving framework to inject these unexpected failures
into your service in the form of YChaos Agents and understand if your service
is equipped to handle unknown failures either within the service
or from a 3rd party service dependency.

## Install

To install ychaos from PyPi,

```bash
pip install ychaos[<subpackage>]
```

The following subpackages are available for usage
1. agents : `pip install ychaos[agents]`
2. chaos : `pip install ychaos[chaos]`

To know more about each subpackage and what they do, refer to the [documentation](https://yahoo.github.io/ychaos)

You can also install the package from the source code.

```bash
git clone https://github.com/yahoo/ychaos
cd ychaos
pip install ".[<subpackage>]"
```

## Usage

Refer to the [documentation](https://yahoo.github.io/ychaos) to know about the usage.

## Maintainers

[The Resilience Team @yahoo](mailto://ychaos-dev@yahooinc.com)

## License

This project is licensed under the terms of the Apache 2.0 open source license. 
Please refer to [LICENSE](https://github.com/yahoo/ychaos/blob/main/LICENSE) for the full terms.
