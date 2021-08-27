#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from abc import ABC
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional

from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from ..testplan.schema import TestPlan
from ..utils.argparse import SubCommand
from .exceptions import YChaosCLIError


class YChaosArgumentParser(ArgumentParser):
    """
    YChaosArgumentParser serves as a special parser to parse the
    CLI commands for ychaos. It provides utility methods to parse arguments,
    pass subcommand implementation and run a subcommand. It also handles
    the CLI exception gracefully by running the `handle` method of the exception raised.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a YChaos Argument parser.

        Args:
            **kwargs: `__root__` for the root execution when no subcommand is thrown.
        """
        # __root__ SubCommand class determines the root of the YChaos
        # i.e. when YChaos CLI is called without any arguments
        self.__root__ = kwargs.pop("__root__", None)

        super(YChaosArgumentParser, self).__init__(*args, **kwargs)

    def parse_args(self, args=None, namespace=None) -> Namespace:  # type: ignore
        args = super(YChaosArgumentParser, self).parse_args(args, namespace)
        if not hasattr(args, "cls"):
            assert issubclass(self.__root__, SubCommand)
            args.cls = self.__root__

        return args

    def run_command(self, args: Namespace) -> int:
        """
        Run a subcommand from YChaos CLI
        """
        try:
            exitcode = args.cls.main(args)
        except YChaosCLIError as e:
            e.handle()
            exitcode = e.exitcode

        return exitcode


class YChaosSubCommand(SubCommand, ABC):

    _exitcode = 0

    def __init__(self, **kwargs):
        assert kwargs.pop("cls") == self.__class__

        self.app = kwargs.pop("app")
        self.console: Console = self.app.console

    def set_exitcode(self, exitcode=0):
        self._exitcode = exitcode

    @classmethod
    def main(cls, args: Namespace) -> Any:
        args.app.console.log("This command does nothing..")
        return 0


class YChaosTestplanInputSubCommand(YChaosSubCommand, ABC):
    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(
            "-t",
            "--testplan",
            type=Path,
            required=True,
            help="The testplan path. This can be relative path from where the CLI is initiated",
            metavar="path",
        )

        return parser

    def get_validated_test_plan(self, path: Path) -> Optional[TestPlan]:
        self.console.log("Getting Test plan")
        self.console.line()
        try:
            testplan = TestPlan.load_file(path=path)
            return testplan
        except ValidationError as validation_error:
            self.set_exitcode(1)
            self.console.print(
                Panel.fit(str(validation_error), title="Validation Error", style="red")
            )
        except IsADirectoryError as is_directory:
            self.set_exitcode(1)
            self.console.print(
                ":file_folder: The input path ({path}) is not a valid testplan file".format(
                    path=path
                )
            )
        except FileNotFoundError as file_not_found_error:
            self.set_exitcode(1)
            self.console.print(
                ":mag: {file} [italic]not found[/italic]".format(file=str(path)),
                style="indian_red",
            )
        return None


class YChaosCLIHook(ABC):
    """
    The Base CLI Hook. Implement the `__call__` method with appropriate signature
    for each of the hook type. The `__call__` method gets called from the EventHook
    methods whenever an event is occurred.
    """

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.console = app.console

        # Determines if this hooks is active and callable.
        self.active = True
