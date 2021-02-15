#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import time
from queue import LifoQueue

from vzmi.ychaos.agents.agent import Agent, AgentConfig, TimedAgentConfig


class NoOpAgent(Agent):  # pragma: no cover
    """
    An agent that does nothing
    """

    def __init__(self, config):
        assert isinstance(config, AgentConfig)
        super(NoOpAgent, self).__init__(config)

    def monitor(self) -> LifoQueue:
        super(NoOpAgent, self).monitor()
        return self._status
        pass

    def setup(self) -> None:
        super(NoOpAgent, self).setup()
        pass

    def run(self) -> None:
        super(NoOpAgent, self).run()
        pass

    def teardown(self) -> None:
        super(NoOpAgent, self).teardown()
        pass


class NoOpTimedAgent(NoOpAgent):  # pragma: no cover
    """
    A time constrained agent that does nothing for `duration` seconds.
    """

    def __init__(self, config):
        assert isinstance(config, TimedAgentConfig)
        super(NoOpTimedAgent, self).__init__(config)

    def run(self) -> None:
        super(NoOpTimedAgent, self).run()
        time.sleep(self.config.duration)
