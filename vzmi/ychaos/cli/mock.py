from argparse import Namespace
from io import StringIO

from rich.console import Console

from vzmi.ychaos.cli.main import App


class MockApp(App):
    """
    To be used for Unittest purpose only. This will create a mocked
    application whose console output will be tracked by a String
    object.

    This class is not for production usecase.
    """

    def __init__(self, args: Namespace):
        if "config" not in args:
            args.config = "dev"
        if "verbose" not in args:
            args.verbose = 0

        super(MockApp, self).__init__(args)
        self.console = Console(file=StringIO(), width=150)

    def get_console_output(self):
        assert isinstance(self.console.file, StringIO)
        return self.console.file.getvalue()
