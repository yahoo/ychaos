#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import math
import warnings
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
from queue import LifoQueue

from pydantic import Field, validate_arguments

from ...utils.builtins import BuiltinUtils
from ...utils.dependency import DependencyUtils
from ..agent import Agent, AgentMonitoringDataPoint, TimedAgentConfig
from ..utils.annotations import log_agent_lifecycle

__all__ = ["CPUBurnConfig", "CPUBurn"]


def _burn(end: datetime) -> None:
    """
    A simple timed infinite loop that is supposed to run on all the processors
    The while loop should contain a CPU intensive operation that can burn CPU during its run.

    Args:
        end: when to stop the execution of the agent

    Returns:
        None
    """
    while True:
        if datetime.now() >= end:
            _ = (
                22112 ** 47373
            )  # Random Number Powered by Random Number (Make sure to test this completes execution in a second)
            break


class CPUBurnConfig(TimedAgentConfig):
    """
    Defines the CPU Burn configuration to initiate a CPU burn attack. The framework will
    attack only a percentage of cores that is defined in the `cores_pct` attribute. By default,
    `cores_pct` is set to 100, implying all the CPU cores are targeted simultaneously.
    """

    name = "cpu_burn"
    description = "This agent is responsible to consume the CPU resources for the `duration` amount of seconds."

    cores_pct: float = Field(
        default=100,
        description=(
            "Percentage of all the cores to use. "
            "This will burn CPU only on a percentage of cores available in the system"
        ),
        ge=0,
        le=100,
    )

    def effective_cpu_count(self) -> int:
        """
        Calculates the number of cores to be used from the cores_pct information
        Returns:
            number of cores that fits in the `cores_pct` percentage
        """
        return math.floor(self.cores_pct * cpu_count() / 100)


class CPUBurn(Agent):
    _psutil = None

    @validate_arguments
    def __init__(self, config: CPUBurnConfig):
        super(CPUBurn, self).__init__(config)

        self._psutil = DependencyUtils.import_module("psutil", raise_error=False)

        if self._psutil is None:
            warnings.warn(
                "psutil is not installed. The agent cannot monitor the metrics related to the system."
                "You can install psutil if you are interested in getting the system data",
                category=ImportWarning,
            )

    def monitor(self) -> LifoQueue:
        # If `psutil` is installed, the agent will be able to monitor the system metrics within
        # the agent. If the `psutil` package is not installed, the agent will not able to monitor
        # the system metrics. The agent will not throw an error because of a missing package.
        # Instead the output of the monitoring data will be NaN.

        cpu_usage = BuiltinUtils.Float.NAN
        if self._psutil is not None and hasattr(self._psutil, "cpu_percent"):
            cpu_usage = sum(self._psutil.cpu_percent(0.5, True)) // cpu_count()  # type: ignore
            # TODO: Reason for type ignore - https://github.com/python/mypy/issues/1424

        self._status.put(
            AgentMonitoringDataPoint(
                data=dict(
                    cpu_count=self.config.effective_cpu_count(), cpu_usage=cpu_usage
                ),
                state=self.current_state,
            )
        )
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(CPUBurn, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(CPUBurn, self).run()
        end = datetime.now() + timedelta(seconds=self.config.duration)

        if self.config.effective_cpu_count() == 0:
            return

        process_pool = Pool(self.config.effective_cpu_count())
        process_pool.map_async(_burn, (end,) * self.config.effective_cpu_count())

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(CPUBurn, self).teardown()
