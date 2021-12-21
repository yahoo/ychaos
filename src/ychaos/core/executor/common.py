#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from typing import Any

from ...utils.dependency import DependencyUtils
from ...utils.hooks import EventHook

CallbackBase: Any  # For mypy

(CallbackBase,) = DependencyUtils.import_from(
    "ansible.plugins.callback", ("CallbackBase",), raise_error=False, warn=False
)
(TaskResult,) = DependencyUtils.import_from(
    "ansible.executor.task_result", ("TaskResult",), raise_error=False, warn=False
)

if CallbackBase:  # pragma: no cover

    class YChaosAnsibleResultCallback(CallbackBase, EventHook):
        """
        This is a callback plugin which help performing actions as results from running the ansible playbook comes in.
        """

        __hook_events__ = dict.fromkeys(
            (
                "on_target_unreachable",
                "on_target_failed",
                "on_target_passed",
            ),
            EventHook.CallableType(TaskResult),
        )

        def __init__(self, *args, **kwargs):
            super(YChaosAnsibleResultCallback, self).__init__()

            EventHook.__init__(self)
            self.hooks.update(kwargs.pop("hooks", dict()))

            self.hosts_passed = dict()
            self.hosts_unreachable = dict()
            self.hosts_failed = dict()

        def v2_runner_on_unreachable(self, result):
            self.hosts_unreachable[result._host.get_name()] = result
            self.execute_hooks("on_target_unreachable", result)

        def v2_runner_on_ok(self, result):
            self.hosts_passed[result._host.get_name()] = result
            self.execute_hooks("on_target_passed", result)

        def v2_runner_on_failed(self, result, ignore_errors=False):
            self.hosts_failed[result._host.get_name()] = result
            self.execute_hooks("on_target_failed", result)
