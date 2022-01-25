#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import collections
import shutil
from pathlib import Path
from unittest import TestCase

from mockito import unstub, when

from ychaos.agents.agent import AgentState
from ychaos.agents.system.shell import Shell, ShellConfig


class TestShell(TestCase):
    def setUp(self) -> None:
        self.usage = collections.namedtuple("usage", "total used free")
        self.stats = self.usage(2048, 1024, 1024)
        when(shutil).disk_usage(Path(".")).thenReturn(self.stats)
        self.shell_config = ShellConfig(
            command="mkdir shellDir; cd shellDir; touch temp; cd ../"
        )
        self.shell_2_config = ShellConfig(command="rm -rf shellDir")

    def test_shell_agent(self):

        shell_agent = Shell(self.shell_config)

        shell_agent.setup()
        self.assertEqual(AgentState.SETUP, shell_agent.current_state)

        shell_agent.run()
        self.assertEqual(AgentState.RUNNING, shell_agent.current_state)

        shell_file = Path().resolve() / "shellDir/temp"
        self.assertTrue(shell_file.exists())

        shell_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, shell_agent.current_state)

        shell_agent = Shell(self.shell_2_config)

        shell_agent.setup()
        self.assertEqual(AgentState.SETUP, shell_agent.current_state)

        shell_agent.run()
        self.assertEqual(AgentState.RUNNING, shell_agent.current_state)

        shell_fir_path = Path().resolve() / "shellDir"
        self.assertFalse(shell_fir_path.exists())

        shell_agent.monitor()

        shell_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, shell_agent.current_state)

    def tearDown(self) -> None:
        unstub()
