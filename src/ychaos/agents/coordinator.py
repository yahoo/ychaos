#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import os
from datetime import datetime, timedelta, timezone
from logging import Logger
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..app_logger import AppLogger
from ..testplan.attack import AttackMode
from ..testplan.schema import TestPlan
from ..utils.hooks import EventHook
from .agent import Agent, AgentState


class ConfiguredAgent:
    """
    Class to hold the configured Agent
    """

    def __init__(
        self, agent: Agent, start_time: Optional[datetime], end_time: Optional[datetime]
    ):
        """
        Initialize ConfiguredAgent
        Args:
            agent: Agent object
            start_time: Agent execution start time
            end_time: Agent execution end time
        """
        self.agent: Agent = agent
        self.start_time = start_time
        self.end_time = end_time
        self.agent_start_thread: Optional[Thread] = None
        self.agent_teardown_thread: Optional[Thread] = None


class Coordinator(EventHook):
    """
    The coordinator is responsible for setting up the chaos agents,
    running the agents and monitor the agent currently being run. It also
    takes care of completing the attack by bringing back to the system to its original
    state.

    ## Coordinator Event Hooks

    === "on_attack_start"
        called when attack is started on the host
        ```python
            def callable_hook(): ...
        ```

    === "on_attack_completed"
        called when attack is completed
        ```python
            def callable_hook(): ...
        ```

    === "on_each_agent_start"
        called when a Agent start executing
        ```python
            def callable_hook(agent_name: str): ...
        ```

    === "on_each_agent_teardown"
        called when a Agent Teardown is started
        ```python
            def callable_hook(agent_name: str): ...
        ```

    === "on_each_agent_stop"
        called when a Agent completes its execution and teardown step
        ```python
            def callable_hook(agent_name: str): ...
        ```
    ---
    """

    __hook_events__ = (
        "on_attack_start",
        "on_attack_completed",
        "on_each_agent_start",
        "on_each_agent_teardown",
        "on_each_agent_stop",
    )
    DEFAULT_DURATION = 3
    THREAD_TIMEOUT = 300

    def __init__(self, test_plan: TestPlan):
        super(Coordinator, self).__init__()
        self.test_plan: TestPlan = test_plan
        self.configured_agents: List[ConfiguredAgent] = []
        self.attack_end_time: Optional[datetime] = None
        self.attack_start_time: Optional[datetime] = None
        self.exit_code = 0
        self.log: Logger = AppLogger.get_logger(__name__)

    def configure_agent_in_test_plan(self) -> List[ConfiguredAgent]:
        """
        Configure all the Agents as specified in the test plan
        Returns:
            list of configured agents
        """

        for agent in self.test_plan.attack.agents:
            next_start_time = datetime.now(timezone.utc)
            configured_agent: Agent

            if self.test_plan.attack.mode.value == AttackMode.SEQUENTIAL.value and len(
                self.configured_agents
            ):
                assert self.configured_agents[-1].end_time is not None
                next_start_time = self.configured_agents[-1].end_time

            agent_config = agent.type.metadata.schema(**agent.config)  # type: ignore
            configured_agent = agent.type.metadata.agent_defn(agent_config)  # type: ignore
            start_time: datetime = next_start_time + timedelta(
                seconds=configured_agent.config.start_delay
            )
            end_time: datetime = start_time + timedelta(
                seconds=getattr(
                    configured_agent.config, "duration", self.DEFAULT_DURATION
                )
            )

            self.configured_agents.append(
                ConfiguredAgent(
                    configured_agent, start_time=start_time, end_time=end_time
                )
            )
        if self.test_plan.attack.mode.value != AttackMode.SEQUENTIAL.value:
            self.configured_agents.sort(
                key=lambda current_agent: current_agent.end_time  # type: ignore
            )
            self.attack_end_time = self.configured_agents[-1].end_time
            self.configured_agents.sort(
                key=lambda current_agent: current_agent.start_time  # type: ignore
            )
            self.attack_start_time = self.configured_agents[0].start_time
        else:
            self.attack_start_time = self.configured_agents[0].start_time
            self.attack_end_time = self.configured_agents[-1].end_time
        return self.configured_agents

    def get_exit_status(self) -> int:
        return self.exit_code

    def get_next_agent_for_attack(self) -> Optional[ConfiguredAgent]:
        """
        Get the next Agent for execution as configured in test plan
        Returns:
            An Agent or None
        """
        current_time: datetime = datetime.now(timezone.utc)
        for configured_agent in self.configured_agents:
            assert configured_agent.start_time is not None
            assert configured_agent.end_time is not None
            if (
                configured_agent.agent.current_state == AgentState.INIT
                and current_time > configured_agent.start_time
            ):
                try:
                    configured_agent.agent.setup()
                except Exception as e:
                    configured_agent.agent.exception.put(e)
                    configured_agent.agent.advance_state(AgentState.ERROR)
                    self.exit_code = 1
                    break
                else:
                    return configured_agent
        return None

    def get_next_agent_for_teardown(self) -> Optional[ConfiguredAgent]:
        """
        Get the next Agent for teardown as configured in test plan
        Returns:
            An Agent or None
        """
        current_time: datetime = datetime.now(timezone.utc)
        for configured_agent in self.configured_agents:
            assert configured_agent.start_time is not None
            assert configured_agent.end_time is not None
            if (
                configured_agent.agent.current_state == AgentState.RUNNING
                and current_time > configured_agent.end_time
                and not configured_agent.agent_teardown_thread
            ):
                return configured_agent
        return None

    def check_for_failed_agents(self, agent: Optional[Agent] = None) -> bool:
        """
        check if any Agent has error
        Args:
            agent: check only this Agent has error

        Returns:
            True if Agent has error else False
        """
        for configured_agent in self.configured_agents:
            if agent and agent != configured_agent.agent:
                continue
            if (
                configured_agent.agent.current_state == AgentState.ERROR
                or not configured_agent.agent.exception.empty()
            ):
                configured_agent.agent.advance_state(AgentState.ERROR)
                configured_agent.agent.preserved_state.has_error = True
                return True
        return False

    def stop_all_running_agents_in_sync(self):
        """
        waits for all agents to complete teardown step
        """
        for configured_agent in self.configured_agents:
            if (
                configured_agent.agent.current_state == AgentState.SETUP
                or configured_agent.agent.current_state == AgentState.INIT
            ):
                configured_agent.agent.advance_state(AgentState.SKIPPED)
            elif configured_agent.agent.current_state == AgentState.ERROR:
                configured_agent.agent.preserved_state.has_error = True
                self.exit_code = 1
            elif (
                configured_agent.agent_start_thread
                and configured_agent.agent_start_thread.is_alive()
                and self.get_exit_status()
            ):
                configured_agent.agent.preserved_state.is_aborted = True
                configured_agent.agent.advance_state(AgentState.ABORTED)

            if (
                not configured_agent.agent.current_state == AgentState.DONE
                and not configured_agent.agent.current_state == AgentState.SKIPPED
            ):
                try:
                    if configured_agent.agent_teardown_thread:
                        configured_agent.agent_teardown_thread.join(
                            timeout=self.THREAD_TIMEOUT
                        )
                    else:
                        configured_agent.agent_teardown_thread = (
                            configured_agent.agent.teardown_async()
                        )
                        self.execute_hooks(
                            "on_each_agent_teardown",
                            configured_agent.agent.config.name,
                        )
                        configured_agent.agent_teardown_thread.join(
                            timeout=self.THREAD_TIMEOUT
                        )
                    if (
                        configured_agent.agent_teardown_thread
                        and configured_agent.agent_teardown_thread.is_alive()
                    ):  # pragma: no cover
                        raise Exception(
                            f"Agent: {configured_agent.agent.config.name} Teardown step failed to complete in {self.THREAD_TIMEOUT}"
                        )
                    if self.check_for_failed_agents(configured_agent.agent):
                        raise configured_agent.agent.exception.get()
                except Exception as e:
                    self.exit_code = 1
                    configured_agent.agent.exception.put(e)
                    configured_agent.agent.advance_state(AgentState.ERROR)
                    configured_agent.agent.preserved_state.has_error = True
            self.execute_hooks(
                "on_each_agent_stop",
                configured_agent.agent.config.name,
            )

            temp_exception_queue = Queue()
            while not configured_agent.agent.exception.empty():  # print all exceptions
                error = configured_agent.agent.exception.get()
                temp_exception_queue.put(error)
                self.log.error(
                    f"Error occurred for the Agent={configured_agent.agent.config.name}",
                    exc_info=error,
                )
            configured_agent.agent.exception = temp_exception_queue

    def get_all_exceptions(self) -> list:
        """
        Get all the Exceptions occurred during the attack
        Returns:
            list of Exceptions

        """
        all_exceptions = []
        for configured_agent in self.configured_agents:
            temp_exception_queue: Queue = Queue()
            while not configured_agent.agent.exception.empty():
                e = configured_agent.agent.exception.get()
                temp_exception_queue.put(e)
                all_exceptions.append(e)
            configured_agent.agent.exception = temp_exception_queue
        return all_exceptions

    def generate_attack_report(self) -> Dict:
        """
        Generates attack report
        """

        class AgentStatus(BaseModel):
            agent_name: str
            start_time: str
            end_time: str
            status: str

        class AttackReport(BaseModel):
            """
            Attack Report Structure
            """

            id: str
            host: str
            start_time: str
            expected_end_time: str
            mode: str
            agents: List[AgentStatus]

        report: AttackReport = AttackReport(
            id=str(self.test_plan.id),
            host=os.uname()[1],
            start_time=str(self.attack_start_time),
            expected_end_time=str(self.attack_end_time),
            mode=self.test_plan.attack.mode.value,
            agents=[],
        )

        for configured_agent in self.configured_agents:
            agent = dict()
            agent["agent_name"] = configured_agent.agent.config.name
            agent["start_time"] = str(configured_agent.start_time)
            if hasattr(configured_agent.agent.config, "duration"):
                agent["end_time"] = str(configured_agent.end_time)
            else:
                agent["end_time"] = "NaN"
            if configured_agent.agent.preserved_state.has_error:
                agent["status"] = AgentState.ERROR.name
                self.exit_code = 1
            elif configured_agent.agent.preserved_state.is_aborted:
                agent["status"] = AgentState.ABORTED.name
            else:
                agent["status"] = configured_agent.agent.current_state.name
            report.agents.append(AgentStatus(**agent))
        return report.dict()

    def start_attack(self) -> int:
        """
        Performs the attack as configured in testplan
        Returns:
            attack status - 0 if successful else 1
        """
        self.log.info("Attack started")
        self.execute_hooks("on_attack_start")
        assert self.attack_end_time is not None
        assert self.configured_agents is not None
        while datetime.now(timezone.utc) <= self.attack_end_time:
            current_agent = self.get_next_agent_for_attack()
            if current_agent:
                current_agent.agent_start_thread = current_agent.agent.start_async()
                self.execute_hooks(
                    "on_each_agent_start",
                    current_agent.agent.config.name,
                )

            current_agent = self.get_next_agent_for_teardown()
            if current_agent:
                current_agent.agent_teardown_thread = (
                    current_agent.agent.teardown_async()
                )
                self.execute_hooks(
                    "on_each_agent_teardown",
                    current_agent.agent.config.name,
                )

            sleep(1)

            if self.check_for_failed_agents():
                self.exit_code = 1
                break

        self.stop_all_running_agents_in_sync()

        if self.exit_code:
            self.log.info("Attack failed")
        else:
            self.log.info("Attack Completed")
        self.execute_hooks("on_attack_completed")
        return self.exit_code
