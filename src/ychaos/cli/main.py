#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from rich.console import Console
from rich.table import Table

from ..app_logger import AppLogger
from ..settings import ApplicationSettings, DevSettings, ProdSettings, Settings
from ..utils.argparse import SubCommandParsersAction
from . import YChaosArgumentParser, YChaosSubCommand
from .agent.main import Agent
from .execute import Execute
from .manual import Manual
from .testplan import TestPlan
from .verify import Verify


class YChaos:
    """
    The YChaos CLI class. The `main` method of this class is the starting point of
    the CLI which takes in the program arguments. See YChaos CLI documentation for
    more details.

    To see the usage of the YChaos CLI, run `ychaos -h` on the terminal
    """

    settings = ApplicationSettings.get_instance()

    @classmethod
    def main(cls, program_arguments: list) -> None:
        """
        All good things begin some place, and that's here.
        Args:
            program_arguments: List of Program Arguments

        Returns:
            None
        """
        ychaos_cli = YChaosArgumentParser(
            prog=cls.settings.PROG,
            formatter_class=ArgumentDefaultsHelpFormatter,
            __root__=YChaosRoot,
        )

        # YChaos CLI version
        ychaos_cli.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"v{cls.settings.get_version()} [yahoo/ychaos]",
        )

        # Verbosity Argument Group
        verbosity_argument_group = ychaos_cli.add_argument_group("verbosity")
        verbosity_argument_group.add_argument(
            "-V",
            "--verbose",
            action="count",
            help="Increase verbosity of logs (INFO)",
            default=0,
            required=False,
        )
        verbosity_argument_group.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode",
            default=False,
            required=False,
        )

        # Configuration for the ychaos Command Line Interface
        ychaos_cli.add_argument(
            "-c",
            "--config",
            choices=["dev", "prod"],
            default="prod",
            help="Set YChaos CLI configuration (prod)",
            metavar="config",
        )

        ychaos_cli.add_argument(
            "--no-color",
            action="store_true",
            default=bool(os.getenv("NO_COLOR", False)),
            help="Disable color on console output ($NO_COLOR)",
        )

        # Arguments for creating HTML & Text Reports
        report_argument_group = ychaos_cli.add_argument_group("reports")
        report_argument_group.add_argument(
            "--text-report",
            type=Path,
            default=None,
            required=False,
            help="Generate a text report from the YChaos execution",
            metavar="path",
        )
        report_argument_group.add_argument(
            "--html-report",
            type=Path,
            default=None,
            required=False,
            help="Generate a HTML report from YChaos execution",
            metavar="path",
        )
        report_argument_group.add_argument(
            "--log-file",
            type=Path,
            default=os.getenv("YCHAOS_LOG_FILE"),
            required=False,
            help=("The file to store application logs. ($YCHAOS_LOG_FILE)"),
            metavar="path",
        )

        ychaos_cli_subparsers = ychaos_cli.add_subparsers(
            action=SubCommandParsersAction,
            dest=cls.settings.COMMAND_IDENTIFIER.format(cls.settings.PROG),
        )

        assert isinstance(ychaos_cli_subparsers, SubCommandParsersAction)

        # Subcommands
        ychaos_cli_subparsers.add_parser(cls=TestPlan)
        ychaos_cli_subparsers.add_parser(cls=Manual)
        ychaos_cli_subparsers.add_parser(cls=Agent)
        ychaos_cli_subparsers.add_parser(cls=Verify)
        ychaos_cli_subparsers.add_parser(cls=Execute)

        args = ychaos_cli.parse_args(program_arguments)

        args.app = App(args, ychaos_cli)

        # Start the Application
        args.app.start()

        # Call the right method for the subcommand
        try:
            exitcode = ychaos_cli.run_command(args)
        except Exception as unknown_error:  # pragma: no cover
            exitcode = 255
            args.app.unknown_error()

        # Teardown
        args.app.teardown(exitcode)

        sys.exit(exitcode)


