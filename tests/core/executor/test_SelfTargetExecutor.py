#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from pathlib import Path
from unittest import TestCase

from vzmi.ychaos.core.exceptions.executor_errors import (
    YChaosTargetConfigConditionFailedError,
)
from vzmi.ychaos.core.executor.SelfTargetExecutor import SelfTargetExecutor
from vzmi.ychaos.testplan.schema import TestPlan


class TestSelfTargetExecutor(TestCase):
    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_self_target_executor_init_raises_error_when_target_type_is_not_self(self):
        mock_invalid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        with self.assertRaises(YChaosTargetConfigConditionFailedError):
            SelfTargetExecutor(mock_invalid_testplan)

    def test_self_target_executor_execute_with_valid_testplan(self):
        mock_invalid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        executor = SelfTargetExecutor(mock_invalid_testplan)
        with self.assertRaises(NotImplementedError):
            executor.execute()
