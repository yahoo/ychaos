#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from queue import LifoQueue
from random import randint
from unittest import TestCase

from ychaos.agents.agent import Agent, AgentConfig, AgentPriority, AgentState
from ychaos.agents.exceptions import AgentError


class MockAgentConfig(AgentConfig):
    name = "mock_agent"
    description = "This is a mock agent used for testing"
    priority = AgentPriority.VERY_LOW_PRIORITY


class MockAgent(Agent):
    def monitor(self) -> LifoQueue:
        super(MockAgent, self).monitor()
        self._status.put(randint(10, 20))

    def setup(self) -> None:
        super(MockAgent, self).setup()
        print(f"Running {self.__class__.__name__} setup method")

    def run(self) -> None:
        super(MockAgent, self).run()
        print(f"Running {self.__class__.__name__} run method")

    def teardown(self) -> None:
        super(MockAgent, self).teardown()
        print(f"Running {self.__class__.__name__} teardown method")


class MockAgentTeardownRaisesError(MockAgent):
    def teardown(self) -> None:
        super(MockAgentTeardownRaisesError, self).teardown()
        raise Exception("Some Error occurred")


class TestBaseAgent(TestCase):
    def setUp(self) -> None:
        self.mock_agent_config = MockAgentConfig()

    def test_agent_setup(self):
        agent = MockAgent(self.mock_agent_config.copy())
        self.assertEqual(agent.current_state, AgentState.INIT)

        agent.setup()
        self.assertEqual(agent.current_state, AgentState.SETUP)

    def test_agent_run_when_state_matches(self):
        agent = MockAgent(self.mock_agent_config.copy())
        self.assertEqual(agent.current_state, AgentState.INIT)

        agent.advance_state(AgentState.SETUP)
        agent.run()
        self.assertEqual(agent.current_state, AgentState.RUNNING)

    def test_agent_run_when_state_mismatch_does_not_raise_error_from_config(self):
        agent_config_copy = self.mock_agent_config.copy()
        agent_config_copy.raise_on_state_mismatch = False

        agent = MockAgent(agent_config_copy)
        self.assertEqual(agent.current_state, AgentState.INIT)

        agent.run()
        self.assertEqual(agent.current_state, AgentState.RUNNING)

    def test_agent_run_when_state_mismatch_raises_error_from_config(self):
        agent = MockAgent(self.mock_agent_config.copy())
        self.assertEqual(agent.current_state, AgentState.INIT)

        with self.assertRaises(AgentError):
            agent.run()

        self.assertEqual(agent.current_state, AgentState.ABORTED)

    def test_agent_teardown_async_when_teardown_raises_error(self):
        agent = MockAgentTeardownRaisesError(self.mock_agent_config.copy())
        self.assertEqual(agent.current_state, AgentState.INIT)

        t = agent.teardown_async()
        t.join()

        self.assertEqual(agent.current_state, AgentState.ERROR)
