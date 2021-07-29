#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from abc import ABC
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional

from ..core.verification.controller import VerificationController
from ..core.verification.data import VerificationStateData
from ..testplan import SystemState
from ..testplan.verification import VerificationConfig, VerificationType
from . import YChaosCLIHook, YChaosTestplanInputSubCommand

__all__ = ["Verify"]


class Verify(YChaosTestplanInputSubCommand):
    """
    The `verify` subcommand of YChaos is used to verify the state of the system. This
    subcommand requires a valid testplan which can be provided with the -t/--testplan argument.
    The subcommand also requires a valid state at which the system is verified.
    """

    name = "verify"
    help = "The verification subcommand of YChaos"

    def __init__(self, **kwargs):
        super(Verify, self).__init__(**kwargs)

        self.test_plan_path: Path = kwargs.pop("testplan")
        self.state: SystemState = SystemState(kwargs.pop("state", None).upper())

        self.dump_yaml: Optional[Path] = kwargs.pop("dump_yaml", None)
        self.dump_json: Optional[Path] = kwargs.pop("dump_json", None)

        self.state_data_path: Optional[Path] = kwargs.pop("state_data", None)

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        parser = super(Verify, cls).build_parser(parser)
        parser.add_argument(
            "-s",
            "--state",
            choices=[x.value.lower() for x in list(SystemState)],
            help="System state to verify",
            default="steady",
            metavar="state",
        )

        report_argument_group = parser.add_argument_group("verification reports")
        report_argument_group.add_argument(
            "--dump-yaml",
            type=Path,
            help="Store the verification data in YAML format",
            required=False,
            metavar="path",
        )

        report_argument_group.add_argument(
            "--dump-json",
            type=Path,
            help="Store the verification data in JSON format",
            required=False,
            metavar="path",
        )

        parser.add_argument(
            "--state-data",
            type=Path,
            help="The path of the verification data state file (JSON/YAML)",
            required=False,
            metavar="path",
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

        # section Hooks
        class VerificationHook(YChaosCLIHook, ABC):
            def __init__(self, app, state: SystemState):
                super(VerificationHook, self).__init__(app)
                self.state = state

        class OnEachPluginStartHook(VerificationHook):
            def __call__(self, index: int, config: VerificationConfig):
                self.console.log(
                    f"Running [i]{self.state.value.lower()}[/i] state verification of type={config.type.value}[{index}]"
                )

        class OnPluginNotFoundHook(VerificationHook):
            def __call__(self, index: int, plugin_type: VerificationType):
                self.console.log(
                    f"The verification plugin type=[i]{plugin_type.value}[/i][{index}] is not available for use."
                )

        class OnEachPluginEndHook(VerificationHook):
            def __call__(
                self,
                index: int,
                config: VerificationConfig,
                verified_state_data: VerificationStateData,
            ):
                self.console.log(
                    (
                        f"Completed [i]{self.state.value.lower()}[/i] state verification of type={config.type.value};"
                        f" verified={verified_state_data.rc==0}"
                    )
                )

        # end section

        verification_controller = VerificationController(
            testplan, self.state, state_data
        )
        verification_controller.register_hook(
            "on_each_plugin_start", OnEachPluginStartHook(self.app, self.state)
        )
        verification_controller.register_hook(
            "on_each_plugin_end", OnEachPluginEndHook(self.app, self.state)
        )
        verification_controller.register_hook(
            "on_plugin_not_found", OnPluginNotFoundHook(self.app, self.state)
        )

        self.console.log(
            f"Starting [i]{self.state.value.lower()}[/i] state verification."
        )
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
        verification_command = Verify(**vars(args))

        verification_command.verify_system_state()

        return verification_command._exitcode
