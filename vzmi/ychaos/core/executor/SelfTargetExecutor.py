#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from vzmi.ychaos.core.executor.BaseExecutor import BaseExecutor


class SelfTargetExecutor(BaseExecutor):

    __target_type__ = "self"

    def execute(self) -> None:
        raise NotImplementedError()
