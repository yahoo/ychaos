#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import json
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from vzmi.ychaos.cli.mock import MockApp
from vzmi.ychaos.cli.verification import Verification
from vzmi.ychaos.testplan.schema import TestPlan


class TestVerificationCommand(TestCase):

    cls = Verification

    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_verification_for_valid_test_plan_with_invalid_plugin_path(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for VerificationCommand
        args.testplan = self.testplans_directory.joinpath("valid/testplan1.json")
        args.state = "steady"

        temp_state_data_file_json = NamedTemporaryFile("w+")
        args.dump_json = temp_state_data_file_json.name

        temp_state_data_file_yaml = NamedTemporaryFile("w+")
        args.dump_yaml = temp_state_data_file_yaml.name

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

        temp_state_data_file_json.seek(0)
        state_data = json.loads(Path(args.dump_json).read_text())
        self.assertIsNotNone(state_data[0]["STEADY"])
        self.assertIsNone(state_data[0]["CHAOS"])

        self.assertTrue(
            "The system is not verified to be in steady state"
            in app.get_console_output()
        )

    def test_verification_for_invalid_test_plan(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for VerificationCommand
        args.testplan = self.testplans_directory.joinpath("invalid/testplan1.json")
        args.state = "steady"

        temp_state_data_file = NamedTemporaryFile("w+")
        args.dump_json = temp_state_data_file.name

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_verification_for_testplan_with_valid_plugin_path(self):
        temp_testplan_file = NamedTemporaryFile("w+")

        args = Namespace()
        args.cls = self.cls

        # Required Arguments for VerificationCommand
        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        testplan.verification[0].config["path"] = __file__
        testplan.export_to_file(temp_testplan_file.name)

        args.testplan = temp_testplan_file.name
        args.state = "steady"

        temp_state_data_file_json = NamedTemporaryFile("w+")
        args.dump_json = temp_state_data_file_json.name

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(0, args.cls.main(args))

        temp_state_data_file_json.seek(0)
        state_data = json.loads(Path(args.dump_json).read_text())
        self.assertIsNotNone(state_data[0]["STEADY"])
        self.assertIsNone(state_data[0]["CHAOS"])

        self.assertTrue(
            "The system is verified to be in steady state" in app.get_console_output()
        )

    def test_verification_for_testplan_with_valid_plugin_path_with_invalid_state_data_path_directory(
        self,
    ):
        temp_testplan_file = NamedTemporaryFile("w+")

        args = Namespace()
        args.cls = self.cls

        # Required Arguments for VerificationCommand
        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        testplan.verification[0].config["path"] = __file__
        testplan.export_to_file(temp_testplan_file.name)

        args.testplan = temp_testplan_file.name
        args.state = "steady"
        args.state_data = self.testplans_directory

        temp_state_data_file_json = NamedTemporaryFile("w+")
        args.dump_json = temp_state_data_file_json.name

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_verification_for_testplan_with_valid_plugin_path_with_invalid_state_data_path_not_found(
        self,
    ):
        temp_testplan_file = NamedTemporaryFile("w+")

        args = Namespace()
        args.cls = self.cls

        # Required Arguments for VerificationCommand
        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        testplan.verification[0].config["path"] = __file__
        testplan.export_to_file(temp_testplan_file.name)

        args.testplan = temp_testplan_file.name
        args.state = "steady"
        args.state_data = self.testplans_directory.joinpath(
            "invalid_path_state_data.json"
        )

        temp_state_data_file_json = NamedTemporaryFile("w+")
        args.dump_json = temp_state_data_file_json.name

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_verification_for_valid_test_plan_with_invalid_plugin_path_when_not_strict(
        self,
    ):
        args = Namespace()
        args.cls = self.cls

        temp_testplan_file = NamedTemporaryFile("w+")
        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        testplan.verification[0].strict = False
        testplan.export_to_file(temp_testplan_file.name)

        # Required Arguments for VerificationCommand
        args.testplan = temp_testplan_file.name
        args.state = "steady"

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(0, args.cls.main(args))

        self.assertTrue(
            "The system is verified to be in steady state" in app.get_console_output()
        )
