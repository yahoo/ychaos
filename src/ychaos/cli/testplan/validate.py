#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, List

from pydantic import ValidationError
from rich.panel import Panel

from ...testplan.validator import TestPlanValidator
from .. import YChaosSubCommand

__all__ = ["TestPlanValidatorCommand"]


class TestPlanValidatorCommand(YChaosSubCommand):
    """
    Test plan validator subcommand is used to validate whether the testplan
    files adheres to the YChaos Test plan schema.
    """

    name = "validate"
    help = "Validate YChaos Test plans"

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(
            "paths",
            type=Path,
            nargs="+",
            help="Space separated list of file/directory paths to validate",
            metavar="path",
        )

        return parser

    def __init__(self, **kwargs):
        super(TestPlanValidatorCommand, self).__init__(**kwargs)

        self.paths: List[Path] = kwargs.pop("paths")

    def resolve_validation_paths(self) -> List[Path]:
        file_types = ("json", "yaml", "yml")
        resolved_filepaths: List[Path] = list()
        for input_path in self.paths:
            if input_path.resolve().is_dir():
                for file_type in file_types:
                    resolved_filepaths.extend(
                        list(input_path.glob(f"**/*.{file_type}"))
                    )
            else:
                resolved_filepaths.append(input_path)

        return resolved_filepaths

    def do_testplans_validation(self):
        self.console.log("Getting Test plans")

        resolved_filepaths = self.resolve_validation_paths()

        if len(resolved_filepaths) == 0:
            self.console.line()
            self.console.print(
                ":open_file_folder: No Test plans found", style="orange3"
            )
            return

        self.console.log("Validating Test plans")
        self.console.line()

        for file in sorted(resolved_filepaths):
            try:
                TestPlanValidator.validate_file(file)
                self.console.print(
                    f":white_check_mark: {file}",
                    style="green",
                )

            except ValidationError as validation_error:
                self.set_exitcode(1)

                self.console.print("")
                self.console.print(f":exclamation: {file}", style="bold red")
                self.console.print(
                    Panel.fit(
                        str(validation_error), title="Validation Error", style="red"
                    )
                )
                self.console.print("")

            except FileNotFoundError as file_not_found_error:
                self.set_exitcode(1)
                self.console.print(
                    f":mag: {file} [italic]not found[/italic]",
                    style="indian_red",
                )

    @classmethod
    def main(cls, args: Namespace) -> Any:
        validator = cls(**vars(args))
        validator.do_testplans_validation()

        return validator._exitcode
