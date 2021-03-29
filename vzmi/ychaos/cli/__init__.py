#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from abc import ABC
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional

from pydantic import ValidationError

from vzmi.ychaos.testplan.schema import TestPlan
from vzmi.ychaos.utils.argparse import SubCommand
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))
(Panel,) = DependencyUtils.import_from("rich.panel", ("Panel",))


class YChaosSubCommand(SubCommand, ABC):

    _exitcode = 0

    def __init__(self, **kwargs):
        pass  # Abstract method

    def set_exitcode(self, exitcode=0):
        self._exitcode = exitcode


class YChaosTestplanInputSubCommand(YChaosSubCommand, ABC):

    console: Any

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
