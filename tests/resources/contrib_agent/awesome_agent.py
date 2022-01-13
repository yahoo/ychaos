from ychaos.agents.agent import Agent, AgentConfig
from ychaos.agents.utils.annotations import log_agent_lifecycle


class AwesomeAgentConfig(AgentConfig):
    name: str = "awesomeagent"
    description: str = "This is an dummy agent"


class MyAwesomeAgent(Agent):
    @log_agent_lifecycle
    def __init__(self, config) -> None:
        print("in method: init")
        assert isinstance(config, AgentConfig)
        super(MyAwesomeAgent, self).__init__(config)

    @log_agent_lifecycle
    def monitor(self) -> None:
        print("in method: monitor")
        super(MyAwesomeAgent, self).monitor()
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        print("in method: setup")
        super(MyAwesomeAgent, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        print("in method: run")
        super(MyAwesomeAgent, self).run()

    @log_agent_lifecycle
    def teardown(self) -> None:
        print("in method: teardown")
        super(MyAwesomeAgent, self).teardown()


AgentClass = MyAwesomeAgent
AgentConfigClass = AwesomeAgentConfig
