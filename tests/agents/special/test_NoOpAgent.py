#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import os
from unittest import TestCase

from mockito import unstub, when

from ychaos.agents.agent import AgentConfig, AgentState
from ychaos.agents.special.NoOpAgent import NoOpAgent


class TestNoOpAgent(TestCase):
    def setUp(self) -> None:
        self.agent_config = AgentConfig(name="noop")

    def test_no_op_agent_with_exceptions_not_empty(self):
        agent = NoOpAgent(self.agent_config)
        self.assertEqual(agent.current_state, AgentState.INIT)

        agent.setup()
        self.assertEqual(agent.current_state, AgentState.SETUP)

        agent.exception.put(TimeoutError())
        agent.start()
        self.assertEqual(agent.current_state, AgentState.ERROR)

    def test_no_op_agent_teardown_when_runner_is_alive(self):
        agent = NoOpAgent(self.agent_config)
        self.assertEqual(agent.current_state, AgentState.INIT)

        agent.setup()
        self.assertEqual(agent.current_state, AgentState.SETUP)

        agent.start()

        when(agent._runner).is_alive().thenReturn(True)

        agent.teardown()

    def test_no_op_agent_is_runnable_when_current_state_is_negative(self):
        agent = NoOpAgent(self.agent_config)
        self.assertEqual(agent.current_state, AgentState.INIT)

        agent.advance_state(AgentState.ERROR)
        self.assertFalse(agent.is_runnable())

    def test_no_op_agent_is_runnable_when_requires_sudo_but_process_non_sudo(self):
        when(os).geteuid().thenReturn(1)
        self.agent_config.is_sudo = True
        agent = NoOpAgent(self.agent_config)
        self.assertEqual(agent.current_state, AgentState.INIT)

        self.assertFalse(agent.is_runnable())

    def test_no_op_agent_current_state_when_state_history_not_available(self):
        self.agent_config.is_sudo = True
        agent = NoOpAgent(self.agent_config)
        agent._state_history = None

        self.assertEqual(agent.current_state, AgentState.UNDEFINED)

    def tearDown(self) -> None:
        unstub()
