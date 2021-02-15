#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms


class AgentError(Exception):
    def __init__(self, msg: str, **kwargs):
        self.msg = msg
