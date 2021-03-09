#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional

from vzmi.ychaos.cli import YChaosTestplanInputSubCommand
from vzmi.ychaos.core.verification.controller import VerificationController
from vzmi.ychaos.testplan import SystemState
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))
(Markdown,) = DependencyUtils.import_from("rich.markdown", ("Markdown",))

__all__ = ["VerificationCommand"]


class VerificationCommand(YChaosTestplanInputSubCommand):

    name = "verify"
    help = "The verification subcommand of YChaos"

    def __init__(self, **kwargs):
        super(VerificationCommand, self).__init__()
        assert kwargs.pop("cls") == self.__class__

        self.app = kwargs.pop("app")
        self.console: Console = self.app.console

        self.test_plan_path: Path = kwargs.pop("testplan")
        self.state: SystemState = SystemState(kwargs.pop("state", None).upper())

        self.dump_yaml: Optional[Path] = kwargs.pop("dump_yaml", None)
        self.dump_json: Optional[Path] = kwargs.pop("dump_json", None)

        self.state_data_path: Optional[Path] = kwargs.pop("state_data", None)

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        parser = super(VerificationCommand, cls).build_parser(parser)
        parser.add_argument(
            "-s",
            "--state",
            choices=[x.value.lower() for x in list(SystemState)],
            help="System state to verify",
            required=True,
        )

        parser.add_argument(
            "--dump-yaml",
            type=Path,
            help="Store the verification data in YAML format",
            required=False,
        )

        parser.add_argument(
            "--dump-json",
            type=Path,
            help="Store the verification data in JSON format",
            required=False,
        )

        parser.add_argument(
            "--state-data",
            type=Path,
            help="The path of the verification data state file (JSON/YAML)",
            required=False,
        )

        return parser

    def get_state_data(self):
        self.console.log("Getting state data")
        self.console.line()
        try:
            import yaml

            path = Path(self.state_data_path)
            with open(path, "r") as file:
                state_data = yaml.safe_load(file)
            return state_data
        except IsADirectoryError as is_directory:
            self.set_exitcode(1)
            self.console.print(
                ":file_folder: The input path ({path}) is not a valid state data file".format(
                    path=self.state_data_path
                )
            )
        except FileNotFoundError as file_not_found_error:
            self.set_exitcode(1)
            self.console.print(
                ":mag: {file} [italic]not found[/italic]".format(
                    file=str(self.state_data_path)
                ),
                style="indian_red",
            )
        return None

    def verify_system_state(self):
        testplan = self.get_validated_test_plan(self.test_plan_path)

        if self._exitcode != 0:
            return

        state_data = list()
        if self.state_data_path:
            state_data = self.get_state_data()
            if self._exitcode != 0:
                return

        verification_controller = VerificationController(
            testplan, self.state, state_data
        )

        self.console.log(f"Running {self.state.value.lower()} state verification")
        is_verified = verification_controller.execute()

        self.set_exitcode(int(not is_verified))

        self.console.line()
        if is_verified:
            self.console.print(
                f"The system is verified to be in {self.state.value.lower()} state",
                style="green",
            )
        else:
            self.console.print(
                f"The system is not verified to be in {self.state.value.lower()} state",
                style="red",
            )

        self.console.line()
        if self.dump_json:
            self.console.log(
                f"Dumping {self.state.value.lower()} state verification data to {self.dump_json}"
            )
            with open(self.dump_json, "w") as fp:
                verification_controller.dump_verification_json(fp)

        if self.dump_yaml:
            self.console.log(
                f"Dumping {self.state.value.lower()} state verification data to {self.dump_yaml}"
            )
            with open(self.dump_yaml, "w") as fp:
                verification_controller.dump_verification_yaml(fp)

    @classmethod
    def main(cls, args: Namespace) -> Any:  # pragma: no cover
        verification_command = VerificationCommand(**vars(args))

        verification_command.verify_system_state()

        return verification_command._exitcode
