#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import subprocess  # nosec
from pathlib import Path
from queue import LifoQueue
from shlex import split
from typing import Optional

from pydantic import Field

from ..agent import (
    Agent,
    AgentMonitoringDataPoint,
    AgentPriority,
    TimedAgentConfig,
)
from ..exceptions import AgentError
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

    ignore_error: bool = Field(
        description="Ignore non-zero return code from shell command", default=False
    )

    env: dict = Field(description="Used to set the environment variables", default=None)

    cwd: Optional[Path] = Field(
        description="Set working directory before running shell command",
        examples=["/etc/tmp"],
        default=None,
    )

    use_shell: bool = Field(
        description="Sets whether to set shell to true or false",
        default=False,
    )


class Shell(Agent):
    stdout: Optional[bytes]
    stderr: Optional[bytes]
    rc: Optional[int]

    def monitor(self) -> LifoQueue:
        super(Shell, self).monitor()

        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(stdout=self.stdout, stderr=self.stderr, rc=self.rc),
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
        )  # nosec

        self.stdout, self.stderr = process.communicate(timeout=self.config.duration)
        self.rc = process.returncode

        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(
                    stdout=self.stdout, stderr=self.stderr, rc=process.returncode
                ),
                state=self.current_state,
            )
        )

        if process.returncode != 0 and not self.config.ignore_error:
            raise AgentError("Error Occurred while running shell command")

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(Shell, self).teardown()
