#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from abc import ABC, abstractmethod

from ...testplan.schema import TestPlan
from ...utils.hooks import EventHook
from ..exceptions.executor_errors import YChaosTargetConfigConditionFailedError


class BaseExecutor(EventHook, ABC):
    """
    TargetExecutor defines the target where the agents are executed to
    test the resiliency of the system. A simple example of Target Executor is the
    [MachineTargetExecutor][ychaos.core.executor.MachineTargetExecutor.MachineTargetExecutor]
    which holds the program logic to execute the agents (with Coordinator) in Virtual Machines/BareMetals

    Each new Target Executor overrides the `execute()` method which defines "what" is to be done
    to execute the agents in a particular target environment.

    This class extends the [EventHook][ychaos.utils.hooks.EventHook] class, which
    implies each of the target executor can define its own events and the hooks that will
    be called during the trigger of an event.
    """

    __target_type__: str

    def __init__(self, testplan: TestPlan, *args, **kwargs):
        super(BaseExecutor, self).__init__()
        self.testplan = testplan
        self._validate_target_config()

    def _get_target_type(self):
        # To avoid circular import
        from ...testplan.attack import TargetType

        return TargetType(self.__target_type__)

    def _validate_target_config(self):
        target_config = self.testplan.attack.get_target_config()
        if self.testplan.attack.target_type != self._get_target_type():
            raise YChaosTargetConfigConditionFailedError("Target type mismatch")

        # Even though ideally this branch is never entered by the code (unless there is some issue with pydantic)
        if not isinstance(
            target_config, self._get_target_type().metadata.schema
        ):  # pragma: no cover
            raise YChaosTargetConfigConditionFailedError(
                "Target configuration is not processable for this executor"
            )

    @abstractmethod
    def execute(self) -> None:
        """
        Define "what" is to be done when the testplan consists
        the instruction to execute the agents in a particular
        target environment.

        Returns:
            None
        """
        pass  # Implement in Executors
