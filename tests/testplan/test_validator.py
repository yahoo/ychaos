from os import scandir
from os.path import dirname
from unittest import TestCase

from parameterized import parameterized
from pydantic import ValidationError

from vzmi.ychaos.testplan.validator import TestPlanValidator


class TestTestPlanValidator(TestCase):
    @parameterized.expand(
        [(x.path,) for x in scandir(dirname(__file__) + "/resources/testplans/valid")]
    )
    def test_valid_testplans(self, path):
        TestPlanValidator.validate_file(path)

    @parameterized.expand(
        [(x.path,) for x in scandir(dirname(__file__) + "/resources/testplans/invalid")]
    )
    def test_valid_testplans(self, path):
        with self.assertRaises(ValidationError):
            TestPlanValidator.validate_file(path)
