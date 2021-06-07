#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from queue import LifoQueue
from unittest import TestCase

from ychaos.agents.agent import Agent, AgentConfig, AgentState
from ychaos.agents.contrib import ContribAgentConfig


class MockCommunityAgentConfig(AgentConfig):
    name = "mock_contrib_agent"


class MockCommunityAgent(Agent):
    def __init__(self, config: MockCommunityAgentConfig):
        super(MockCommunityAgent, self).__init__(config)
        assert self.current_state == AgentState.INIT

    def monitor(self) -> LifoQueue:
        super(MockCommunityAgent, self).monitor()

    def setup(self) -> None:
        super(MockCommunityAgent, self).setup()

    def run(self) -> None:
        super(MockCommunityAgent, self).run()

    def teardown(self) -> None:
        super(MockCommunityAgent, self).teardown()


class TestContribAgent(TestCase):
    def test_init_contrib_agent_calls_external_init(self):
        config = ContribAgentConfig(
            path=__file__,
            config=dict(),
            agent_class="MockCommunityAgent",
            agent_config_class="MockCommunityAgentConfig",
        )
        contrib_agent = config.get_agent()
        self.assertEqual(contrib_agent.current_state, AgentState.INIT)

    def test_external_agents_lifecycle(self):
        config = ContribAgentConfig(
            path=__file__,
            config=dict(),
            agent_class="MockCommunityAgent",
            agent_config_class="MockCommunityAgentConfig",
        )
        contrib_agent = config.get_agent()
        self.assertEqual(contrib_agent.current_state, AgentState.INIT)

        contrib_agent.setup()
        self.assertEqual(contrib_agent.current_state, AgentState.SETUP)

        contrib_agent.run()
        self.assertEqual(contrib_agent.current_state, AgentState.RUNNING)

        contrib_agent.teardown()
        self.assertEqual(contrib_agent.current_state, AgentState.TEARDOWN)

        contrib_agent.monitor()  # coverage
