#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import functools
import time
from queue import LifoQueue

from ..agent import Agent, AgentConfig, TimedAgentConfig
from ..utils.annotations import log_agent_lifecycle

NoOpAgentConfig = functools.partial(AgentConfig, name="no_op")


class NoOpAgent(Agent):
    """
    An agent that does nothing
    """

    def __init__(self, config):
        assert isinstance(config, AgentConfig)
        super(NoOpAgent, self).__init__(config)

    def monitor(self) -> LifoQueue:  # pragma: no cover
        super(NoOpAgent, self).monitor()
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(NoOpAgent, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(NoOpAgent, self).run()

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(NoOpAgent, self).teardown()


NoOpTimedAgentConfig = functools.partial(TimedAgentConfig, name="no_op_timed")


class NoOpTimedAgent(NoOpAgent):  # pragma: no cover
    """
    A time constrained agent that does nothing for `duration` seconds.
    """

    def __init__(self, config):
        assert isinstance(config, TimedAgentConfig)
        super(NoOpTimedAgent, self).__init__(config)

    @log_agent_lifecycle
    def run(self) -> None:
        super(NoOpTimedAgent, self).run()
        time.sleep(self.config.duration)
