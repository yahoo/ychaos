#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import subprocess  # nosec
from queue import LifoQueue

from pydantic import Field

from ..agent import (
    Agent,
    AgentMonitoringDataPoint,
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
        description="The shell command to be executed", examples=["mkdir tempDir", "ls"]
    )


class Shell(Agent):
    def monitor(self) -> LifoQueue:
        super(Shell, self).monitor()

        self._status.put(
            AgentMonitoringDataPoint(data=dict(), state=self.current_state)
        )
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(Shell, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(Shell, self).run()

        subprocess.Popen(self.config.command, shell=True).wait()  # nosec

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(Shell, self).teardown()
