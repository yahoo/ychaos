from ychaos.agents.agent import Agent, AgentConfig
from ychaos.agents.utils.annotations import log_agent_lifecycle
from queue import LifoQueue
import os


class MyDummyAgentConfig(AgentConfig):
    name: str = "dummy_agent"
    description: str = "This is an dummy agent"


class MyDummyAgent(Agent):
    def __init__(self, config):
        assert isinstance(config, AgentConfig)
        super(MyDummyAgent, self).__init__(config)

    def monitor(self) -> LifoQueue:
        super(MyDummyAgent, self).monitor()
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(MyDummyAgent, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(MyDummyAgent, self).run()
        with open("/tmp/OK", "w") as f:
            f.write("This is a Dummy Agent")

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(MyDummyAgent, self).teardown()
        os.remove("/tmp/OK")


AgentClass = MyDummyAgent
AgentConfigClass = MyDummyAgentConfig
