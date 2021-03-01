#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from argparse import ArgumentParser, Namespace
from io import StringIO
from pathlib import Path
from typing import Any, Optional

from vzmi.ychaos.cli import YChaosSubCommand
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))
(Markdown,) = DependencyUtils.import_from("rich.markdown", ("Markdown",))

__all__ = ["Manual"]


class Manual(YChaosSubCommand):
    """
    Used to print the manual for the entire CLI command.

    ```
    $ ychaos manual -h
    usage: ychaos manual [-h] [-f FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -f FILE, --file FILE  Print YChaos CLI Manual to a file
    ```
    """

    name = "manual"
    help = "Print the manual for YChaos CLI"

    def __init__(self, **kwargs):
        super(Manual, self).__init__()
        assert kwargs.pop("cls") == self.__class__

        self.app = kwargs.pop("app")
        self.console: Console = self.app.console

        self.file: Optional[Path] = kwargs.pop("file", None)

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(
            "-f",
            "--file",
            type=Path,
            help="Print YChaos CLI Manual to a file",
            required=False,
        )

        return parser

    def do_print_manual_entry(self):
        tempfile = StringIO()
        for cmd, msg in self.app.manual_entry().items():
            tempfile.write(f"{'#' * len(cmd.split())} {cmd}")
            tempfile.write("\n")
            tempfile.write("```\n")
            tempfile.write(msg)
            tempfile.write("\n```\n")

        if self.file is not None:
            try:
                self.file.write_text(tempfile.getvalue())
                self.console.log(
                    f"{self.app.settings.PROG} manual entry written to {self.file}"
                )
            except FileNotFoundError as file_not_found_error:
                self.set_exitcode(1)
                self.console.print(
                    f":mag: {self.file} [italic]not found[/italic]",
                    style="indian_red",
                )
            except IsADirectoryError as is_a_directory_error:
                self.set_exitcode(1)
                self.console.print(
                    f":file_folder: The input path ({self.file}) is a directory"
                )
        else:
            self.console.print(Markdown(tempfile.getvalue()))

    @classmethod
    def main(cls, args: Namespace) -> Any:  # pragma: no cover
        manual = Manual(**vars(args))
        manual.do_print_manual_entry()

        return manual._exitcode
