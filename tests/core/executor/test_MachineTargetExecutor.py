#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
import yaml
from pathlib import Path
from unittest import TestCase

from mockito import ANY, mock, unstub, when

from ychaos.core.exceptions.executor_errors import (
    YChaosTargetConfigConditionFailedError,
)
from ychaos.core.executor.MachineTargetExecutor import (
    MachineTargetExecutor,
    YChaosAnsibleResultCallback,
)
from ychaos.testplan.schema import TestPlan


class TestMachineTargetExecutor(TestCase):
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

    def test_machine_executor_playbook_tasks_sanity(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        executor = MachineTargetExecutor(mock_valid_testplan)
        executor.prepare()

        expected_tasks = [
            dict(
                name="Check current working directory",
                action=dict(module="command", args=dict(cmd="pwd")),
                register="result_pwd",
                changed_when="false",
            ),
            dict(
                name="Check if python3 installed",
                action=dict(module="command", args=dict(cmd="which python3")),
                register="result_which_python3",
                changed_when="false",
                failed_when=["result_which_python3.rc != 0"],
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
                    virtualenv_command="{{result_which_python3.stdout}} -m venv",
                ),
                failed_when=["result_pip.state == 'absent'"],
                vars=dict(ansible_python_interpreter="{{result_which_python3.stdout}}"),
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
                vars=dict(ansible_python_interpreter="{{result_which_python3.stdout}}"),
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
                name="Copy testplan from local to remote",
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
                    cmd=" ".join(
                        [
                            "source {{result_pip.virtualenv}}/bin/activate",
                            "&&",
                            "ychaos --log-file {{result_create_workspace.path}}/ychaos.log",
                            "agent attack --testplan {{result_testplan_file.dest}} --attack-report-yaml {{result_create_workspace.path}}/attack_report.yaml",
                        ],
                    ),
                ),
            ),
            dict(
                name="Zip workspace directory",
                action=dict(
                    module="community.general.archive",
                    path="{{result_create_workspace.path}}",
                    dest="{{result_create_workspace.path}}/ychaos.zip",
                    format="zip",
                ),
            ),
            dict(
                name="Copy Workspace directory to local",
                action=dict(
                    module="fetch",
                    src="{{result_create_workspace.path}}/ychaos.zip",
                    dest=str(
                        mock_valid_testplan.attack.get_target_config().report_dir.resolve()
                    )
                    + "/ychaos_{{inventory_hostname}}.zip",
                ),
            ),
            dict(
                name="Delete YChaos Workspace on host",
                action=dict(
                    module="file",
                    path="{{result_create_workspace.path}}",
                    state="absent",
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

    def test_machine_executor_prepare_with_single_host(self):
        mock_valid_testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan5.yaml")
        )
        executor = MachineTargetExecutor(mock_valid_testplan)
        executor.prepare()

        self.assertListEqual(
            sorted(executor.ansible_context.inventory.hosts),
            [
                "mockhost01.ychaos.yahoo.com",
            ],
        )
        self.assertEqual(executor.ansible_context.play_source["connection"], "ssh")
        self.assertEqual(executor.ansible_context.play_source["strategy"], "free")
        self.assertTrue(
            executor.ansible_context.play_source["hosts"]
            in [
                "mockhost01.ychaos.yahoo.com",
            ]
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

    def test_machine_executor_with_valid_contrib_agent_testplan(self):

        with open(
            Path(__file__)
            .joinpath("../../../resources/contribAgent/contribAgentTestplan.yaml")
            .resolve()
        ) as f:
            tp = yaml.safe_load(f)
        tp["attack"]["agents"][0]["config"]["path"] = Path(
            "../../resources/contribAgent/dummy_agent.py"
        ).absolute()
        mock_valid_testplan = TestPlan(**tp)
        executor = MachineTargetExecutor(mock_valid_testplan)

    def test_machine_executor_when_agent_type_is_contrib(self):
        with open(
            Path(__file__)
            .joinpath("../../../resources/contribAgent/contribAgentTestplan.yaml")
            .resolve()
        ) as f:
            tp = yaml.safe_load(f)
        tp["attack"]["agents"][0]["config"]["path"] = Path(
            "../../resources/contribAgent/dummy_agent.py"
        ).absolute()
        mock_valid_testplan = TestPlan(**tp)
        executor = MachineTargetExecutor(mock_valid_testplan)
        executor.prepare()
        playbook_tasks = list(
            map(lambda x: x["name"], executor.ansible_context.play_source["tasks"])
        )
        self.assertNotIn("Copy testplan from local to remote", playbook_tasks)
        self.assertIn("Copy new testplan to remote", playbook_tasks)
        self.assertIn("Copy dummy_agent.py to remote", playbook_tasks)

    def tearDown(self) -> None:
        unstub()
