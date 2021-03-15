#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

import sys
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from vzmi.ychaos import __version__
from vzmi.ychaos.app_logger import AppLogger
from vzmi.ychaos.cli import YChaosSubCommand
from vzmi.ychaos.cli.agentcli.main import AgentCLI
from vzmi.ychaos.cli.exceptions import YChaosCLIError
from vzmi.ychaos.cli.manual import Manual
from vzmi.ychaos.cli.testplan import TestPlan
from vzmi.ychaos.cli.verification import VerificationCommand
from vzmi.ychaos.settings import (
    ApplicationSettings,
    DevSettings,
    ProdSettings,
    Settings,
)
from vzmi.ychaos.utils.argparse import SubCommandParsersAction
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))
(Table,) = DependencyUtils.import_from("rich.table", ("Table",))


class YChaos:
    """
    The YChaos CLI class. The `main` method of this class is the starting point of
    the CLI which takes in the program arguments. See YChaos CLI documentation for
    more details.

    ```
    $ ychaos -h
    usage: ychaos [-h] [-v] [-V] [--debug] [-c {dev,prod}]
                  [--text-report TEXT_REPORT] [--html-report HTML_REPORT]
                  {testplan,manual,agent} ...

    positional arguments:
      {testplan,manual,agent}
        testplan            sub command for test plan operations
        manual              Print the manual for YChaos CLI
        agent               ychaos agent CLI

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -c {dev,prod}, --config {dev,prod}
                            Set YChaos CLI configuration (prod)

    verbosity:
      -V, --verbose         Increase verbosity of logs (INFO)
      --debug               Enable debug mode

    reports:
      --text-report TEXT_REPORT
                            Generate a text report from the YChaos execution
      --html-report HTML_REPORT
                            Generate a HTML report from YChaos execution
    ```
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
        ychaos_cli = ArgumentParser(prog=cls.settings.PROG)

        # YChaos CLI version
        ychaos_cli.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"v{__version__} [resilience/vzmi.ychaos]",
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

        # Configuration for the GRU Command Line Interface
        ychaos_cli.add_argument(
            "-c",
            "--config",
            choices=["dev", "prod"],
            default="prod",
            help="Set YChaos CLI configuration (prod)",
        )

        # Arguments for creating HTML & Text Reports
        report_argument_group = ychaos_cli.add_argument_group("reports")
        report_argument_group.add_argument(
            "--text-report",
            type=Path,
            default=None,
            required=False,
            help="Generate a text report from the YChaos execution",
        )
        report_argument_group.add_argument(
            "--html-report",
            type=Path,
            default=None,
            required=False,
            help="Generate a HTML report from YChaos execution",
        )

        ychaos_cli_subparsers = ychaos_cli.add_subparsers(
            action=SubCommandParsersAction,
            dest=cls.settings.COMMAND_IDENTIFIER.format(cls.settings.PROG),
        )

        # Subcommands
        ychaos_cli_subparsers.add_parser(cls=TestPlan, name=TestPlan.name)
        ychaos_cli_subparsers.add_parser(cls=Manual, name=Manual.name)
        ychaos_cli_subparsers.add_parser(cls=AgentCLI, name=AgentCLI.name)
        ychaos_cli_subparsers.add_parser(
            cls=VerificationCommand, name=VerificationCommand.name
        )

        args = ychaos_cli.parse_args(program_arguments)

        if not hasattr(args, "cls"):
            args.cls = YChaosRoot

        args.app = App(args, ychaos_cli)

        # Start the Application
        args.app.start()

        # Call the right method for the subcommand
        try:
            exitcode = args.cls.main(args)
        except YChaosCLIError as e:
            e.handle()
            exitcode = e.exitcode
        except Exception as unknown_error:
            exitcode = 255
            args.app.unknown_error()

        # Teardown
        args.app.teardown(exitcode)

        exit(exitcode)


class App:
    def __init__(self, args: Namespace, cli: Optional[ArgumentParser] = None):
        Settings(args.config)

        args.verbose = min(2, args.verbose)

        self.args = args
        self.console = Console(record=True)
        self.settings: Union[DevSettings, ProdSettings] = Settings.get_instance()

        self.cli = cli

        AppLogger()  # Initializes the AppLogger

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
    def main(cls, args: Namespace) -> Any:  # pragma: no cover
        return 0


# This is where it all started..
def main():
    YChaos.main(sys.argv[1:])
