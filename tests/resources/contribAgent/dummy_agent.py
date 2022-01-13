from ychaos.agents.agent import Agent, AgentConfig
from ychaos.agents.utils.annotations import log_agent_lifecycle
from queue import LifoQueue
import os


class MyDummyAgentConfig(AgentConfig):
    name: str = "dummy_agent"
    description: str = "This is an dummy agent"


class MyDummyAgent(Agent):
    def __init__(self) -> None:
        pass

    def monitor(self) -> None:
        pass

    def setup(self) -> None:
        pass

    def run(self) -> None:
        pass

    def teardown(self) -> None:
        pass


AgentClass = MyDummyAgent
AgentConfigClass = MyDummyAgentConfig
