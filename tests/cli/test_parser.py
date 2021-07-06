#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from argparse import Namespace
from typing import Any
from unittest import TestCase

from ychaos.cli import YChaosArgumentParser, YChaosCLIError
from ychaos.utils.argparse import SubCommand


class MockYChaosCLIError(YChaosCLIError):

    exitcode = 2

    def handle(self) -> None:
        assert True is not False


class MockSubCommand(SubCommand):

    __err__ = {
        0: None,
        1: MockYChaosCLIError(app=None, message="CLI Error occurred"),
        2: Exception("Unknown error"),
    }

    @classmethod
    def main(cls, args: Namespace) -> Any:
        if args.err != 0:
            raise cls.__err__[args.err]


class TestYChaosArgumentParser(TestCase):
    def test_ychaos_argument_parser_handle_cli_error(self):
        ychaos_arg_parser = YChaosArgumentParser()
        exitcode = ychaos_arg_parser.run_command(Namespace(err=1, cls=MockSubCommand))
        self.assertEqual(exitcode, 2)
