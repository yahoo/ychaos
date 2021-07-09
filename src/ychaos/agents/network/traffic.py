#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import shutil
from pathlib import Path
from queue import LifoQueue
from stat import S_IREAD, S_IRGRP, S_IROTH
from tempfile import NamedTemporaryFile
from typing import List, Optional

from pydantic import Field, validate_arguments

from ..agent import Agent, TimedAgentConfig
from ..utils.annotations import log_agent_lifecycle


class TrafficBlockConfig(TimedAgentConfig):
    name = "traffic_block"
    description = "This agent modifies the the hosts /etc/hosts file to block traffic to certain hostnames"

    is_sudo = True

    hostsfile: Path = Field(
        description="The Filepath of hosts file", default=Path("/etc/hosts")
    )

    backup_hostsfile: Optional[Path] = Field(
        description="The filepath to store backup of hosts file. By default, the agent will create temporary file",
        default=None,
    )

    hosts: List[str] = Field(
        description="List of destination outbound hostnames to block",
        default=list(),
        examples=[["yahoo.com", "google.com"]],
    )


class TrafficBlock(Agent):
    LOCALHOST = "127.0.0.1"
    permission = int()

    @validate_arguments
    def __init__(self, config: TrafficBlockConfig):
        super(TrafficBlock, self).__init__(config)

        if config.backup_hostsfile is None:
            config.backup_hostsfile = Path(
                NamedTemporaryFile(mode="w+", delete=False).name
            )

    def monitor(self) -> LifoQueue:
        super(TrafficBlock, self).monitor()
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(TrafficBlock, self).setup()

        shutil.copy(self.config.hostsfile, self.config.backup_hostsfile)

        # Makes the Backup File as Read Only. This is a protection from
        # backup file getting deleted/modified accidentally. The file can still
        # be modified with root access.
        self.permission = Path(self.config.backup_hostsfile).lstat().st_mode
        Path(self.config.backup_hostsfile).chmod(S_IREAD | S_IRGRP | S_IROTH)

    @log_agent_lifecycle
    def run(self) -> None:
        super(TrafficBlock, self).run()
        with open(self.config.hostsfile, "a") as hosts_file:
            hosts_file.write("\n")
            for host in self.config.hosts:
                hosts_file.write(f"{self.LOCALHOST}\t{host}\n")

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(TrafficBlock, self).teardown()

        # Restore the permissions for the file and move it to original location
        self.config.backup_hostsfile.chmod(self.permission)
        shutil.copy(self.config.backup_hostsfile, self.config.hostsfile)

        # Delete the backup hostsfile
        self.config.backup_hostsfile.unlink()
