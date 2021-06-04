#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms


class AgentError(Exception):
    def __init__(self, msg: str, **kwargs):
        self.msg = msg


class InsufficientPermissionError(AgentError):
    pass
