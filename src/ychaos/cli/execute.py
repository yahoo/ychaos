#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from abc import ABC
from argparse import Namespace
from pathlib import Path
from typing import Any, Optional

from ..core.executor.MachineTargetExecutor import MachineTargetExecutor
from ..testplan.attack import TargetType
from . import YChaosCLIHook, YChaosTestplanInputSubCommand


class YChaosCLITargetExecutorHook(YChaosCLIHook, ABC):
    def __init__(self, app):
        super(YChaosCLITargetExecutorHook, self).__init__(app=app)
        self._exitcode = 0


class Execute(YChaosTestplanInputSubCommand):

    name = "execute"
    help = "The execute subcommand of YChaos"

    def __init__(self, **kwargs):
        super(Execute, self).__init__(**kwargs)

        self.test_plan_path: Path = kwargs.pop("testplan")

        self.testplan = self.get_validated_test_plan(self.test_plan_path)
        if not self.testplan:
            self.set_exitcode(1)
            return

        self.executor: Optional[Any] = None

    # Section: Hooks for each Target Type

    def _register_machine_target_hooks(self) -> None:
        """
        Registers all the CLI hooks for Machine Target Type executor
        Returns:
            None
        """
        assert isinstance(self.executor, MachineTargetExecutor)

        class OnTargetExecutorStart(YChaosCLITargetExecutorHook):
            def __call__(self):
                self.console.log(
                    f"Starting attack. executor={MachineTargetExecutor.__target_type__}"
                )

        class OnTargetUnreachableHook(YChaosCLITargetExecutorHook):
            def __call__(self, result):
                self.console.print(f"{result._host.get_name()} is unreachable")
                self._exitcode = 1

        class OnTargetFailedHook(YChaosCLITargetExecutorHook):  # pragma: no cover
            def __call__(self, result):
                self.console.log(
                    f"Attack on {result._host.get_name()} failed. Task={result.task_name}"
                )
                self._exitcode = 1

        class OnNoTargetsFoundHook(YChaosCLITargetExecutorHook):
            def __call__(self):
                self.console.print("No targets found for attack. Bailing out..")

        self.executor.register_hook("on_start", OnTargetExecutorStart(self.app))
        self.executor.register_hook(
            "on_target_unreachable", OnTargetUnreachableHook(self.app)
        )
        self.executor.register_hook("on_target_failed", OnTargetFailedHook(self.app))
        self.executor.register_hook(
            "on_no_targets_found", OnNoTargetsFoundHook(self.app)
        )

    def build_executor(self):
        if self.testplan.attack.target_type == TargetType.MACHINE:
            self.executor = MachineTargetExecutor(testplan=self.testplan)
            self._register_machine_target_hooks()
        elif self.testplan.attack.target_type == TargetType.SELF:
            raise NotImplementedError()
        else:
            raise NotImplementedError()

    def run(self):
        self.executor.execute()

        for hook_name, hooks in self.executor.hooks.items():
            if any([_h._exitcode != 0 for _h in hooks]):
                self.set_exitcode(1)
                break

    @classmethod
    def main(cls, args: Namespace) -> Any:
        execute = cls(**vars(args))

        if execute._exitcode != 0:
            return execute._exitcode

        execute.build_executor()
        execute.run()

        return execute._exitcode
