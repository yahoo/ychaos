#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

import filecmp
import os
import shutil
from pathlib import Path
from stat import S_IWUSR, S_IREAD, S_IWRITE, S_IRGRP, S_IROTH
from unittest import TestCase

from mockito import when, unstub

from vzmi.ychaos.agents.network.traffic import BlockTrafficConfig, BlockTraffic

from tempfile import NamedTemporaryFile


class TestBlockTraffic(TestCase):

    targetFilePath = "/tmp/targetHostsFile"
    expectedTargetFilePath = f"{os.path.dirname(__file__)}/res/expectedTargetHosts"
    backupFilePath = "/tmp/backup_hosts_file"

    def setUp(self) -> None:
        self.test_hostsfile = NamedTemporaryFile("w+", delete=False).name
        with open(self.test_hostsfile, "w") as file:
            file.write("\n")
            file.write("127.0.0.1	thissitedoesnotexist.com\n")
            file.write("127.0.0.1	thissitealsodoesnotexist.com\n")

    def test_setup_create_backup_file(self):
        block_traffic_config = BlockTrafficConfig(
            hosts=["thissitedoesnotexist.com", "thissitealsodoesnotexist.com"],
            hostsfile=self.test_hostsfile,
        )
        self.assertIsNone(block_traffic_config.backup_hostsfile)

        agent = BlockTraffic(block_traffic_config)

        agent.setup()
        self.assertTrue(agent.config.backup_hostsfile.is_file())
        self.assertTrue(filecmp.cmp(self.test_hostsfile, agent.config.backup_hostsfile))

        with open(self.test_hostsfile, "w") as file:
            file.write("mockTest")

    def test_teardown_resets_the_host_file(self):
        block_traffic_config = BlockTrafficConfig(
            hosts=["thissitedoesnotexist.com", "thissitealsodoesnotexist.com"],
            hostsfile=self.test_hostsfile,
        )
        self.assertIsNone(block_traffic_config.backup_hostsfile)

        agent = BlockTraffic(block_traffic_config)

        agent.setup()
        self.assertTrue(agent.config.backup_hostsfile.is_file())
        self.assertTrue(filecmp.cmp(self.test_hostsfile, agent.config.backup_hostsfile))

        backup_hostfile_copy = NamedTemporaryFile("w+")
        shutil.copy(agent.config.backup_hostsfile, backup_hostfile_copy.name)

        with open(self.test_hostsfile, "w") as file:
            file.write("mockTest")

        agent.teardown()
        self.assertFalse(agent.config.backup_hostsfile.is_file())
        self.assertTrue(filecmp.cmp(self.test_hostsfile, backup_hostfile_copy.name))

    def test_run_modifes_hosts_file(self):
        block_traffic_config = BlockTrafficConfig(
            hosts=["testredirect.com"], hostsfile=self.test_hostsfile
        )
        self.assertIsNone(block_traffic_config.backup_hostsfile)

        agent = BlockTraffic(block_traffic_config)

        agent.setup()
        self.assertTrue(agent.config.backup_hostsfile.is_file())
        self.assertTrue(filecmp.cmp(self.test_hostsfile, agent.config.backup_hostsfile))

        when(os).geteuid().thenReturn(0)

        agent.run()
        test_hostsfile_content = Path(self.test_hostsfile).read_text()
        self.assertTrue("127.0.0.1	testredirect.com" in test_hostsfile_content)

        backup_hostfile_copy = NamedTemporaryFile("w+")
        shutil.copy(agent.config.backup_hostsfile, backup_hostfile_copy.name)

        agent.teardown()
        self.assertFalse(agent.config.backup_hostsfile.is_file())
        self.assertTrue(filecmp.cmp(self.test_hostsfile, backup_hostfile_copy.name))

    def tearDown(self) -> None:
        Path(self.test_hostsfile).unlink()
        unstub()
