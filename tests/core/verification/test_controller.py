#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

import yaml
from mockito import unstub, verify, when

from ychaos.core.verification.controller import VerificationController
from ychaos.testplan import SystemState
from ychaos.testplan.schema import TestPlan
from ychaos.testplan.verification import VerificationConfig, VerificationType


class TestVerificationController(TestCase):
    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )
        self.mock_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )

    def test_verification_controller_init(self):
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.STEADY, list()
        )

        self.assertEqual(verification_controller.testplan, self.mock_testplan)
        self.assertEqual(
            len(verification_controller.verification_data),
            len(self.mock_testplan.verification),
        )

    def test_verification_controller_init_raises_error_on_data_size_mismatch(self):
        with self.assertRaises(ValueError):
            VerificationController(
                self.mock_testplan,
                SystemState.STEADY,
                [dict(STEADY=None), dict(CHAOS=None)],
            )

    def test_verification_controller_execute_for_valid_state(self):
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.STEADY, [dict(STEADY=None)]
        )
        verification_controller.testplan.verification[0].config["path"] = __file__
        is_verified = verification_controller.execute()
        self.assertTrue(is_verified)
        self.assertEqual(len(verification_controller.verification_data), 1)
        self.assertIsNotNone(
            verification_controller.verification_data[0].get_data(SystemState.STEADY)
        )

    def test_verification_controller_execute_for_state_not_present_in_verification_config(
        self,
    ):
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.RECOVERED, list()
        )
        verification_controller.testplan.verification[0].config["path"] = __file__
        is_verified = verification_controller.execute()
        self.assertTrue(is_verified)
        self.assertEqual(len(verification_controller.verification_data), 1)
        self.assertFalse(
            verification_controller.verification_data[0].is_data_present(
                SystemState.RECOVERED
            )
        )
        self.assertIsNone(
            verification_controller.verification_data[0].get_data(SystemState.RECOVERED)
        )

    def test_verfication_controller_dump_json_data(self):
        mock_data_file = NamedTemporaryFile("w+")
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.STEADY, list()
        )
        verification_controller.testplan.verification[0].config["path"] = __file__
        is_verified = verification_controller.execute()
        self.assertTrue(is_verified)

        verification_controller.dump_verification(mock_data_file, output_format="json")

        mock_data_file.seek(0)
        verification_data = json.loads(Path(mock_data_file.name).read_text())

        self.assertListEqual(
            verification_data, verification_controller.get_encoded_verification_data()
        )

    def test_verfication_controller_dump_yaml_data(self):
        mock_data_file = NamedTemporaryFile("w+")
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.STEADY, list()
        )
        verification_controller.testplan.verification[0].config["path"] = __file__
        is_verified = verification_controller.execute()
        self.assertTrue(is_verified)

        verification_controller.dump_verification(mock_data_file, output_format="yaml")

        with open(mock_data_file.name) as f:
            verification_data = yaml.safe_load(f)
            self.assertListEqual(
                verification_data,
                verification_controller.get_encoded_verification_data(),
            )

    def test_verification_controller_for_plugin_not_found(self):
        self.mock_testplan.verification[0] = VerificationConfig(
            states=[
                SystemState.STEADY,
            ],
            type=VerificationType.NOOP,
            config=dict(),
        )

        verification_controller = VerificationController(
            self.mock_testplan, SystemState.STEADY, list()
        )

        class MockOnPluginNotFoundHook:
            def __init__(self):
                self.test_var = False

            def __call__(self, *args):
                self.test_var = True

        mock_on_plugin_not_found_hook = MockOnPluginNotFoundHook()
        verification_controller.register_hook(
            "on_plugin_not_found", mock_on_plugin_not_found_hook
        )

        is_verified = verification_controller.execute()
        self.assertTrue(is_verified)

        self.assertTrue(mock_on_plugin_not_found_hook.test_var)

    def test_verification_controller_to_not_sleep_for_delay_before_if_in_different_system_state(
        self,
    ):

        when(time).sleep(0).thenReturn(None)
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.RECOVERED, list()
        )
        verification_controller.execute()
        verify(time, times=1).sleep(0)

    def test_verification_controller_to_sleep_for_delay_before_if_in_right_system_state(
        self,
    ):
        when(time).sleep(0).thenReturn(None)
        verification_controller = VerificationController(
            self.mock_testplan, SystemState.STEADY, list()
        )
        verification_controller.execute()
        verify(time, times=2).sleep(0)

    def tearDown(self) -> None:
        unstub()
