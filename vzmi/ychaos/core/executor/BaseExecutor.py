#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from vzmi.ychaos.core.exceptions.executor_errors import (
    YChaosTargetConfigConditionFailedError,
)
from vzmi.ychaos.testplan.schema import TestPlan


class BaseExecutor:

    __target_type__: str

    def __init__(self, testplan: TestPlan, *args, **kwargs):
        self.testplan = testplan
        self._validate_target_config()

    def _get_target_type(self):
        # To avoid circular import
        from vzmi.ychaos.testplan.attack import TargetType

        return TargetType(self.__target_type__)

    def _validate_target_config(self):
        target_config = self.testplan.attack.get_target_config()
        if self.testplan.attack.target_type != self._get_target_type():
            raise YChaosTargetConfigConditionFailedError("Target type mismatch")

        # Even though ideally this branch is never entered by the code (unless there is some issue with pydantic)
        if not isinstance(
            target_config, self._get_target_type().MACHINE.metadata.schema
        ):  # pragma: no cov
            raise YChaosTargetConfigConditionFailedError(
                "Target configuration is not processable for this executor"
            )
