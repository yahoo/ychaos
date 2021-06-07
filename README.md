
<!-- TODO Add other badges (SDv4, codecov, chat, -->
![Python Support](https://img.shields.io/pypi/pyversions/ychaos)
[![PyPi](https://img.shields.io/pypi/status/ychaos)](https://pypi.org/project/ychaos/)
[![Code Style](https://img.shields.io/badge/codestyle-black-black)](https://black.readthedocs.io/en/stable/index.html)
[![Documentation](https://img.shields.io/badge/Documentation-latest-blue)](https://yahoo.github.io/ychaos)
[![License](https://img.shields.io/github/license/yahoo/ychaos)](https://github.com/yahoo/ychaos/blob/main/LICENSE)

# ychaos

The Resilience Toolkit

YChaos is a self-serving chaos testing toolkit designed to
provide users with all the capabilities of doing an end to end resilience
testing of your service. YChaos is designed to give users a framework
to validate, verify and attack your system to simulate real life
failures that might cause outages in your service.

To get started, refer to the [documentation](https://yahoo.github.io/ychaos)

## Install

To install ychaos,

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
python setup.py develop easy_install ychaos[<subpackage>]
```

## Usage

Refer to the documentation to know about the usage.

## Maintainers

<!-- TODO Add Team Email -->
[The Resilience Team @yahoo](ychaos-dev@verizonmedia.com)

## License

This project is licensed under the terms of the Apache 2.0 open source license. 
Please refer to [LICENSE](https://github.com/yahoo/ychaos/blob/main/LICENSE) for the full terms.