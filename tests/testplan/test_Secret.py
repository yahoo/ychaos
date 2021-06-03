#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import os
from unittest import TestCase

from mockito import unstub, when

from ychaos.testplan.common import Secret


class TestSecret(TestCase):
    def test_get_secret_value_from_env(self):
        when(os).getenv("MOCK_ENV_VAR").thenReturn("mock_env_var_value")
        secret = Secret(id="MOCK_ENV_VAR")
        self.assertEqual("mock_env_var_value", secret.get_secret_value())

    def test_get_secret_value_from_env_when_env_var_does_not_exist(self):
        secret = Secret(id="MOCK_ENV_VAR")
        self.assertEqual(None, secret.get_secret_value())

    def tearDown(self) -> None:
        unstub()
