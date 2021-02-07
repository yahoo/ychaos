from argparse import ArgumentParser, Namespace
from typing import Any

from vzmi.ychaos.cli.testplan.validate import TestPlanValidatorCommand
from vzmi.ychaos.utils.argparse import SubCommand, SubCommandParsersAction

__all__ = ["TestPlan"]


class TestPlan(SubCommand):
    """
    ```
    $ ychaos testplan -h
    usage: ychaos testplan [-h] {validate} ...

    positional arguments:
      {validate}
        validate  Validate YChaos Test plans

    optional arguments:
      -h, --help  show this help message and exit
    ```
    """

    name = "testplan"
    help = "sub command for test plan operations"

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        test_plan_command_subparser = parser.add_subparsers(
            action=SubCommandParsersAction, dest="_cmd.{}".format(cls.name)
        )

        test_plan_command_subparser.add_parser(
            name=TestPlanValidatorCommand.name, cls=TestPlanValidatorCommand
        )

        return parser

    @classmethod
    def main(cls, args: Namespace) -> Any:  # pragma: no cover
        pass
