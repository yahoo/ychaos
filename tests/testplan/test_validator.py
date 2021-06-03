#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from os import scandir
from pathlib import Path
from unittest import TestCase

from pydantic import ValidationError

from ychaos.testplan.validator import TestPlanValidator


class TestTestPlanValidator(TestCase):
    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_valid_testplans(self):
        for path in scandir(self.testplans_directory.joinpath("valid")):
            TestPlanValidator.validate_file(path)

    def test_invalid_testplans(self):
        for path in scandir(self.testplans_directory.joinpath("invalid")):
            with self.assertRaises(ValidationError):
                TestPlanValidator.validate_file(path)
