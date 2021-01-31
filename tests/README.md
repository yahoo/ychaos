# Package Tests

This directory contains code to test the code in the package.

## Adding tests

To add a test:

- Create a Python file with a name that begins with the string `test` in this directory.
- In the file include tests the default test runner supports both [unittest](https://docs.python.org/3/library/unittest.html) and [doctest](https://docs.python.org/3/library/doctest.html) test modules.

## Testing locally

There are two ways to run the tests locally:
- [Enable a local git commit hook to run tests before each local git commit]()
- [Manually run the tox test utility manually]()

### Enabling a local git commit hook to run tests
1. Initialize the repository to with the [ouroath_python_project currentrepo init](https://git.vzbuilders.com/pages/Python/ouroath.python_project/currentrepo_command/#initializing-the-local-repository) command.  This command only needs to be run once to configure the testing tools.
2. Add the githook to the repository using the [ouroath_python_project currentrepo enablehook](https://git.vzbuilders.com/pages/Python/ouroath.python_project/currentrepo_command/#installing-the-pre-commit-githook) command. 
3. Use git to commit any changes locally and all the tests will be run automatically each time a git commit is run.
4. Before pushing any changes to the repository run [ouroath_python_project currentrepo deinit](https://git.vzbuilders.com/pages/Python/ouroath.python_project/currentrepo_command/#deinitializing-the-local-repository) command.  This will undo the changes done by the first step.

### Manual testing
1. Initialize the repository to with the [ouroath_python_project currentrepo init](https://git.vzbuilders.com/pages/Python/ouroath.python_project/currentrepo_command/#initializing-the-local-repository) command.  This command only needs to be run once to configure the testing tools.
2. Run the [tox](https://tox.readthedocs.io/en/latest/) command to test the code locally.  This command can be rerun multiple times to continue testig the code.
3. Before pushing changes to the repository run [ouroath_python_project currentrepo deinit](https://git.vzbuilders.com/pages/Python/ouroath.python_project/currentrepo_command/#deinitializing-the-local-repository) command.  This will undo the changes done by the first step.
