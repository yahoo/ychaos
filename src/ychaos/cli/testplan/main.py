#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser, Namespace
from typing import Any

from ychaos.cli import YChaosSubCommand
from ychaos.cli.testplan.validate import TestPlanValidatorCommand
from ychaos.utils.argparse import SubCommandParsersAction

__all__ = ["TestPlan"]


class TestPlan(YChaosSubCommand):
    """
    The testplan sub-command. Provides commands to operate on testplan.
    See Testplan documentation for more details.
    """

    name = "testplan"
    help = "sub command for test plan operations"

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        test_plan_command_subparser = parser.add_subparsers(
            action=SubCommandParsersAction, dest=f"_cmd.{cls.name}"
        )

        test_plan_command_subparser.add_parser(
            name=TestPlanValidatorCommand.name, cls=TestPlanValidatorCommand
        )

        return parser

    @classmethod
    def main(cls, args: Namespace) -> Any:  # pragma: no cover
        pass
