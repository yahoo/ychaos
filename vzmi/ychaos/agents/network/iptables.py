#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

import shlex
import subprocess  # nosec using shlex
from enum import Enum
from ipaddress import IPv4Address, IPv4Network
from queue import LifoQueue
from typing import List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    Field,
    IPvAnyAddress,
    IPvAnyNetwork,
    validate_arguments,
)

from vzmi.ychaos.agents.agent import (
    Agent,
    AgentMonitoringDataPoint,
    TimedAgentConfig,
)
from vzmi.ychaos.agents.exceptions import AgentError

__all__ = ["IPTablesBlockConfig", "IPTablesBlock"]


class IptablesChain(Enum):
    OUTPUT = "OUTPUT"
    INPUT = "INPUT"


class IptablesRuleOperation(Enum):
    INSERT = "-I"
    DELETE = "-D"


def iptables_command_builder(
    operation, chain, port, endpoint, iptable_wait_second
) -> str:
    command = f"sudo iptables {shlex.quote(operation)} {shlex.quote(chain)}"

    args = f" -p tcp -j DROP -w {shlex.quote(str(iptable_wait_second))}"

    if port:
        args += f" --dport {shlex.quote(str(port))}"

    if endpoint:
        args += f" -d {shlex.quote(endpoint)}"

    return command + args


class IPTablesBlockConfig(TimedAgentConfig):
    name = "block_ports"
    desc = "This minion modifies the iptables rules to block traffic to specified ports or endpoint"
    is_sudo = True
    incoming_ports: Optional[List[int]] = Field(
        description="List of incoming ports to block",
        default=list(),
        examples=[[3000, 4443]],
    )
    ip_table_wait_sec: int = Field(
        description="Wait for the  lock. To prevent multiple instances of the program from running concurrently, an attempt will be made to obtain an exclusive lock at launch",
        default=3,
        examples=[500, 450, 120],
        lt=1800,
        gt=0,
    )

    destination_ports: Optional[List[int]] = Field(
        description="List of destination ports to block",
        default=list(),
        examples=[[3000, 4443]],
    )

    incoming_endpoints: Optional[
        List[Union[IPvAnyNetwork, AnyHttpUrl, IPvAnyAddress]]
    ] = Field(
        description="List of incoming endpoint to block",
        examples=["203.0.113.0", "https://yahoo.com:443"],
    )

    outgoing_endpoints: Optional[
        List[Union[IPvAnyNetwork, AnyHttpUrl, IPvAnyAddress]]
    ] = Field(
        description="List of outgoing endpoint to block",
        examples=["203.0.113.0", "https://yahoo.com:443"],
    )

    duration: int = Field(
        description="The duration(in Secs) for which BlockPort Minion Runs",
        default=300,
        examples=[500, 450, 120],
        lt=1800,
        gt=0,
    )


