#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from typing import List

from pydantic import BaseModel


class AgentStatus(BaseModel):
    agent_name: str
    start_time: str
    end_time: str
    status: str


class AttackReport(BaseModel):
    """
    Attack Report Structure
    """

    id: str
    host: str
    attack_start_time: str
    expected_attack_end_time: str
    mode: str
    agents: List[AgentStatus]
