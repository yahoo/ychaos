import sys
from argparse import ArgumentParser, Namespace
from typing import Iterable, List, Union

from rich.console import Console
from rich.table import Table

from vzmi.ychaos import __version__
from vzmi.ychaos.cli.exceptions import YChaosCLIError
from vzmi.ychaos.cli.testplan import TestPlan
from vzmi.ychaos.settings import DevSettings, ProdSettings, Settings
from vzmi.ychaos.utils.argparse import SubCommandParsersAction


class YChaos:
    """
    The YChaos CLI class. The `main` method of this class is the starting point of
    the CLI which takes in the program arguments.

    ```
    $ ychaos -h
    usage: ychaos [-h] [-v] [-V] [-c {dev,prod}] {testplan} ...

    positional arguments:
      {testplan}
        testplan            sub command for test plan operations

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -V, --verbose         Increase verbosity of logs (INFO)
      -c {dev,prod}, --config {dev,prod}
                            Set YChaos CLI configuration (prod)
    ```
    """

    @classmethod
    def main(cls, program_arguments: list):
        ychaos_cli = ArgumentParser(prog=Settings.get_instance().PROG)

        # YChaos CLI version
        ychaos_cli.add_argument(
            "-v",
            "--version",
            action="version",
            version="v{version} [ssharma06/vzmi.ychaos]".format(version=__version__),
        )

        ychaos_cli.add_argument(
            "-V",
            "--verbose",
            action="count",
            help="Increase verbosity of logs (INFO)",
            default=0,
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

        ychaos_cli_subparsers = ychaos_cli.add_subparsers(
            action=SubCommandParsersAction,
            dest="_cmd.{}".format(Settings.get_instance().PROG),
        )

        # Subcommands
        ychaos_cli_subparsers.add_parser(cls=TestPlan, name=TestPlan.name)

        args = ychaos_cli.parse_args(program_arguments)

        args.app = App(args)

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
    def __init__(self, args: Namespace):
        Settings(args.config)

        args.verbose = min(2, args.verbose)

        self.args = args
        self.console: Console = Console(record=True)
        self.settings: Union[DevSettings, ProdSettings] = Settings.get_instance()

    def start(self) -> None:
        self.console.clear()
        self.console.rule(
            title=self.settings.APP_DESC,
            style="magenta",
        )

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
        branch = _args.get("_cmd.{}".format(parent), None)

        tree = []
        while branch is not None:
            tree.append(parent)
            parent = branch
            branch = _args.get("_cmd.{}".format(parent), None)

        tree.append(parent)
        return tree

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
        self.console.line()
        self.console.log("Exiting with exitcode={}".format(exitcode))
        self.console.rule(
            title=":sunny:",
            style="magenta",
        )


# This is where it all started..
def main():
    YChaos.main(sys.argv[1:])
