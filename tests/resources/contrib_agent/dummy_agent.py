from ychaos.agents.agent import Agent, AgentConfig


class MyDummyAgentConfig(AgentConfig):
    name: str = "dummy_agent"
    description: str = "This is an dummy agent"


class MyDummyAgent(Agent):
    def __init__(self) -> None:
        print("in method: init")
        pass

    def monitor(self) -> None:
        print("in method: monitor")
        pass

    def setup(self) -> None:
        print("in method: setup")
        pass

    def run(self) -> None:
        print("in method: run")
        pass

    def teardown(self) -> None:
        print("in method: teardown")
        pass


AgentClass = MyDummyAgent
AgentConfigClass = MyDummyAgentConfig
