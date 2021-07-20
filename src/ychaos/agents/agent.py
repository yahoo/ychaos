#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import os
import warnings
from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum
from queue import LifoQueue, Queue
from threading import Thread
from types import SimpleNamespace
from typing import Any, Dict, Tuple

from pydantic import BaseModel, Field

from ..utils.builtins import BuiltinUtils
from .exceptions import AgentError


class AgentState(IntEnum):
    SKIPPED = -3
    ABORTED = -2
    ERROR = -1
    UNDEFINED = 0
    INIT = 1
    SETUP = 2
    RUNNING = 3
    COMPLETED = 4
    TEARDOWN = 5
    DONE = 6


class AgentPriority(IntEnum):
    VERY_HIGH_PRIORITY = 0
    HIGH_PRIORITY = 1
    MODERATE_PRIORITY = 2
    LOW_PRIORITY = 3
    VERY_LOW_PRIORITY = 4
    UNDEFINED_PRIORITY = -1


class AgentMonitoringDataPoint(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(
        ..., description="Data from the agent at `timestamp` instant"
    )
    state: AgentState = Field(
        description="The state of the agent at `timestamp` instant"
    )


class AgentConfig(BaseModel):
    """
    The configuration of the agent that is to be run. This is the base configuration
    for any agent. Custom configuration attributes can be added to individual agent by inheriting
    this model.
    """

    name: str = Field(..., description="A one word identifier for the Agent.")
    description: str = Field(
        default="An awesome YChaos agent.",
        description="Multiline description of the agent in consideration",
    )
    priority: AgentPriority = Field(
        default=AgentPriority.UNDEFINED_PRIORITY,
        description="A priority assigned to the agent.",
    )

    # Runner configurations (Advanced configuration parameters)
    is_sudo: bool = Field(
        default=False,
        description="Setting this to true, requires the agent to run as root.",
    )

    # Be very careful when setting this key to False.
    # If you are aware of what you are doing, then go ahead.
    raise_on_state_mismatch: bool = Field(
        default=True, description="Raise error on state mismatch"
    )

    start_delay: int = Field(
        default=10, description="Give a delay of few seconds before running this agent"
    )

    def get_agent(self):
        """
        The Fallback factory method to use where the Agent
        instance depends on the configuration

        Returns:
            An agent subclass of Agent
        """
        pass


class TimedAgentConfig(AgentConfig):
    """
    The configuration of the agent which is constrained by a duration. This configuration
    is used for agents that are supposed to run for a particular amount of time before going
    to teardown state.
    """

    duration: int = Field(
        default=300,
        description="The duration for which this agent should run",
    )


class Agent(ABC):
    """
    An agent is an attack module that is configured to cause some kind of chaos on
    the target. A very simple of agent is the CPU Burn agent that is responsible
    for consuming CPU resources during the time interval its run.

    Each agent takes in one configuration object that is a subclass of AgentConfig.

    The agents have a lifecycle defined in `AgentState` each of them indicating
    the state in which the agent is currently in. The agent is advanced to the next state before
    executing any of the lifecycle methods.
    """

    def __init__(self, config):
        """
        Initialize an agent with a configuration

        Raises:
            InsufficientPermissionError: When the agent is configured to be sudo, but the agent is not run as root.

        Args:
            config: Agent configuration.
        """
        self.config = config

        self._runner = Thread(target=self.__run_exc_wrapper, name=config.name)
        self._stopper = Thread(
            target=self.__teardown_exc_wrapper, name=config.name + "_teardown"
        )
        self.stop_async_run: bool = False  # can be used as a flag to stop the attack and return from `run` method

        self.exception = Queue(-1)

        self._status = LifoQueue()
        self._state_history = list()

        self.preserved_state = SimpleNamespace(has_error=False, is_aborted=False)
        self.advance_state(AgentState.INIT)

    @abstractmethod
    def monitor(self) -> LifoQueue:  # pragma: no cover
        """
        Defines the implementation to monitor some stats for this agent and return a queue of
        the status

        Returns:
            A Queue of the status for this agent.
        """
        pass

    @abstractmethod
    def setup(self) -> None:
        """
        Defines the setup method. Used to set up the resources
        required for the agent. This is usually called before start

        Returns:
            None
        """
        self.advance_state(AgentState.SETUP)

    @abstractmethod
    def run(self) -> None:
        """
        Define what the agent does for the attack. Calling this method will block the calling thread.
        Caller has to take responsibility of updating the state of the agent once it is done.
        Use `start` or `start_async` for a better usage.

        Raises:
            AgentError: if `config.error_on_state_mismatch` is True and current state is not SETUP

        Returns:
            None
        """
        if self.current_state != AgentState.SETUP:
            if self.config.raise_on_state_mismatch:
                self.advance_state(AgentState.ABORTED)
                raise AgentError("Agent state is not in SETUP state. Bailing out")

            warnings.warn(
                "Agent is currently not in the SETUP state. Proceeding anyway"
            )

        if not self.is_runnable():
            raise AgentError("Agent not in executable state. Bailing out")
        self.advance_state(AgentState.RUNNING)

    def start(
        self,
        coro=BuiltinUtils.pass_coroutine,
        args: Tuple[Any, ...] = tuple(),
        interval=None,
    ) -> None:
        """
        A blocking start call. This method waits for the agent process to complete/exit.
        Calls a `coro` coroutine every `interval` seconds
        Also sets the agent state on COMPLETED/ERROR.
        Use `start_async()` method for the runner thread to run in background

        Args:
            coro: A function to call every `interval` seconds when the _runner is alive
            args: Arguments
            interval: Interval between 2 coroutine calls

        Returns:
            None
        """
        self._runner.start()
        while self._runner.is_alive():
            coro(*args)
            self._runner.join(interval)

        if self.exception.empty():
            self.advance_state(AgentState.COMPLETED)
        else:
            self.advance_state(AgentState.ERROR)

    def start_async(self) -> Thread:  # pragma: no cover
        """
        Unblocking call to start the run method. It is the responsibility of the
        caller to update the agent with its state, handle exceptions, etc.
        """
        self._runner.start()
        return self._runner

    def teardown_async(self) -> Thread:  # pragma: no cover
        """
        Non blocking call to start the teardown method. The caller takes full responsibility of handing

        Returns:
            teardown_async Thread instance
        """
        self._stopper.start()
        return self._stopper

    @abstractmethod
    def teardown(self) -> None:
        """
        This is called once the execute method is done to ensure a rollback is done
        to the state the agent entered.It wait for start_async thread to stop if its alive.

        Returns:
            None
        """
        self.advance_state(AgentState.TEARDOWN)
        self.stop_async_run = True
        if self._runner.is_alive():
            self._runner.join()

    def is_runnable(self) -> bool:
        """
        Fail Fast approach to find if the agent will be able to proceed to the next step.
        It is advised to run this method before running, start, run or start_async to
        avoid any mishaps in testing.

        Returns:
            True if able to proceed, False otherwise
        """
        if self.current_state < 0:
            return False
        if not self.exception.empty():
            return False
        if self.config.is_sudo and os.geteuid() != 0:
            return False

        return True

    def advance_state(self, state: AgentState):
        if self._state_history and self._state_history[-1] == state:
            return
        self._state_history.append(state)

    @property
    def current_state(self) -> AgentState:
        """
        Gets the current state of the agent.

        Returns:
            current state
        """
        if not self._state_history:
            # Never possible
            self._state_history = list()
            self.advance_state(AgentState.UNDEFINED)
        return self._state_history[-1]

    def __run_exc_wrapper(self):
        try:
            self.run()
        except Exception as e:
            self.exception.put(e)
            self.advance_state(AgentState.ERROR)

    def __teardown_exc_wrapper(self):
        try:
            self.teardown()
            self.advance_state(AgentState.DONE)
        except Exception as e:
            self.exception.put(e)
            self.advance_state(AgentState.ERROR)
