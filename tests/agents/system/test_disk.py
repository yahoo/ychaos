#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import collections
import shutil
from pathlib import Path
from unittest import TestCase

from mockito import unstub, when

from ychaos.agents.agent import AgentState
from ychaos.agents.system.disk import DiskFill, DiskFillConfig


class TestDiskFill(TestCase):
    def setUp(self) -> None:
        self.usage = collections.namedtuple("usage", "total used free")
        self.stats = self.usage(2048, 1024, 1024)
        when(shutil).disk_usage(Path(".")).thenReturn(self.stats)
        self.disk_fill_config_50 = DiskFillConfig(
            duration=0.1, partition="./", partition_pct=50
        )
        self.disk_fill_config_100 = DiskFillConfig(
            duration=0.1, partition="./", partition_pct=100
        )

    def test_disk_fill_when_percentage_fill_normal(self):

        disk_fill_agent = DiskFill(self.disk_fill_config_50)

        self.assertEqual(
            str(Path().resolve()),
            self.disk_fill_config_50.partition.absolute().as_posix(),
        )
        self.assertEqual(50, self.disk_fill_config_50.partition_pct)

        disk_fill_agent.setup()
        self.assertEqual(AgentState.SETUP, disk_fill_agent.current_state)

        disk_fill_agent.run()
        self.assertEqual(AgentState.RUNNING, disk_fill_agent.current_state)

        ychaos_diskfill_dir_path = Path().resolve() / "ychaos_diskfill"
        self.assertTrue(ychaos_diskfill_dir_path.exists())
        disk_dir = Path().resolve() / "ychaos_diskfill/filler0.txt"
        self.assertEqual(512, disk_dir.stat().st_size)

        disk_fill_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, disk_fill_agent.current_state)
        self.assertFalse(ychaos_diskfill_dir_path.exists())

    def test_disk_fill_when_percentage_fill_full(self):
        disk_fill_agent = DiskFill(self.disk_fill_config_100)

        self.assertEqual(
            str(Path().resolve()),
            self.disk_fill_config_100.partition.absolute().as_posix(),
        )
        self.assertEqual(100, self.disk_fill_config_100.partition_pct)

        disk_fill_agent.setup()
        self.assertEqual(AgentState.SETUP, disk_fill_agent.current_state)

        disk_fill_agent.run()
        self.assertEqual(AgentState.RUNNING, disk_fill_agent.current_state)

        disk_dir = Path().resolve() / "ychaos_diskfill/filler0.txt"
        self.assertEqual(1024, disk_dir.stat().st_size)

        disk_fill_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, disk_fill_agent.current_state)

    def test_disk_fill_when_percentage_fill_stop_run(self):
        disk_fill_agent = DiskFill(self.disk_fill_config_100)

        self.assertEqual(
            str(Path().resolve()),
            self.disk_fill_config_100.partition.absolute().as_posix(),
        )
        self.assertEqual(100, self.disk_fill_config_100.partition_pct)

        disk_fill_agent.setup()
        self.assertEqual(AgentState.SETUP, disk_fill_agent.current_state)

        disk_fill_agent.stop_async_run = True

        disk_fill_agent.run()
        self.assertEqual(AgentState.RUNNING, disk_fill_agent.current_state)

        ychaos_diskfill_file_0 = Path().resolve() / "ychaos_diskfill/filler0.txt"
        self.assertFalse(ychaos_diskfill_file_0.exists())

        disk_fill_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, disk_fill_agent.current_state)

    def test_disk_teardown_with_multiple_files(self):
        self.disk_fill_config_100.max_file_size = 1000
        disk_fill_agent = DiskFill(self.disk_fill_config_100)

        self.assertEqual(
            str(Path().resolve()),
            self.disk_fill_config_100.partition.absolute().as_posix(),
        )
        self.assertEqual(100, self.disk_fill_config_100.partition_pct)

        disk_fill_agent.setup()
        self.assertEqual(AgentState.SETUP, disk_fill_agent.current_state)

        disk_fill_agent.run()
        self.assertEqual(AgentState.RUNNING, disk_fill_agent.current_state)

        disk_dir = Path().resolve() / "ychaos_diskfill/filler0.txt"
        self.assertEqual(1000, disk_dir.stat().st_size)

        disk_fill_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, disk_fill_agent.current_state)

    def test_disk_teardown_without_disk_fill_dir(self):
        stats = self.usage(4096, 4096, 0)
        when(shutil).disk_usage(Path(".")).thenReturn(stats)
        disk_fill_agent = DiskFill(self.disk_fill_config_100)

        self.assertEqual(
            str(Path().resolve()),
            self.disk_fill_config_100.partition.absolute().as_posix(),
        )
        self.assertEqual(100, self.disk_fill_config_100.partition_pct)

        disk_fill_agent.setup()
        self.assertEqual(AgentState.SETUP, disk_fill_agent.current_state)

        disk_fill_agent.run()
        self.assertEqual(AgentState.RUNNING, disk_fill_agent.current_state)

        files_dir = Path().resolve() / "ychaos_diskfill"
        self.assertFalse(files_dir.exists())

        disk_fill_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, disk_fill_agent.current_state)

    def test_disk_burn_monitor(self):
        disk_fill_config = DiskFillConfig(
            duration=0.1, partition="./", partition_pct=50
        )
        disk_fill_agent = DiskFill(disk_fill_config)

        monitor_status_queue = disk_fill_agent.monitor()
        status = monitor_status_queue.get()

        self.assertEqual(512, status.data["disk_space_to_fill"])
        self.assertEqual(1024, status.data["disk_free_space"])

    def tearDown(self) -> None:
        unstub()
