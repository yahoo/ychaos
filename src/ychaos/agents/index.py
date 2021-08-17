#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from types import SimpleNamespace

from ..utils.builtins import AEnum
from .contrib import ContribAgentConfig
from .network.iptables import (
    DNSBlock,
    DNSBlockConfig,
    IPTablesBlock,
    IPTablesBlockConfig,
)
from .network.traffic import TrafficBlock, TrafficBlockConfig
from .special.NoOpAgent import (
    NoOpAgent,
    NoOpAgentConfig,
    NoOpTimedAgent,
    NoOpTimedAgentConfig,
)
from .system.cpu import CPUBurn, CPUBurnConfig
from .system.disk import DiskFill, DiskFillConfig
from .system.icmp import PingDisable, PingDisableConfig
from .validation.certificate import (
    CertificateFileValidation,
    CertificateFileValidationConfig,
    ServerCertValidation,
    ServerCertValidationConfig,
)

__all__ = ["AgentType"]


class AgentType(AEnum):

    # Special Agents
    NO_OP = "no_op", SimpleNamespace(schema=NoOpAgentConfig, agent_defn=NoOpAgent)
    NO_OP_TIMED = "no_op_timed", SimpleNamespace(
        schema=NoOpTimedAgentConfig, agent_defn=NoOpTimedAgent
    )

    # System Agents
    CPU_BURN = "cpu_burn", SimpleNamespace(schema=CPUBurnConfig, agent_defn=CPUBurn)

    # Network Agents
    IPTABLES_BLOCK = "iptables_block", SimpleNamespace(
        schema=IPTablesBlockConfig, agent_defn=IPTablesBlock
    )
    DNS_BLOCK = "dns_block", SimpleNamespace(schema=DNSBlockConfig, agent_defn=DNSBlock)
    TRAFFIC_BLOCK = "traffic_block", SimpleNamespace(
        schema=TrafficBlockConfig, agent_defn=TrafficBlock
    )

    # Validation Agents
    SERVER_CERT_VALIDATION = "server_cert_validation", SimpleNamespace(
        schema=ServerCertValidationConfig, agent_defn=ServerCertValidation
    )
    CERT_FILE_VALIDATION = "cert_file_validation", SimpleNamespace(
        schema=CertificateFileValidationConfig, agent_defn=CertificateFileValidation
    )

    # Special Contrib agent
    CONTRIB = "contrib", SimpleNamespace(  # pragma: no cover
        schema=ContribAgentConfig, agent_defn=lambda config: config.get_agent()
    )

    DISABLE_PING = "disable_ping", SimpleNamespace(
        schema=PingDisableConfig, agent_defn=PingDisable
    )

    DISK_FILL = "disk_fill", SimpleNamespace(schema=DiskFillConfig, agent_defn=DiskFill)
