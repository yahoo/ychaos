# Contribution

## How to setup this repository on Local Machine?

1. Clone the repository on your local machine

    ```bash
    git clone git@git.vzbuilders.com:`whoami`/vzmi.ychaos.git
    ```

2. Setup the project on an IDE (Preferrably PyCharm).

    !!! Note
        It is recommended to install [pydantic plugin for Pycharm](https://pydantic-docs.helpmanual.io/pycharm_plugin/)

3. After [creating a virtual environment for the project](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html),
install the editable version of the package

    ```bash
    pip install -e .[debug]
    ```
    
    !!! Note
        If you are using zsh, you will have to run `pip install -e ".[debug]"`

4. Add your code changes in the required files and commit the changes to a branch. Include documentation
to the code added using the [Google docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) format.

5. Commit the file and include a meaningful name to the commit. If the changes to the code
are more than huge, it is advised to split the commits into multiple.

## How to run Screwdriver validations locally?

!!! Note
    If you have installed the development package with `debug` extension, then all of these
    packages required for screwdriver validations will already be installed in your virtual environment.

To run all the code analysis steps locally run `make build`. To
run unittests locally, run `make test`.

## Coding standards

This section of the document contains some of the coding standards
followed in this package. It is recommended to read this and follow this
for any contribution. Some of the preferred way of standards are mentioned.
Although, most of the sub sections are provided with reasoning, this is not an
official coding standard and can vary in special conditions.

!!! hint
    Note that this is a constantly updating section of the document
    and will receive more items based on our experience.

### Imports

#### Importing class

If you are importing a class from a module, then import only the class from the module 
instead of importing the entire module.

For example:

=== "Preferred"

    ```python
    from pathlib import Path
    mock_path = Path("/home/awesomeuser/mockdirectory")
    ```

=== "Avoid"

    ```python
    import pathlib
    mock_path = pathlib.Path("/home/awesomeuser/mockdirectory")
    ```

#### Importing attributes/methods from module

In case you want to import a method or an attribute from the module, 
whose name starts with a small alphabet, then import the module instead of
method or attribute.

**Reasoning**: If the module under change already has a variable named
same as method/attribute, this will make you do an extra work of renaming
all of those variables.

For example:

=== "Preferred"

    ```python
    import os
    print(os.cpu_count())
    ```

=== "Avoid"
    
    ```python
    from os import cpu_count
    print(cpu_count())
    ```

### `@staticmethod` vs `@classmethod`

We generally use class method to create factory methods. Factory methods return classobject
(similar to a constructor) for different use cases. We generally use static methods to create
utility functions.

### One Line if statements

Use one line if statements if there is an else block defined and has some
piece of code. If the else block just contains `None`, use a simple if statement

=== "Preferred"

    ```python
    if True:
        sum([1, 4, -3, 19])
    ```

=== "Avoid"
    
    ```python
    sum([12, 4, -3, 10]) if True else None
    ```
    
### Path operations

Use [pathlib](https://docs.python.org/3/library/pathlib.html) for path operation instead of
`os.path` as this has better methods of operating on path. It also has utility methods to resolve
expand user etc. 