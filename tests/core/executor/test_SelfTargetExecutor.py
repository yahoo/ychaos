#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
from pathlib import Path
from unittest import TestCase

from ychaos.core.exceptions.executor_errors import (
    YChaosTargetConfigConditionFailedError,
)
from ychaos.core.executor.SelfTargetExecutor import SelfTargetExecutor
from ychaos.testplan.schema import TestPlan

from mockito import when, ANY, verify, unstub


class MockHookForTesting:
    def __init__(self):
        self.test_value = False

    def __call__(self, *args, **kwargs):
        self.test_value = True


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
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        executor = SelfTargetExecutor(mock_valid_testplan)

    def test_self_executor_prepare(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        executor = SelfTargetExecutor(mock_valid_testplan)
        executor.prepare()
        self.assertListEqual(
            sorted(executor.ansible_context.inventory.hosts), ["localhost"]
        )
        self.assertEqual(executor.ansible_context.play_source["connection"], "local")
        self.assertTrue(executor.ansible_context.play_source["hosts"] in ["localhost"])

    def test_self_executor_playbook_tasks_sanity(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        executor = SelfTargetExecutor(mock_valid_testplan)
        executor.prepare()

        expected_tasks = [
            dict(
                name="Check current working directory",
                action=dict(module="command", args=dict(cmd="pwd")),
                register="result_pwd",
                changed_when="false",
            ),
            dict(
                name="Create a virtual environment",
                register="result_pip",
                action=dict(
                    module="pip",
                    chdir="{{result_pwd.stdout}}",
                    name="pip",
                    state="latest",
                    virtualenv="ychaos_env",
                    virtualenv_command="python3 -m venv",
                ),
                failed_when=["result_pip.state == 'absent'"],
            ),
            dict(
                name="Install ychaos[agents]",
                register="result_pip_install_ychaos_agents",
                action=dict(
                    module="pip",
                    chdir="{{result_pwd.stdout}}",
                    name="ychaos[agents]",
                    virtualenv="ychaos_env",
                ),
                failed_when=["result_pip_install_ychaos_agents.state == 'absent'"],
            ),
            dict(
                name="Create a workspace directory for storing local report files",
                register="result_create_workspace",
                action=dict(
                    module="file",
                    path="{{result_pwd.stdout}}/ychaos_ws",
                    state="directory",
                    mode="0755",
                ),
            ),
            dict(
                name="Put testplan in ychaos_ws",
                register="result_testplan_file",
                action=dict(
                    module="copy",
                    content=json.dumps(
                        mock_valid_testplan.to_serialized_dict(), indent=4
                    ),
                    dest="{{result_create_workspace.path}}/testplan.json",
                ),
            ),
            dict(
                name="Run YChaos Agent",
                ignore_errors="yes",
                action=dict(
                    module="shell",
                    args=dict(
                        cmd=" ".join(
                            [
                                "ychaos --log-file '{{result_create_workspace.path}}/ychaos.log'",
                                "agent attack --testplan '{{result_testplan_file.dest}}' --attack-report-yaml '{{result_create_workspace.path}}/attack_report.yaml'",
                            ]
                        ),
                    ),
                ),
            ),
            dict(
                name="Delete Virtual environment",
                action=dict(
                    module="file",
                    path="{{result_pip.virtualenv}}",
                    state="absent",
                ),
            ),
        ]
        playbook_tasks = executor.ansible_context.play_source["tasks"]

        self.assertEqual(len(playbook_tasks), len(expected_tasks))
        for i, task in enumerate(playbook_tasks):
            self.assertDictEqual(task, expected_tasks[i])

    def test_self_executor_execute_with_no_errors_running_playbook(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        executor = SelfTargetExecutor(mock_valid_testplan)
        executor.prepare()

        when(executor.ansible_context.tqm).run(ANY).thenReturn(True)
        mock_hook_on_start = MockHookForTesting()
        mock_hook_on_end = MockHookForTesting()
        mock_hook_on_error = MockHookForTesting()

        executor.register_hook("on_start", mock_hook_on_start)
        executor.register_hook("on_end", mock_hook_on_end)
        executor.register_hook("on_error", mock_hook_on_error)

        when(executor).prepare().thenReturn(
            True
        )  # executor.execute() calls prepare again so mocking here
        executor.execute()

        verify(executor.ansible_context.tqm, times=1).run(ANY)
        self.assertTrue(mock_hook_on_start.test_value)
        self.assertTrue(mock_hook_on_end.test_value)
        self.assertFalse(mock_hook_on_error.test_value)

    def test_self_executor_execute_with_an_errors_running_playbook(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan1.yaml")
        )
        executor = SelfTargetExecutor(mock_valid_testplan)

        executor.prepare()
        when(executor.ansible_context.tqm).run(ANY).thenRaise(RuntimeError)
        mock_hook_on_start = MockHookForTesting()
        mock_hook_on_end = MockHookForTesting()
        mock_hook_on_error = MockHookForTesting()

        executor.register_hook("on_start", mock_hook_on_start)
        executor.register_hook("on_end", mock_hook_on_end)
        executor.register_hook("on_error", mock_hook_on_error)

        when(executor).prepare().thenReturn(True)
        executor.execute()

        verify(executor.ansible_context.tqm, times=1).run(ANY)
        self.assertTrue(mock_hook_on_start.test_value)
        self.assertFalse(mock_hook_on_end.test_value)
        self.assertTrue(mock_hook_on_error.test_value)

    def tearDown(self) -> None:
        unstub()
