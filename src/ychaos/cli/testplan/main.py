#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser

from ...utils.argparse import SubCommandParsersAction
from .. import YChaosSubCommand
from .validate import TestPlanValidatorCommand

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