class App:
    def __init__(self, args: Namespace, cli: Optional[ArgumentParser] = None):
        Settings(args.config)

        args.verbose = min(2, args.verbose)

        self.args = args
        self.console = Console(record=True, no_color=args.no_color)
        self.settings: Union[DevSettings, ProdSettings] = Settings.get_instance()

        self.cli = cli

        if args.log_file:
            self.settings.LOG_FILE_PATH = args.log_file

        AppLogger()

    def start(self) -> None:
        self.console.clear()
        self.console.rule(
            title=self.settings.APP_DESC,
            style="magenta",
        )

        if self.args.cls != YChaosRoot:
            self.print_cli_configuration()
            self.console.line()
            self.console.log("Starting app")

    def get_command_tree(self) -> List[str]:
        """
        Determines the command tree of the invoked command.

        Returns:
            List of commands starting with `ychaos` and ending at the sub-command invoked
        """
        _args = vars(self.args)

        parent = self.settings.PROG
        branch = _args.get(self.settings.COMMAND_IDENTIFIER.format(parent), None)

        tree = []
        while branch is not None:
            tree.append(parent)
            parent = branch
            branch = _args.get(self.settings.COMMAND_IDENTIFIER.format(parent), None)

        tree.append(parent)
        return tree

    def _walk_parser(self, parser: ArgumentParser, tree):
        """
        Walk the Argument parser and collect all the subcommands and its help message.

        Args:
            parser: Argument Parser

        Returns:
            Tree dictionary
        """
        if parser._subparsers is not None:
            for action in parser._subparsers._actions:
                if isinstance(action, SubCommandParsersAction):
                    for command, subparser in action.choices.items():
                        tree[subparser.prog] = subparser.format_help()
                        tree = self._walk_parser(subparser, tree)
        return tree

    def manual_entry(self) -> Dict[str, str]:
        """
        Determines the manual entry of the YChaos CLI and returns a program
        aware dictionary of cli -> usage mapping

        Returns:
            Dictionary of command to help message mapping
        """
        _tree = OrderedDict()
        assert self.cli is not None
        _tree[self.settings.PROG] = self.cli.format_help()
        self._walk_parser(self.cli, _tree)

        return _tree

    def is_debug_mode(self) -> bool:
        """
        Returns if the app was initialized with debug mode
        Returns:
            True if debug mode
        """
        return self.args.debug

    def print_cli_configuration(self):
        self.console.line()
        table = Table(title="YChaos CLI configuration", header_style="bold green")
        table.add_column("Configuration", style="bold sea_green2")
        table.add_column("Value")

        _renderable_config = vars(self.args).copy()
        _renderable_config.pop("app")
        _renderable_config.pop("cls")

        _renderable_config["_command_"] = " :arrow_right: ".join(
            self.get_command_tree()
        )

        for k, v in sorted(_renderable_config.items()):
            if not k.startswith("_cmd"):
                if isinstance(v, Iterable) and not isinstance(v, str):
                    v = "\n".join([str(_v) for _v in v])
                if v is not None:
                    table.add_row(str(k), str(v))

        self.console.print(table)

    def unknown_error(self):
        self.console.line()
        self.console.print_exception(extra_lines=2)

    def teardown(self, exitcode: int) -> None:
        if self.args.cls != YChaosRoot:
            self.console.line()
            self.console.log(f"Exiting with exitcode={exitcode}")
            self.console.rule(
                title=":sunny:",
                style="magenta",
            )

        # Save Reports
        if self.args.text_report:
            self.console.save_text(self.args.text_report)

        if self.args.html_report:
            self.console.save_html(self.args.html_report)


class YChaosRoot(YChaosSubCommand):
    """
    The YChaos root command. This class is invoked when the ychaos
    cli is invoked without any subcommands
    """

    @classmethod
    def main(cls, args: Namespace) -> Any:
        """
        Does Nothing.
        Args:
            args: Arguments

        Returns:
            0 (Zero) exitcode
        """
        return 0


# This is where it all started..
def main():
    YChaos.main(sys.argv[1:])
