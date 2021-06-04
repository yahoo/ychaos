#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import tempfile
from argparse import Namespace
from pathlib import Path
from unittest import TestCase

from ychaos.agents.coordinator import Coordinator
from ychaos.cli.agent.attack import Attack
from ychaos.cli.mock import MockApp


class TestAgentAttackCLI(TestCase):

    cls = Attack

    def setUp(self) -> None:
        self.test_plans_directory = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )
        Coordinator.DEFAULT_DURATION = 1
        self.attack_report_yaml_path: Path = Path(
            tempfile.NamedTemporaryFile("w+", delete=False).name
        )

    def test_valid_test_plan(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("valid/testplan1.json")
        args.attack_report_yaml = self.attack_report_yaml_path

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app
        args.cls.main(args)
        self.assertEqual(0, args.cls.main(args))
        self.assertTrue(Path.is_file(self.attack_report_yaml_path))

    def test_no_attack_report_path(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("valid/testplan1.json")
        args.attack_report_yaml = None

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(0, args.cls.main(args))

    def test_invalid_attack_report_path(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("valid/testplan1.json")
        args.attack_report_yaml = Path(".")

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(0, args.cls.main(args))
        self.assertTrue("is not a valid file path" in app.get_console_output())

    def test_invalid_test_plan(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("invalid/testplan1.yaml")
        args.attack_report_yaml = self.attack_report_yaml_path

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_invalid_test_plan_path(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("invalid/invalid_path.yaml")
        args.attack_report_yaml = self.attack_report_yaml_path

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_test_plan_path_is_a_directory(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("valid/")
        args.attack_report_yaml = self.attack_report_yaml_path

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))
