#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import subprocess  # nosec
from pathlib import Path
from queue import LifoQueue
from shlex import split

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
    description = "runs a shell command provided by the user"

    priority = AgentPriority.MODERATE_PRIORITY

    command: str = Field(
        description="The shell command to be executed", examples=["mkdir tempDir", "ls"]
    )

    timeout: int = Field(
        description="Time in s after which shell command execution will be terminated. This is required to avoid "
        "indefinite wait",
        default=10,
    )

    ignore_error: bool = Field(
        description="Ignore non-zero return code from shell command", default=False
    )

    env: dict = Field(description="Used to set the environment variables", default=None)

    cwd: Path = Field(
        description="Set working directory before running shell command",
        examples=["/etc/tmp"],
        default=None,
    )

    user: str = Field(
        description="Set the user before running shell command", default=None
    )

    use_shell: bool = Field(
        description="Sets whether to set shell to true or false",
        default=False,
    )


class Shell(Agent):
    stdout = ""
    stderr = ""

    def monitor(self) -> LifoQueue:
        super(Shell, self).monitor()

        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(stdout=self.stdout, stderr=self.stderr),
                state=self.current_state,
            )
        )
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(Shell, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(Shell, self).run()

        remote_command = split(self.config.command)
        process = subprocess.Popen(  # type: ignore
            remote_command,
            shell=self.config.use_shell,  # nosec
            stdin=subprocess.PIPE,
            cwd=self.config.cwd,
            env=self.config.env,
            user=self.config.user,
        )  # nosec
        self.stdout, self.stderr = process.communicate(timeout=self.config.timeout)

        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(stdout=self.stdout, stderr=self.stderr),
                state=self.current_state,
            )
        )

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(Shell, self).teardown()
