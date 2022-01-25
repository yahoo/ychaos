#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from queue import LifoQueue
import os

from pydantic import Field

from ..agent import (
    Agent,
    AgentPriority,
    TimedAgentConfig,
)
from ..utils.annotations import log_agent_lifecycle


class ShellConfig(TimedAgentConfig):
    """
    Defines the Shell configuration to run shell command.
    """

    name = "shell"
    description = "shell agent"

    priority = AgentPriority.MODERATE_PRIORITY

    command: str = Field(
        description="The shell command to be executed",
        examples=["mkdir tempDir", "ls"]
    )


class Shell(Agent):
    def monitor(self) -> LifoQueue:
        super(Shell, self).monitor()

        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(Shell, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(Shell, self).run()

        os.system(self.config.command)

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(Shell, self).teardown()
