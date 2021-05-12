#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from argparse import Namespace
from pathlib import Path
from unittest import TestCase

from ychaos.cli.exceptions import YChaosCLIError
from ychaos.cli.mock import MockApp
from ychaos.cli.testplan.validate import TestPlanValidatorCommand


class MockYChaosCLIError(YChaosCLIError):
    def handle(self) -> None:
        assert True is True


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

        error = YChaosCLIError(app=MockApp(args), message="Some Error occured")
        self.assertEqual(error.exitcode, 1)
        error.handle()
