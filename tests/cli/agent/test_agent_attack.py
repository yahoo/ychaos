#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from pathlib import Path
from unittest import TestCase

from vzmi.ychaos.cli.main import YChaos


class TestAgentAttackCLI(TestCase):
    def setUp(self) -> None:
        self.test_plans_path = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )

    def test_agent_cli_build(self):
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(["agent", "--help"])
        self.assertEqual(0, _exit.exception.code)

    def test_valid_test_plan(self):
        cmd = f"ychaos agent attack --testplan {self.test_plans_path}/valid/testplan1.json"
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(cmd.split()[1:])
        self.assertEqual(0, _exit.exception.code)

    def test_invalid_test_plan(self):
        cmd = f"ychaos agent attack --testplan {self.test_plans_path}/invalid/testplan1.yaml"
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(cmd.split()[1:])
        self.assertEqual(1, _exit.exception.code)

    def test_invalid_test_plan_path(self):
        cmd = f"ychaos agent attack --testplan {self.test_plans_path}/invalid/testplan11.yaml"
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(cmd.split()[1:])
        self.assertEqual(1, _exit.exception.code)
