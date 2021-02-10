#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from argparse import Namespace
from io import StringIO

from vzmi.ychaos.cli.main import App
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))


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
