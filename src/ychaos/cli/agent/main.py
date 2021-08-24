#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser

from ...utils.argparse import SubCommandParsersAction
from .. import YChaosSubCommand
from .attack import Attack

__all__ = ["Agent"]


class Agent(YChaosSubCommand):
    """
    The Agent subcommand used to operate on YChaos agents. Most of the subcommands
    under `agent` requires testplan.
    """

    name = "agent"
    help = "The agent subcommand of YChaos"

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        test_plan_command_subparser = parser.add_subparsers(
            action=SubCommandParsersAction, dest=f"_cmd.{cls.name}"
        )
        assert isinstance(test_plan_command_subparser, SubCommandParsersAction)

        test_plan_command_subparser.add_parser(cls=Attack)
        return parser
