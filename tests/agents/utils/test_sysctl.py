#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from pathlib import Path
from unittest import TestCase

from mockito import patch, unstub

from ychaos.agents.utils.sysctl import SysCtl


class TestSysCtl(TestCase):
    def test_sysctl_get_for_a_valid_key(self):
        valid_mock_var = "var1.subvar1.flag1"

        patch(Path.is_file, lambda: True)
        patch(Path.read_bytes, lambda: b"0")

        val = SysCtl.get(valid_mock_var)
        self.assertEqual(0, int(val))

    def test_sysctl_get_for_an_invalid_key(self):
        invalid_mock_var = "var1.subvar1.invalid_flag1"

        patch(Path.is_file, lambda: False)

        with self.assertRaises(KeyError):
            SysCtl.get(invalid_mock_var)

    def test_sysctl_is_variable_when_raise_error_set_to_false(self):
        invalid_mock_var = "var1.subvar1.invalid_flag1"

        patch(Path.is_file, lambda: False)

        self.assertFalse(SysCtl.is_variable(invalid_mock_var, raise_error=False))

    def tearDown(self) -> None:
        unstub()
