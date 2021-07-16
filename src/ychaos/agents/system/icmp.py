#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

# TODO: PingDisable Agent
import warnings
from queue import LifoQueue

from ..agent import (
    Agent,
    AgentMonitoringDataPoint,
    AgentPriority,
    TimedAgentConfig,
)
from ..utils.annotations import log_agent_lifecycle
from ..utils.sysctl import SysCtl


class PingDisableConfig(TimedAgentConfig):
    name = "ping_disable"
    description = "This agent disables the system to respond to ping/icmp packets"

    priority = AgentPriority.MODERATE_PRIORITY
    is_sudo = True


class PingDisable(Agent):

    sysctl_var = "net.ipv4.icmp_echo_ignore_all"

    def monitor(self) -> LifoQueue:
        super(PingDisable, self).monitor()
        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(),  # TODO: Ping localhost and add monitoring data
                state=self.current_state,
            )
        )
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(PingDisable, self).setup()
        self.preserved_state.is_ping_disabled = int(SysCtl.get(self.sysctl_var)) == 1

    @log_agent_lifecycle
    def run(self) -> None:
        super(PingDisable, self).run()
        if self.preserved_state.is_ping_disabled:
            warnings.warn(
                "ICMP ignore is already turned on. "
                "Running this agent will be a no-operation"
            )
        else:
            SysCtl.set(self.sysctl_var, b"1")

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(PingDisable, self).teardown()
        if not self.preserved_state.is_ping_disabled:
            SysCtl.set(self.sysctl_var, b"0")
