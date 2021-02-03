# Contribution

## How to setup this repository on Local Machine?

1. Clone the repository on your local machine

    ```bash
    git clone git@git.vzbuilders.com:`whoami`/vzmi.ychoas.git
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

You can also run all of the screwdriver validations at once using the script
provided in the `develop` directory. Change the permission using `chmod +x develop/validate.sh`
and run the script `./develop/validate.sh` to run all validations at once.