#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from rich.emoji import Emoji

from ychaos.cli.mock import MockApp
from ychaos.cli.testplan.validate import TestPlanValidatorCommand


class TestTestPlanValidatorCommand(TestCase):

    cls = TestPlanValidatorCommand

    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_validate_valid_testplans_in_directory(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.paths = [
            self.testplans_directory.joinpath("valid/"),
        ]

        # Create a Mocked CLI App
        app = MockApp(args)

        args.app = app
        self.assertEqual(0, args.cls.main(args))

        console_output = app.get_console_output()

        self.assertTrue(
            f"{Emoji.replace(':white_check_mark:')} {self.testplans_directory}/valid/testplan1.json"
            in console_output
        )

    def test_validate_valid_testplans_individual_files(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.paths = [
            self.testplans_directory.joinpath("valid/testplan1.yaml"),
        ]

        # Create a Mocked CLI App
        app = MockApp(args)

        args.app = app
        self.assertEqual(0, args.cls.main(args))

        console_output = app.get_console_output()

        self.assertTrue(
            f"{Emoji.replace(':white_check_mark:')} {self.testplans_directory}/valid/testplan1.yaml"
            in console_output
        )

    def test_validate_invalid_testplan_file(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.paths = [
            self.testplans_directory.joinpath("invalid/testplan1.yaml"),
        ]

        # Create a Mocked CLI App
        app = MockApp(args)

        args.app = app
        self.assertEqual(1, args.cls.main(args))

        console_output = app.get_console_output()

        self.assertTrue(
            f"{Emoji.replace(':exclamation:')} {self.testplans_directory}/invalid/testplan1.yaml"
            in console_output
        )

    def test_validate_empty_directory(self):
        args = Namespace()
        args.cls = self.cls

        with TemporaryDirectory() as empty_directory:
            # Required Arguments for TestPlanValidatorCommand
            args.paths = [Path(empty_directory)]

            # Create a Mocked CLI App
            app = MockApp(args)

            args.app = app
            self.assertEqual(0, args.cls.main(args))

            console_output = app.get_console_output()
            self.assertTrue(
                f"{Emoji.replace(':open_file_folder:')} No Test plans found"
                in console_output
            )

    def test_validate_file_not_found(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.paths = [
            self.testplans_directory.joinpath("valid/unknown_testplan.yaml"),
        ]

        # Create a Mocked CLI App
        app = MockApp(args)

        args.app = app
        self.assertEqual(1, args.cls.main(args))

        console_output = app.get_console_output()

        self.assertTrue(
            f"{Emoji.replace(':mag:')} {self.testplans_directory}/valid/unknown_testplan.yaml not found"
            in console_output
        )

    def get_mock_namespace(self):
        pass