class IPTablesBlock(Agent):
    @validate_arguments
    def __init__(self, config: IPTablesBlockConfig):
        super(IPTablesBlock, self).__init__(config)

    def monitor(self) -> LifoQueue:
        super(IPTablesBlock, self).monitor()
        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(),
                state=self.current_state,
            )
        )
        return self._status

    def setup(self) -> None:
        super(IPTablesBlock, self).setup()

    @staticmethod
    def raise_io_error_on_iptables_failure(proc: subprocess.CompletedProcess, message):
        if proc.returncode != 0:
            raise IOError(message)

    def run(self) -> None:
        super(IPTablesBlock, self).run()
        for port in self.config.incoming_ports:
            proc = subprocess.run(  # nosec using shlex
                iptables_command_builder(
                    IptablesRuleOperation.INSERT.value,
                    IptablesChain.INPUT.value,
                    port,
                    None,
                    self.config.ip_table_wait_sec,
                ).split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.raise_io_error_on_iptables_failure(
                proc, f"Error While Adding IpTable Rule: DROP {port} to INPUT Chain"
            )
        for port in self.config.destination_ports:
            proc = subprocess.run(  # nosec using shlex
                iptables_command_builder(
                    IptablesRuleOperation.INSERT.value,
                    IptablesChain.OUTPUT.value,
                    port,
                    None,
                    self.config.ip_table_wait_sec,
                ).split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.raise_io_error_on_iptables_failure(
                proc, f"Error While Adding IpTable Rule: DROP {port} to OUTPUT Chain"
            )

        for endpoint in self.config.incoming_endpoints:
            if isinstance(endpoint, AnyHttpUrl):
                proc = subprocess.run(  # nosec using shlex
                    iptables_command_builder(
                        IptablesRuleOperation.INSERT.value,
                        IptablesChain.INPUT.value,
                        endpoint.port,
                        str(endpoint.host),
                        self.config.ip_table_wait_sec,
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.raise_io_error_on_iptables_failure(
                    proc,
                    f"Error While Adding IpTable Rule: DROP {endpoint} to INPUT Chain",
                )

            elif isinstance(endpoint, (IPv4Network, IPv4Address)):
                proc = subprocess.run(  # nosec using shlex
                    iptables_command_builder(
                        IptablesRuleOperation.INSERT.value,
                        IptablesChain.INPUT.value,
                        None,
                        str(endpoint),
                        self.config.ip_table_wait_sec,
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.raise_io_error_on_iptables_failure(
                    proc,
                    f"Error While Adding IpTable Rule: DROP {endpoint} to INPUT Chain",
                )

        for endpoint in self.config.outgoing_endpoints:
            if isinstance(endpoint, AnyHttpUrl):
                proc = subprocess.run(  # nosec using shlex
                    iptables_command_builder(
                        IptablesRuleOperation.INSERT.value,
                        IptablesChain.OUTPUT.value,
                        endpoint.port,
                        str(endpoint.host),
                        self.config.ip_table_wait_sec,
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.raise_io_error_on_iptables_failure(
                    proc,
                    f"Error While Adding IpTable Rule: DROP {endpoint} to INPUT Chain",
                )

            elif isinstance(endpoint, (IPv4Network, IPv4Address)):
                proc = subprocess.run(  # nosec using shlex
                    iptables_command_builder(
                        IptablesRuleOperation.INSERT.value,
                        IptablesChain.OUTPUT.value,
                        None,
                        str(endpoint),
                        self.config.ip_table_wait_sec,
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                self.raise_io_error_on_iptables_failure(
                    proc,
                    f"Error While Adding IpTable Rule: DROP {endpoint} to INPUT Chain",
                )

    def teardown(self) -> None:
        super(IPTablesBlock, self).teardown()
        error = False
        for port in self.config.incoming_ports:
            proc = subprocess.run(  # nosec using shlex
                iptables_command_builder(
                    IptablesRuleOperation.DELETE.value,
                    IptablesChain.INPUT.value,
                    port,
                    None,
                    self.config.ip_table_wait_sec,
                ).split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            error = proc.returncode != 0 or error

        for port in self.config.destination_ports:
            proc = subprocess.run(  # nosec using shlex
                iptables_command_builder(
                    IptablesRuleOperation.DELETE.value,
                    IptablesChain.OUTPUT.value,
                    port,
                    None,
                    self.config.ip_table_wait_sec,
                ).split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            error = proc.returncode != 0 or error

        for endpoint in self.config.incoming_endpoints:
            if isinstance(endpoint, AnyHttpUrl):
                proc = subprocess.run(  # nosec using shlex
                    iptables_command_builder(
                        IptablesRuleOperation.DELETE.value,
                        IptablesChain.INPUT.value,
                        endpoint.port,
                        str(endpoint.host),
                        self.config.ip_table_wait_sec,
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                error = proc.returncode != 0 or error

            elif isinstance(endpoint, (IPv4Network, IPv4Address)):
                proc = subprocess.run(  # nosec using shlex
                    iptables_command_builder(
                        IptablesRuleOperation.DELETE.value,
                        IptablesChain.OUTPUT.value,
                        None,
                        str(endpoint),
                        self.config.ip_table_wait_sec,
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                error = proc.returncode != 0 or error

        if error:
            raise AgentError("Error Occurred while removing IpTable rule")
