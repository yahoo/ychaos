#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from argparse import Namespace
from io import StringIO

from rich.console import Console

from .main import App


class MockApp(App):
    """
    This will create a mocked application similar to [App][ychaos.cli.main.App]
    whose console output will be tracked by a StringIO object for verification. This is not
    to be used for production and only for testing purposes.
    """

    def __init__(self, args: Namespace):
        if "config" not in args:
            args.config = "dev"
        if "verbose" not in args:
            args.verbose = 0
        if "log_file" not in args:
            args.log_file = None
        if "no_color" not in args:
            args.no_color = None

        super(MockApp, self).__init__(args)
        self.console = Console(file=StringIO(), width=150)

    def get_console_output(self) -> str:
        """
        Returns the entire console output printed by the CLI application during its run

        Returns:
            String
        """
        assert isinstance(self.console.file, StringIO)
        return self.console.file.getvalue()
