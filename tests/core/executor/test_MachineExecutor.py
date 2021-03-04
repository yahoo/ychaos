#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from pathlib import Path
from unittest import TestCase

from vzmi.ychaos.core.exceptions.executor_errors import (
    YChaosTargetConfigConditionFailedError,
)
from vzmi.ychaos.core.executor.MachineTargetExecutor import MachineTargetExecutor
from vzmi.ychaos.testplan.attack import AttackConfig, TargetType
from vzmi.ychaos.testplan.schema import TestPlan


class TestMachineExecutor(TestCase):
    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_machine_executor_init_raises_error_when_target_type_is_not_machine(self):
        mock_invalid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        with self.assertRaises(YChaosTargetConfigConditionFailedError):
            MachineTargetExecutor(mock_invalid_testplan)

    def test_machine_executor_init_with_valid_testplan(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        executor = MachineTargetExecutor(mock_valid_testplan)
