#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import subprocess
from unittest import TestCase

from mockito import mock, unstub, when

from ychaos.agents.agent import AgentState
from ychaos.agents.exceptions import AgentError
from ychaos.agents.system.shell import Shell, ShellConfig


class TestShell(TestCase):
    def setUp(self) -> None:
        self.shell_config = ShellConfig(
            command="echo 'testing shell agent'", use_shell=False
        )

    def test_shell_agent(self):
        shell_agent = Shell(self.shell_config)
        shell_agent.setup()
        self.assertEqual(AgentState.SETUP, shell_agent.current_state)

        mock_process = mock(spec=subprocess.Popen, config_or_spec=dict(returncode=0))

        when(subprocess).Popen(
            ["echo", "testing shell agent"],
            shell=False,
            stdin=subprocess.PIPE,
            cwd=None,
            env=None,
        ).thenReturn(mock_process)
        when(mock_process).communicate(timeout=300).thenReturn((None, None))

        shell_agent.run()

        self.assertEqual(AgentState.RUNNING, shell_agent.current_state)

        monitor_status_queue = shell_agent.monitor()
        status = monitor_status_queue.get()

        self.assertEqual(status.data["stdout"], None)
        self.assertEqual(status.data["stderr"], None)
        self.assertEqual(status.data["rc"], 0)

        shell_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, shell_agent.current_state)

    def test_shell_agent_error_while_executing(self):
        shell_agent = Shell(self.shell_config)
        shell_agent.setup()
        self.assertEqual(AgentState.SETUP, shell_agent.current_state)

        mock_process = mock(spec=subprocess.Popen, config_or_spec=dict(returncode=1))

        when(subprocess).Popen(
            ["echo", "testing shell agent"],
            shell=False,
            stdin=subprocess.PIPE,
            cwd=None,
            env=None,
        ).thenReturn(mock_process)
        when(mock_process).communicate(timeout=300).thenReturn(
            (b"mock_stdout", b"mock_stderr")
        )

        with self.assertRaises(AgentError):
            shell_agent.run()

        self.assertEqual(AgentState.RUNNING, shell_agent.current_state)

        monitor_status_queue = shell_agent.monitor()
        status = monitor_status_queue.get()

        self.assertEqual(status.data["stdout"], b"mock_stdout")
        self.assertEqual(status.data["stderr"], b"mock_stderr")
        self.assertEqual(status.data["rc"], 1)

        shell_agent.teardown()
        self.assertEqual(AgentState.TEARDOWN, shell_agent.current_state)

    def tearDown(self) -> None:
        unstub()
