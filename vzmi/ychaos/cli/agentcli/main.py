#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser, Namespace

from vzmi.ychaos.cli import YChaosSubCommand
from vzmi.ychaos.cli.agentcli.attack import Attack
from vzmi.ychaos.utils.argparse import SubCommandParsersAction
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))

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

        test_plan_command_subparser.add_parser(name=Attack.name, cls=Attack)
        return parser

    @classmethod
    def main(cls, args: Namespace):
        pass
