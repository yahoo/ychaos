#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from typing import Any, Dict


class YChaosError(Exception):
    def __init__(self, e, message, **kwargs):
        self.exception = e
        self.message: str = message
        self.attrs: Dict[str, Any] = kwargs
