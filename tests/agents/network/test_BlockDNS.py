#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import os
import subprocess
from unittest import TestCase

from mockito import any, unstub, verify, when

from ychaos.agents.agent import AgentState
from ychaos.agents.exceptions import AgentError
from ychaos.agents.network.iptables import DNSBlock, DNSBlockConfig


class TestBlockDNSConfig(TestCase):
    def test_block_dns_setup(self):
        config = DNSBlockConfig()
        agent = DNSBlock(config)
        agent.setup()
        agent.monitor()  # coverage

        self.assertEqual(agent.current_state, AgentState.SETUP)

    def test_block_dns_teardown_does_not_modify_iptables_rule_when_in_setup(self):
        config = DNSBlockConfig()
        agent = DNSBlock(config)
        agent.setup()

        self.assertEqual(agent.current_state, AgentState.SETUP)

        when(subprocess).run(
            any,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        agent.teardown()

        verify(subprocess, times=0).run(
            any,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_block_dns_run(self):
        config = DNSBlockConfig()
        agent = DNSBlock(config)
        agent.setup()

        self.assertEqual(agent.current_state, AgentState.SETUP)

        when(os).geteuid().thenReturn(0)

        when(subprocess).run(
            "sudo iptables -I OUTPUT -p udp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        when(subprocess).run(
            f"sudo iptables -I OUTPUT -p tcp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        agent.run()

        self.assertEqual(agent.current_state, AgentState.RUNNING)

    def test_block_dns_run_raises_io_error(self):
        config = DNSBlockConfig()
        agent = DNSBlock(config)
        agent.setup()

        self.assertEqual(agent.current_state, AgentState.SETUP)

        when(os).geteuid().thenReturn(0)

        when(subprocess).run(
            "sudo iptables -I OUTPUT -p udp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        when(subprocess).run(
            f"sudo iptables -I OUTPUT -p tcp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=1))

        with self.assertRaises(IOError):
            agent.run()

    def test_block_dns_teardown_restores_after_running(self):
        config = DNSBlockConfig()
        agent = DNSBlock(config)
        agent.setup()

        self.assertEqual(agent.current_state, AgentState.SETUP)

        agent.advance_state(AgentState.RUNNING)

        when(subprocess).run(
            "sudo iptables -D OUTPUT -p udp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        when(subprocess).run(
            "sudo iptables -D OUTPUT -p tcp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        agent.teardown()

        verify(subprocess, times=2).run(
            any,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_block_dns_teardown_raises_error_when_failed(self):
        config = DNSBlockConfig()
        agent = DNSBlock(config)
        agent.setup()

        self.assertEqual(agent.current_state, AgentState.SETUP)

        agent.advance_state(AgentState.RUNNING)

        when(subprocess).run(
            "sudo iptables -D OUTPUT -p udp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

        when(subprocess).run(
            "sudo iptables -D OUTPUT -p tcp --dport 53 -j DROP -w 3".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=1))

        with self.assertRaises(AgentError):
            agent.teardown()

        verify(subprocess, times=2).run(
            any,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def tearDown(self) -> None:
        unstub()
