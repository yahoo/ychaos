#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from .BaseExecutor import BaseExecutor


class SelfTargetExecutor(BaseExecutor):

    __target_type__ = "self"

    def execute(self) -> None:
        raise NotImplementedError()
