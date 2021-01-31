
| CI Pipeline                                                                                                                   | Documentation |
| -----------                                                                                                                   | ------------- |
| [![Build Status](https://screwdriver.ouroath.com/pipelines/1041241/badge)](https://screwdriver.ouroath.com/pipelines/1041241) | [![Documentation](https://git.vzbuilders.com/pages/ssharma06/vzmi.ychaos/_images/badge_documentation_latest.svg)](https://git.vzbuilders.com/pages/ssharma06/vzmi.ychaos) |

----

# ychaos

Python module vzmi.ychaos

## Documentation

The package documentation is available here: [![Documentation](https://git.vzbuilders.com/pages/ssharma06/vzmi.ychaos/_images/badge_documentation_latest.svg)](https://git.vzbuilders.com/pages/ssharma06/vzmi.ychaos)

## This repository structure

### [changelog.d](changelog.d)/

This directory contains user news information to add to the changelog for the package.  

See the [changelog README.md](changelog.d/README.md) for instructions on adding a changelog entry.

### [doc/source](doc/source)/

Sphinx format documentation, if using the sphinx tool for documentation add the documentation files in this directory.

See the [Sphinx Documentation README.md](doc/source/README.md) for instructions on adding sphinx documentation.

### [docs](docs)/

Mkdocs format documentation, if using the [mkdocs](https://www.mkdocs.org/) tool for documentation (the default), the documentation goes in this directory.

See the [Mkdocs Documentation README.md](docs/README.md) for instructions on adding mkdocs documentation.

### [vzmi/ychaos](vzmi/ychaos)/

This directory is for the importable python code for the package.

### [scripts](scripts)/

This directory contains python scripts, any scripts added to this directory are automatically added as scripts to the
package.  The python package utility will install these scripts in the same bin directory as the Python interpreter being
used to do the installation.

### [tests](tests)/

This directory contains unit tests.  Any files added to this directory that are named beginning with `test` will automatically
be run by the test utility.

### [deploy.conf](deploy.conf)

The deploy.conf file is used by the [invirtualenv](https://github.com/yahoo/invirtualenv) utility to generate application packaging including: rpm, yinst, and docker containers.

### [MANIFEST.in](MANIFEST.in)

This file is the package manifest, it specifies the files that are added to the package.  The configuration for this file
is specified in the [Python Packaging Guide](https://packaging.python.org/guides/using-manifest-in/).

**NOTE**: Files need to be specifed in the [MANIFEST.in](MANIFEST.in) and the [setup.cfg](setup.cfg) file in order to be
added to the package.

### [pyproject.toml](pyproject.toml)

This is a standard Python configuration file to define build requirements for the package (things that must be installed before the package can be built/installed).

It can also contain configuration for tooling that is used to work with build requirements such as the [screwdrivercd package
installation utility](https://yahoo.github.io/python-screwdrivercd/Install_Dependencies/)

### [screwdriver.yaml](screwdriver.yaml)

This file contains the Screwdriver CI/CD configuration.

### [sd.allow](sd.allow)

This file specifies what screwdriver jobs may write changes to this git repository.

### [setup.cfg](setup.cfg)

This is the primary Python package configuration file.  See the [Verizon Python Developer Guide setup.cfg](https://git.vzbuilders.com/pages/developer/python-guide/faq/package_configuration_setup_cfg/) document for information about this file.

### [setup.py](setup.py)

This file is the old format package configuration file.  Generally package configuration should use the [setup.cfg](setup.cfg) file.  However this file is sometimes needed for advanced packaging configurations.

See the [Verizon Python Developer Guide setup.py](https://git.vzbuilders.com/pages/developer/python-guide/faq/package_configuration_setup_py/) document for information about working with this file.

