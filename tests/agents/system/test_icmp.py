#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import math
import multiprocessing
import os
from datetime import datetime, timedelta
from unittest import TestCase

from mockito import unstub, verify, when

from ychaos.agents.agent import AgentState
from ychaos.agents.system.cpu import CPUBurn, CPUBurnConfig, _burn
from ychaos.agents.system.icmp import PingDisable, PingDisableConfig
from ychaos.agents.utils.sysctl import SysCtl
from ychaos.utils.dependency import DependencyUtils


class TestPingDisable(TestCase):
    def setUp(self) -> None:
        pass

    def test_ping_disable_setup(self):
        config = PingDisableConfig()
        agent = PingDisable(config)
        when(SysCtl).get("net.ipv4.icmp_echo_ignore_all").thenReturn(0)
        agent.setup()

        self.assertFalse(agent.preserved_state.is_ping_disabled)

    def test_ping_disable_run_when_ping_not_disabled(self):
        config = PingDisableConfig()
        agent = PingDisable(config)

        when(SysCtl).get("net.ipv4.icmp_echo_ignore_all").thenReturn(0)
        agent.setup()

        when(os).geteuid().thenReturn(0)
        when(SysCtl).set("net.ipv4.icmp_echo_ignore_all", b"1").thenReturn(True)
        agent.run()
        verify(SysCtl, times=1).set("net.ipv4.icmp_echo_ignore_all", b"1")

        agent.monitor()

        when(SysCtl).set("net.ipv4.icmp_echo_ignore_all", b"0").thenReturn(True)
        agent.teardown()
        verify(SysCtl, times=1).set("net.ipv4.icmp_echo_ignore_all", b"0")

    def test_ping_disable_run_when_ping_already_disabled(self):
        config = PingDisableConfig()
        agent = PingDisable(config)

        when(SysCtl).get("net.ipv4.icmp_echo_ignore_all").thenReturn(1)
        agent.setup()

        when(os).geteuid().thenReturn(0)
        agent.run()
        verify(SysCtl, times=0).set("net.ipv4.icmp_echo_ignore_all", b"1")

        agent.monitor()

        agent.teardown()
        verify(SysCtl, times=0).set("net.ipv4.icmp_echo_ignore_all", b"0")

    def tearDown(self) -> None:
        unstub()
