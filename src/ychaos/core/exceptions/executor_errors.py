#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from ychaos.core.exceptions import YChaosError


class YChaosTargetConfigConditionFailedError(YChaosError):
    def __init__(self, message: str, **kwargs):
        super(YChaosTargetConfigConditionFailedError, self).__init__(
            ValueError("Testplan target configuration condition failed"),
            message,
            **kwargs,
        )
