#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import math
import shutil
from pathlib import Path
from queue import LifoQueue

from pydantic import Field

from ..agent import (
    Agent,
    AgentMonitoringDataPoint,
    AgentPriority,
    TimedAgentConfig,
)
from ..utils.annotations import log_agent_lifecycle


class DiskFillConfig(TimedAgentConfig):
    """
    Defines the Disk Fill configuration to consume the disk space. The framework will
    fill the disk space of a directory defined in `partition` and fill only a percentage of available
    space, as defined in the `partition_pct` attribute. By default,
    `partition_pct` is set to 100, implying the complete disk space of that partition will be filled.
    """

    name = "disk_fill"
    description = "This agent fills up disk space."

    priority = AgentPriority.MODERATE_PRIORITY

    partition: Path = Field(
        description="The Filepath of directory or partition to fill",
        default=Path("/etc/"),
        examples=["/etc/tmp", "/home/tmpuser"],
    )

    partition_pct: float = Field(
        default=80,
        description=(
            "Percentage of the disk partition to fill"
            "This will fill a percentage of the disk space on the partition"
        ),
        gt=0,
        le=100,
    )

    max_file_size: int = Field(
        default=(1024 * 1024 * 1024 * 20),  # Max file size is 20GB,
        description=(
            "Maximum size of each disk fill file. If the size to be filled exceeds this max file size, multiple"
            "disk fill files will be used"
        ),
        gt=1024,
    )

    disk_fill_dir: str = Field(
        default="ychaos_diskfill",
        description=(
            "Name of the temporary directory in which to store the disk fill files."
            "This will be the path relative to the partition to fill"
        ),
    )

    def effective_disk_to_fill(self) -> int:
        """
        Calculates the disk space that needs to be filled based on the available space in the partition and
        the percentage of partition to fill partition_pct.
        Returns:
            disk space to fill in given partition.
        """
        stat = shutil.disk_usage(self.partition)
        partition_size_available = stat.free
        return math.floor(self.partition_pct / 100 * partition_size_available)


class DiskFill(Agent):
    def monitor(self) -> LifoQueue:
        super(DiskFill, self).monitor()
        available_space = shutil.disk_usage(self.config.partition).free

        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(
                    disk_space_to_fill=self.config.effective_disk_to_fill(),
                    disk_free_space=available_space,
                ),
                state=self.current_state,
            )
        )
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(DiskFill, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(DiskFill, self).run()
        size = self.config.effective_disk_to_fill()
        if size <= 0:
            return
        disk_fill_dir = Path(self.config.partition / self.config.disk_fill_dir)
        disk_fill_dir.mkdir(parents=True, exist_ok=True)

        space_remaining = size
        index = 0
        while space_remaining > 0:
            if self.stop_async_run:
                break
            tmp = space_remaining
            cur_file_size = self.config.max_file_size
            space_remaining -= self.config.max_file_size
            if space_remaining <= 0:
                cur_file_size = tmp
            with open(disk_fill_dir / f"filler{index}.txt", "wb") as f:
                f.seek(cur_file_size - 1)
                f.write(b"\0")
            index += 1

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(DiskFill, self).teardown()
        tmp_dir = self.config.partition / self.config.disk_fill_dir
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
