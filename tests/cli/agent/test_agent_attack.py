#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from argparse import Namespace
from pathlib import Path
from unittest import TestCase

from vzmi.ychaos.agents.coordinator import Coordinator
from vzmi.ychaos.cli.agentcli.attack import Attack
from vzmi.ychaos.cli.mock import MockApp


class TestAgentAttackCLI(TestCase):

    cls = Attack

    def setUp(self) -> None:
        self.test_plans_directory = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )
        Coordinator.DEFAULT_DURATION = 1

    def test_valid_test_plan(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("valid/testplan1.json")

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(0, args.cls.main(args))

    def test_invalid_test_plan(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("invalid/testplan1.yaml")

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_invalid_test_plan_path(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("invalid/invalid_path.yaml")

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

    def test_test_plan_path_is_a_directory(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for TestPlanValidatorCommand
        args.testplan = self.test_plans_directory.joinpath("valid/")

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))
