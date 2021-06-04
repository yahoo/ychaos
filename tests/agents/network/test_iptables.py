#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import os
import subprocess
from unittest import TestCase

from mockito import ANY, unstub, verify, when

from ychaos.agents.network.iptables import IPTablesBlock, IPTablesBlockConfig


class TestIPTablesBlock(TestCase):
    def mock_subprocess_exits_normally(self, cmd):
        if isinstance(cmd, str):
            cmd = cmd.split()
        when(subprocess).run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=0))

    def mock_subprocess_exits_with_error(self, cmd):
        if isinstance(cmd, str):
            cmd = cmd.split()
        when(subprocess).run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).thenReturn(subprocess.CompletedProcess(args=[], returncode=1))

    def verify_sub_process(self, cmd):

        verify(subprocess).run(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def setUp(self) -> None:
        self.iptables_block_minion_config = IPTablesBlockConfig(
            incoming_ports=[9000, 9001],
            destination_ports=[9002, 9003],
            iptables_wait=1,
            incoming_endpoints=["203.0.113.0", "https://yahoo.com:443"],
            outgoing_endpoints=["203.0.113.0", "https://yahoo.com:443"],
        )

    def test_run_sets_ip_tables_rules(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        agent.setup()
        agent.monitor()
        self.mock_subprocess_exits_normally(ANY)
        agent.run()
        self.verify_sub_process(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.verify_sub_process(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        self.verify_sub_process(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9002"
        )
        self.verify_sub_process(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9003"
        )
        self.verify_sub_process(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        self.verify_sub_process(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 443 -d yahoo.com"
        )
        self.verify_sub_process(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        self.verify_sub_process(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 443 -d yahoo.com"
        )

    def test_run_sets_ip_tables_rules_incoming_port_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.mock_subprocess_exits_with_error(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        agent.setup()
        with self.assertRaises(IOError):
            agent.run()

    def test_run_sets_ip_tables_rules_destination_port_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9002"
        )
        self.mock_subprocess_exits_with_error(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9003"
        )
        agent.setup()
        with self.assertRaises(IOError):
            agent.run()

    def test_run_sets_ip_tables_rules_incoming_endpoint_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9002"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9003"
        )
        self.mock_subprocess_exits_with_error(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        agent.setup()
        with self.assertRaises(IOError):
            agent.run()

    def test_run_sets_ip_tables_rules_incoming_endpoint_url_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9002"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9003"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        self.mock_subprocess_exits_with_error(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 443 -d yahoo.com"
        )
        agent.setup()
        with self.assertRaises(IOError):
            agent.run()

    def test_run_sets_ip_tables_rules_outgoing_endpoint_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9002"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9003"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 443 -d yahoo.com"
        )
        self.mock_subprocess_exits_with_error(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        agent.setup()
        with self.assertRaises(IOError):
            agent.run()

    def test_run_sets_ip_tables_rules_outgoing_endpoint_url_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9000"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 9001"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9002"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 9003"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I INPUT -p tcp -j DROP -w 1 --dport 443 -d yahoo.com"
        )
        self.mock_subprocess_exits_normally(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 -d 203.0.113.0/32"
        )
        self.mock_subprocess_exits_with_error(
            "sudo iptables -I OUTPUT -p tcp -j DROP -w 1 --dport 443 -d yahoo.com"
        )
        agent.setup()
        with self.assertRaises(IOError):
            agent.run()

    def test_teardown_drops_ip_tables_rules_error(self):
        when(os).geteuid().thenReturn(0)
        iptables_block_minion_config = self.iptables_block_minion_config
        agent = IPTablesBlock(iptables_block_minion_config)
        self.mock_subprocess_exits_with_error(ANY)
        with self.assertRaises(Exception):
            agent.teardown()

    def tearDown(self) -> None:
        unstub()
