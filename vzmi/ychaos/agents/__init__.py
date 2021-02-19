#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from types import SimpleNamespace

from vzmi.ychaos.utils.builtins import AEnum

from .agent import AgentConfig, TimedAgentConfig


class AgentType(AEnum):

    # Special Agents
    NO_OP = "no_op", SimpleNamespace(schema=AgentConfig)
    NO_OP_TIMED = "no_op_timed", SimpleNamespace(schema=TimedAgentConfig)

    # System Agents
    # TODO: Add CPU Burn etc.
