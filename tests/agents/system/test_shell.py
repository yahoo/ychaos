#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import subprocess
from unittest import TestCase

from mockito import unstub, when

from ychaos.agents.agent import AgentState
from ychaos.agents.system.shell import Shell, ShellConfig


class TestShell(TestCase):
    def setUp(self) -> None:
        self.shell_config = ShellConfig(
            command="echo 'testing shell agent'", use_shell=False, timeout=15
        )

    def test_shell_agent(self):
        shell_agent = Shell(self.shell_config)
        shell_agent.setup()
        self.assertEqual(AgentState.SETUP, shell_agent.current_state)

        shell_agent.run()
        self.assertEqual(AgentState.RUNNING, shell_agent.current_state)

        when(subprocess).Popen("echo 'testing shell agent'", shell=False).thenReturn(
            None
        )

        when(subprocess).Popen(
            "echo 'testing shell agent'",
            shell=False,
            stdin=subprocess.PIPE,
            cwd=None,
            env=None,
        ).thenReturn(None)

        monitor_status_queue = shell_agent.monitor()
        status = monitor_status_queue.get()

        self.assertEqual(status.data["stdout"], None)
        self.assertEqual(status.data["stderr"], None)

        shell_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, shell_agent.current_state)

    def tearDown(self) -> None:
        unstub()
