#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
import random
from types import SimpleNamespace
from pathlib import Path
from ...app_logger import AppLogger
from ...agents.index import AgentType
from ...testplan.attack import MachineTargetDefinition
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


class MachineTargetExecutor(BaseExecutor):
    """
    The executor that executes the agent on a set of Virtual machines/Bare metals
    by connecting to the hosts via SSH. The input for the executor is the testplan,
    within which, the target_type is defined as `machine`. The target_config will
    provide the list of hosts out of which random `blast_radius`% of the hosts
    is selected for attack.

    The following are the valid hooks to this executor

    ## Valid Hooks

    === "on_start"
        Called when starting to run the Ansible playbook.

        ```python
            def callable_hook(): ...
        ```

    === "on_no_targets_found"
        Called when no targets are found to attack. Either blast radius is
        too low or there are no hosts in the attack list.

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

    __target_type__ = "machine"

    # __taskresult_callable__ = EventHook.Callable(TaskResult)

    __hook_events__ = {
        "on_no_targets_found": EventHook.CallableType(),
        "on_start": EventHook.CallableType(),
        "on_target_unreachable": EventHook.CallableType(TaskResult),
        "on_target_failed": EventHook.CallableType(TaskResult),
        "on_target_passed": EventHook.CallableType(TaskResult),
        "on_error": EventHook.CallableType(Exception),
        "on_end": EventHook.CallableType(TaskResult),
    }

    def __init__(self, testplan: TestPlan, *args, **kwargs):
        super(MachineTargetExecutor, self).__init__(testplan)

        # Selects a `blast_radius`% of hosts at random from the
        # effective hosts and uses it as the target hosts for the attack
        self._compute_target_hosts()

        self.ansible_context = SimpleNamespace()

        self.logger = AppLogger.get_logger(self.__class__.__name__)

    def _compute_target_hosts(self):
        target_defn: MachineTargetDefinition = self.testplan.attack.get_target_config()
        effective_hosts = target_defn.get_effective_hosts()
        self.target_hosts = random.sample(
            effective_hosts, target_defn.blast_radius * len(effective_hosts) // 100
        )

    def prepare(self):
        self.ansible_context.loader = DataLoader()
        self.ansible_context.results_callback = YChaosAnsibleResultCallback(
            hooks={
                k: v
                for k, v in self.hooks.items()
                if k in YChaosAnsibleResultCallback.__hook_events__
            }
        )

        # Hosts to be in comma separated string
        hosts = ",".join(self.testplan.attack.get_target_config().get_effective_hosts())
        if len(self.testplan.attack.get_target_config().get_effective_hosts()) == 1:
            hosts += ","
        self.ansible_context.inventory = InventoryManager(
            loader=self.ansible_context.loader, sources=hosts
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
            name="YChaos Ansible Play",
            hosts=",".join(self.target_hosts),
            remote_user=self.testplan.attack.get_target_config().ssh_config.user,
            connection="ssh",
            strategy="free",
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
                    name="Check if python3 installed",
                    action=dict(module="command", args=dict(cmd="which python3")),
                    register="result_which_python3",
                    changed_when="false",
                    failed_when=[
                        # Fail if python3 not installed on the target
                        "result_which_python3.rc != 0"
                    ],
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
                    failed_when=[
                        # Failed in these following reasons
                        # 1. pip not installed
                        # 2. Failed to installed latest pip version
                        "result_pip.state == 'absent'"
                    ],
                    vars=dict(
                        ansible_python_interpreter="{{result_which_python3.stdout}}"
                    ),
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
                    vars=dict(
                        ansible_python_interpreter="{{result_which_python3.stdout}}"
                    ),
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
                *self.get_file_transfer_tasks(),
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
                            ]
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
                            self.testplan.attack.get_target_config().report_dir.resolve()
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
            ],
        )

    def get_file_transfer_tasks(self):
        task_list = list()
        testplan = self.testplan.copy()
        for i, agent in enumerate(self.testplan.attack.agents):
            if agent.type == AgentType.CONTRIB:
                filename = Path(testplan.attack.agents[i].config["path"])
                task = dict(
                    name=f"Copy {filename.name} to remote",
                    register="copy_contrib_agent_" + filename.stem,
                    action=dict(
                        module="copy",
                        src=str(filename.absolute()),
                        dest="{{result_create_workspace.path}}/" + filename.name,
                    ),
                )
                task_list.append(task)
                testplan.attack.agents[i].config["path"] = "./ychaos_ws/{}".format(
                    filename.name
                )

        # testplan will not have any changes from original if there are no contrib agents present
        testplan_task = [
            dict(
                name="Copy testplan from local to remote",
                register="result_testplan_file",
                action=dict(
                    module="copy",
                    content=json.dumps(testplan.to_serialized_dict(), indent=4),
                    dest="{{result_create_workspace.path}}/testplan.json",
                ),
            )
        ]

        return testplan_task + task_list

    def execute(self) -> None:
        self.prepare()

        if len(self.target_hosts) == 0:
            self.execute_hooks("on_no_targets_found")
            return

        play = Play().load(
            self.ansible_context.play_source,
            variable_manager=self.ansible_context.variable_manager,
            loader=self.ansible_context.loader,
        )

        # Create Report Directory
        import os

        os.makedirs(
            self.testplan.attack.get_target_config().report_dir.resolve(), exist_ok=True
        )

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
