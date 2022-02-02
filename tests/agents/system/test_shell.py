#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import collections
import shutil
import subprocess
from pathlib import Path
from unittest import TestCase

from mockito import unstub, when

from ychaos.agents.agent import AgentState
from ychaos.agents.system.shell import Shell, ShellConfig


class TestShell(TestCase):
    def setUp(self) -> None:
        self.usage = collections.namedtuple("usage", "total used free")
        self.stats = self.usage(2048, 1024, 1024)
        self.shell_config = ShellConfig(command="mkdir shellDir")

    def test_shell_agent(self):
        shell_agent = Shell(self.shell_config)
        shell_agent.setup()
        self.assertEqual(AgentState.SETUP, shell_agent.current_state)

        shell_agent.run()
        self.assertEqual(AgentState.RUNNING, shell_agent.current_state)

        shell_file = Path().resolve() / "shellDir"
        self.assertTrue(shell_file.exists())

        when(subprocess).Popen("mkdir shellDir;", shell=True).thenReturn(None)

        monitor_status_queue = shell_agent.monitor()
        status = monitor_status_queue.get()

        self.assertEqual(status.data["stdout"], None)
        self.assertEqual(status.data["stderr"], None)

        shell_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, shell_agent.current_state)

    def tearDown(self) -> None:
        shell_fir_path = Path().resolve() / "shellDir"
        if shell_fir_path.exists():
            shutil.rmtree(shell_fir_path)
        unstub()
