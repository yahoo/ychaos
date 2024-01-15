#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from argparse import Namespace
from pathlib import Path
from unittest import TestCase

from mockito import mock, unstub, verify, when
from rich.console import Console

from ychaos.cli.exceptions import YChaosCLIError
from ychaos.cli.mock import MockApp
from ychaos.cli.testplan.validate import TestPlanValidatorCommand


class TestYChaosCLIError(TestCase):
    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_exception_init(self):
        args = Namespace(debug=False)
        args.cls = TestPlanValidatorCommand

        # Required Arguments for TestPlanValidatorCommand
        args.paths = [
            self.testplans_directory.joinpath("valid/"),
        ]

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        error = YChaosCLIError(app=MockApp(args), message="Some Error occurred")
        self.assertEqual(error.exitcode, 1)
        error.handle()

    def test_exception_init_with_debug_mode(self):
        args = Namespace(debug=True)
        args.cls = TestPlanValidatorCommand

        # Required Arguments for TestPlanValidatorCommand
        args.paths = [
            self.testplans_directory.joinpath("valid/"),
        ]

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        try:
            # Populate exc_info for traceback
            raise Exception("Unknown Error")
        except:
            error = YChaosCLIError(app=MockApp(args), message="Some Error occurred")
            error.app.console = mock(spec=Console)
            when(error.app.console).print_exception(extra_lines=2).thenReturn(None)
            error.handle()
            verify(error.app.console, times=1).print_exception(extra_lines=2)

    def tearDown(self) -> None:
        unstub()
