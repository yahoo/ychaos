#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from types import SimpleNamespace

from vzmi.ychaos.agents.contrib import ContribAgentConfig
from vzmi.ychaos.agents.network.iptables import (
    DNSBlock,
    DNSBlockConfig,
    IPTablesBlock,
    IPTablesBlockConfig,
)
from vzmi.ychaos.agents.network.traffic import TrafficBlock, TrafficBlockConfig
from vzmi.ychaos.agents.special.NoOpAgent import (
    NoOpAgent,
    NoOpAgentConfig,
    NoOpTimedAgent,
    NoOpTimedAgentConfig,
)
from vzmi.ychaos.agents.system.cpu import CPUBurn, CPUBurnConfig
from vzmi.ychaos.agents.validation.certificate import (
    ServerCertValidation,
    ServerCertValidationConfig,
)
from vzmi.ychaos.utils.builtins import AEnum

__all__ = ["AgentType"]


class AgentType(AEnum):

    # Special Agents
    NO_OP = "no_op", SimpleNamespace(schema=NoOpAgentConfig, agent_defn=NoOpAgent)
    NO_OP_TIMED = "no_op_timed", SimpleNamespace(
        schema=NoOpTimedAgentConfig, agent_defn=NoOpTimedAgent
    )

    # System Agents
    CPU_BURN = "cpu_burn", SimpleNamespace(schema=CPUBurnConfig, agent_defn=CPUBurn)
    # TODO: Add CPU Burn etc.

    # Network Agents
    IPTABLES_BLOCK = "iptables_block", SimpleNamespace(
        schema=IPTablesBlockConfig, agent_defn=IPTablesBlock
    )
    DNS_BLOCK = "dns_block", SimpleNamespace(schema=DNSBlockConfig, agent_defn=DNSBlock)
    TRAFFIC_BLOCK = "traffic_block", SimpleNamespace(
        schema=TrafficBlockConfig, agent_defn=TrafficBlock
    )

    SERVER_CERT_VALIDATION = "server_cert_validation", SimpleNamespace(
        schema=ServerCertValidationConfig, agent_defn=ServerCertValidation
    )

    CONTRIB = "contrib", SimpleNamespace(
        schema=ContribAgentConfig, agent_defn=lambda config: config.get_agent()
    )
