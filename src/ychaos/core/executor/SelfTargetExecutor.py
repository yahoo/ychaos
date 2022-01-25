#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
from types import SimpleNamespace

from ...app_logger import AppLogger
from ...testplan.attack import SelfTargetDefinition
from ...testplan.schema import TestPlan
from ...utils.dependency import DependencyUtils
from ...utils.hooks import EventHook
from .BaseExecutor import BaseExecutor

(YChaosAnsibleResultCallback,) = DependencyUtils.import_from(
    "ychaos.core.executor.common",
    ("YChaosAnsibleResultCallback",),
    raise_error=False,
    warn=False,
)

(TaskQueueManager,) = DependencyUtils.import_from(
    "ansible.executor.task_queue_manager",
    ("TaskQueueManager",),
    raise_error=False,
    warn=False,
)
(InventoryManager,) = DependencyUtils.import_from(
    "ansible.inventory.manager", ("InventoryManager",), raise_error=False, warn=False
)
(DataLoader,) = DependencyUtils.import_from(
    "ansible.parsing.dataloader", ("DataLoader",), raise_error=False, warn=False
)
(Play,) = DependencyUtils.import_from(
    "ansible.playbook.play", ("Play",), raise_error=False, warn=False
)

(VariableManager,) = DependencyUtils.import_from(
    "ansible.vars.manager", ("VariableManager",), raise_error=False, warn=False
)

(TaskResult,) = DependencyUtils.import_from(
    "ansible.executor.task_result", ("TaskResult",), raise_error=False, warn=False
)


class SelfTargetExecutor(BaseExecutor):
    """
    The executor that executes the agent on localhost. The input for the executor is the testplan,
    within which, the target_type is defined as `self`.

    The following are the valid hooks to this executor

    ## Valid Hooks

    === "on_start"
        Called when starting to run the Ansible playbook.

        ```python
            def callable_hook(): ...
        ```

    === "on_target_unreachable"
        Called when a target becomes unreachable during the Ansible play

        ```python
            def callable_hook(result: AnsibleResult): ...
        ```

    === "on_target_passed"
        Called when an ansible task is passed

        ```python
            def callable_hook(result: AnsibleResult): ...
        ```

    === "on_target_failed"
        Called when an ansible task is failed

        ```python
            def callable_hook(result: AnsibleResult): ...
        ```

    === "on_end"
        Called after the end of Ansible playbook run

        ```python
            def callable_hook(result): ...
        ```

    === "on_error"
        Called when an exception is raised

        ```python
            def callable_hook(e: Exception): ...
        ```
    """

    __target_type__ = "self"

    __hook_events__ = {
        "on_start": EventHook.CallableType(),
        "on_target_unreachable": EventHook.CallableType(TaskResult),
        "on_target_failed": EventHook.CallableType(TaskResult),
        "on_target_passed": EventHook.CallableType(TaskResult),
        "on_error": EventHook.CallableType(Exception),
        "on_end": EventHook.CallableType(TaskResult),
    }

    LOCALHOST: str = "localhost"

    def __init__(self, testplan: TestPlan, *args, **kwargs):
        super(SelfTargetExecutor, self).__init__(testplan)
        self.ansible_context = SimpleNamespace()
        self.logger = AppLogger.get_logger(self.__class__.__name__)

    def prepare(self):
        self.ansible_context.loader = DataLoader()

        self.ansible_context.results_callback = YChaosAnsibleResultCallback(
            hooks={
                k: v
                for k, v in self.hooks.items()
                if k in YChaosAnsibleResultCallback.__hook_events__
            }
        )

        self.ansible_context.inventory = InventoryManager(
            loader=self.ansible_context.loader, sources=f"{self.LOCALHOST},"
        )

        self.ansible_context.variable_manager = VariableManager(
            loader=self.ansible_context.loader, inventory=self.ansible_context.inventory
        )

        self.ansible_context.tqm = TaskQueueManager(
            inventory=self.ansible_context.inventory,
            variable_manager=self.ansible_context.variable_manager,
            loader=self.ansible_context.loader,
            passwords=dict(vault_pass=None),
            stdout_callback=self.ansible_context.results_callback,
        )

        self.ansible_context.play_source = dict(
            name="Ychaos Ansible Play",
            hosts=self.LOCALHOST,
            connection="local",
            gather_facts="no",
            ignore_unreachable="no",
            tasks=[
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
                    failed_when=[
                        # Failed in these following reasons
                        # 1. pip not installed
                        # 2. Failed to installed latest pip version
                        "result_pip.state == 'absent'"
                    ],
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
                    failed_when=[
                        # Failed if unable to install ychaos[agents]
                        "result_pip_install_ychaos_agents.state == 'absent'"
                    ],
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
                            self.testplan.to_serialized_dict(), indent=4
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
            ],
        )

    def execute(self) -> None:

        self.prepare()
        play = Play().load(
            data=self.ansible_context.play_source,
            variable_manager=self.ansible_context.variable_manager,
            loader=self.ansible_context.loader,
        )

        import os

        target_config: SelfTargetDefinition = self.testplan.attack.get_target_config()
        os.makedirs(target_config.report_dir.resolve(), exist_ok=True)

        try:
            self.execute_hooks("on_start")
            result = self.ansible_context.tqm.run(play)
            self.execute_hooks("on_end", result)
        except Exception as e:
            self.execute_hooks("on_error", e)
        finally:
            self.ansible_context.tqm.cleanup()
            if self.ansible_context.loader:  # pragma: no cover
                self.ansible_context.loader.cleanup_all_tmp_files()
