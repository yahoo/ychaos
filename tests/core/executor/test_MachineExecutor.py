#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from pathlib import Path
from unittest import TestCase

from mockito import mock, unstub, ANY, when

from vzmi.ychaos.core.exceptions.executor_errors import (
    YChaosTargetConfigConditionFailedError,
)
from vzmi.ychaos.core.executor.MachineTargetExecutor import (
    MachineTargetExecutor,
    YChaosAnsibleResultCallback,
)
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

    def test_machine_executor_prepare(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        executor = MachineTargetExecutor(mock_valid_testplan)
        executor.prepare()

        self.assertListEqual(
            sorted(executor.ansible_context.inventory.hosts),
            ["mockhost01.ychaos.yahoo.com", "mockhost02.ychaos.yahoo.com"],
        )
        self.assertEqual(executor.ansible_context.play_source["connection"], "ssh")
        self.assertEqual(executor.ansible_context.play_source["strategy"], "free")
        self.assertTrue(
            executor.ansible_context.play_source["hosts"]
            in ["mockhost01.ychaos.yahoo.com", "mockhost02.ychaos.yahoo.com"]
        )

    def test_ychaos_ansible_callback(self):
        callback = YChaosAnsibleResultCallback(
            hooks=dict(
                on_target_passed=[lambda: self.assertTrue(True)],
                on_target_failed=[lambda: self.assertTrue(True)],
                on_target_unreachable=[lambda: self.assertTrue(True)],
            )
        )

        mock_host_object = mock(dict(get_name=lambda: "mockhost01.ychaos.yahoo.com"))

        mock_result = mock(dict(_host=mock_host_object))

        callback.v2_runner_on_ok(mock_result)
        self.assertEqual(len(callback.hosts_passed), 1)

        callback.v2_runner_on_failed(mock_result)
        self.assertEqual(len(callback.hosts_failed), 1)

        callback.v2_runner_on_unreachable(mock_result)
        self.assertEqual(len(callback.hosts_unreachable), 1)

    def test_machine_executor_execute(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        executor = MachineTargetExecutor(mock_valid_testplan)

        class MockHookForTargetUnreachable:
            # Always gets called for UT

            def __init__(self):
                self.test_value = False

            def __call__(self, *args, **kwargs):
                # Toggle the test value and assert this method is called
                self.test_value = True

        mock_hook_target_unreachable = MockHookForTargetUnreachable()

        class MockHookForTargetPassed:
            def __init__(self):
                self.test_value = False

            def __call__(self, *args, **kwargs):
                # Should never get called
                assert True is False

        executor.register_hook("on_target_unreachable", mock_hook_target_unreachable)
        executor.register_hook("on_target_passed", MockHookForTargetPassed())

        executor.prepare()
        executor.ansible_context.tqm = mock()
        when(executor.ansible_context.tqm).play(ANY).thenAnswer(
            mock_hook_target_unreachable()
        )

        executor.execute()
        self.assertTrue(mock_hook_target_unreachable.test_value)

    def test_machine_executor_execute_with_no_target_hosts(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        mock_valid_testplan.attack.target_config["blast_radius"] = 0
        executor = MachineTargetExecutor(mock_valid_testplan)

        class MockHookForNoTargetFound:
            # Always gets called for UT

            def __init__(self):
                self.test_value = False

            def __call__(self, *args, **kwargs):
                # Toggle the test value and assert this method is called
                self.test_value = True

        mock_hook_target_unreachable = MockHookForNoTargetFound()

        executor.register_hook("on_no_targets_found", mock_hook_target_unreachable)

        executor.execute()
        self.assertTrue(mock_hook_target_unreachable.test_value)

    def tearDown(self) -> None:
        unstub()
