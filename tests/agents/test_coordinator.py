#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import time
from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase

from mockito import ANY, unstub, when

from ychaos.agents.agent import AgentMonitoringDataPoint, AgentState
from ychaos.agents.coordinator import Coordinator
from ychaos.testplan.attack import AttackMode
from ychaos.testplan.schema import TestPlan


class TestCoordinator(TestCase):
    def setUp(self) -> None:
        self.test_plans_directory = (
            Path(__file__).joinpath("../../resources/testplans").resolve()
        )
        self.test_plan = TestPlan.load_file(
            self.test_plans_directory.joinpath("valid/testplan4.yaml")
        )

        # Avoid slow UTs
        when(time).sleep(ANY).thenReturn(None)
        Coordinator.DEFAULT_DURATION = 1

    def tearDown(self) -> None:
        unstub()

    def test_configure_agent_in_test_plan_sequential_mode(self):
        test_plan = self.test_plan.copy()
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        self.assertEqual(len(configured_agents), len(test_plan.attack.agents))
        for i in range(len(configured_agents)):
            self.assertEqual(
                (
                    configured_agents[i].end_time - configured_agents[i].start_time
                ).seconds,
                getattr(
                    configured_agents[i].agent.config,
                    "duration",
                    Coordinator.DEFAULT_DURATION,
                ),
            )
            self.assertEqual(
                configured_agents[i].agent.config.name.upper(),
                test_plan.attack.agents[i].type.name,
            )

    def test_configure_agent_in_test_plan_concurrent_mode(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        self.assertEqual(len(configured_agents), len(test_plan.attack.agents))
        agents_with_same_start_delay = {0: [], 1: []}
        for i in range(len(configured_agents)):
            self.assertEqual(
                (
                    configured_agents[i].end_time - configured_agents[i].start_time
                ).seconds,
                getattr(
                    configured_agents[i].agent.config,
                    "duration",
                    Coordinator.DEFAULT_DURATION,
                ),
            )
            agents_with_same_start_delay[
                configured_agents[i].agent.config.start_delay
            ].append(configured_agents[i])
        self.assertFalse(coordinator.get_exit_status())

    def test_get_next_agent_for_attack(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        for configured_agent in configured_agents:
            while datetime.now(timezone.utc) <= coordinator.attack_end_time:
                agent = coordinator.get_next_agent_for_runnable()
                if agent:
                    self.assertEqual(id(configured_agent), id(agent))
                    break
            else:
                self.fail(
                    f"Failed to get Agent:{configured_agent.agent.config.name} for attack"
                )

    def test_get_next_agent_for_attack_agent_setup_step_failed(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        configured_agents[0].agent.advance_state(AgentState.SETUP)
        when(configured_agents[1].agent).setup().thenRaise(IOError())
        self.assertEqual(configured_agents[1].agent.current_state, AgentState.INIT)
        coordinator.configured_agents = coordinator.configured_agents[:2]
        for index, configured_agent in enumerate(configured_agents):
            while datetime.now(timezone.utc) <= coordinator.attack_end_time:
                if index == 0 or index == 1:
                    if coordinator.get_next_agent_for_runnable():
                        self.fail(msg="Test Failed")
                        break
                else:
                    break

        if not configured_agents[1].agent.exception.empty():
            self.assertIsInstance(configured_agents[1].agent.exception.get(), IOError)
        else:
            self.fail(msg="Missing Error in Agent")
        self.assertTrue(coordinator.get_exit_status())

    def test_check_for_failed_agents(self):
        test_plan = self.test_plan.copy()
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        when(configured_agents[0].agent).setup().thenRaise(IOError())
        self.assertFalse(coordinator.check_for_failed_agents())
        while datetime.now(timezone.utc) <= configured_agents[0].end_time:
            coordinator.get_next_agent_for_runnable()

        self.assertTrue(coordinator.check_for_failed_agents())
        self.assertTrue(coordinator.check_for_failed_agents(configured_agents[0].agent))
        self.assertFalse(
            coordinator.check_for_failed_agents(configured_agents[1].agent)
        )
        coordinator.configured_agents = []
        self.assertFalse(coordinator.check_for_failed_agents())

    def test_get_next_agent_for_teardown(self):
        test_plan = self.test_plan.copy()
        coordinator = Coordinator(test_plan)
        coordinator.configure_agent_in_test_plan()
        coordinator.configured_agents = coordinator.configured_agents[:2]
        self.assertFalse(coordinator.get_next_agent_for_teardown())
        coordinator.configured_agents[1].agent.advance_state(AgentState.RUNNING)
        while datetime.now(timezone.utc) <= coordinator.configured_agents[1].end_time:
            pass

        self.assertEqual(
            id(coordinator.get_next_agent_for_teardown()),
            id(coordinator.configured_agents[1]),
        )

    def test_stop_all_running_agents_in_sync(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        configured_agents[0].agent.advance_state(AgentState.SETUP)

        configured_agents[1].agent.advance_state(AgentState.ERROR)
        configured_agents[1].agent.exception.put(IOError("testing"))
        configured_agents[1].agent.status.put(
            AgentMonitoringDataPoint(
                data=dict(
                    testdata=1.4,
                ),
                state=AgentState.RUNNING,
            )
        )
        configured_agents[2].agent.setup()
        configured_agents[2].agent_start_thread = configured_agents[
            2
        ].agent.start_async()
        configured_agents[3].agent.setup()
        configured_agents[3].agent.start_async()
        configured_agents[3].agent_teardown_thread = configured_agents[
            3
        ].agent.teardown_async()
        configured_agents[3].agent_teardown_thread.join()
        configured_agents[3].agent.advance_state(AgentState.RUNNING)

        coordinator.stop_all_running_agents_in_sync()

        self.assertEqual(coordinator.exit_code, 1)

    def test_generate_attack_report(self):
        test_plan = self.test_plan.copy()
        coordinator = Coordinator(test_plan)
        configured_agents = coordinator.configure_agent_in_test_plan()
        configured_agents[0].agent.preserved_state.has_error = True
        configured_agents[1].agent.preserved_state.is_aborted = True
        result = coordinator.generate_attack_report()
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], str(coordinator.test_plan.id))
        self.assertEqual(result["mode"], coordinator.test_plan.attack.mode.value)
        self.assertEqual(result["start_time"], str(coordinator.attack_start_time))
        self.assertEqual(result["expected_end_time"], str(coordinator.attack_end_time))
        self.assertEqual(len(result["agents"]), len(coordinator.configured_agents))

        expected_agent_states = (
            AgentState.ERROR.name,
            AgentState.ABORTED.name,
            AgentState.INIT.name,
            AgentState.INIT.name,
        )
        for i in range(0, 4):
            self.assertEqual(result["agents"][i]["status"], expected_agent_states[i])

        report_agents = list(zip(result["agents"], coordinator.configured_agents))
        for report_agent in report_agents:
            self.assertEqual(
                report_agent[0]["end_time"],
                str(report_agent[1].end_time)
                if hasattr(report_agent[1].agent.config, "duration")
                else "NaN",
            )
            self.assertEqual(
                report_agent[0]["start_time"], str(report_agent[1].start_time)
            )
            self.assertEqual(
                report_agent[0]["agent_name"], report_agent[1].agent.config.name
            )

    def test_start_attack_successfully(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        test_plan.attack.agents = test_plan.attack.agents[-1:]
        coordinator = Coordinator(test_plan)
        coordinator.configure_agent_in_test_plan()
        coordinator.start_attack()
        self.assertFalse(coordinator.get_exit_status())
        report = coordinator.generate_attack_report()
        for agent in report["agents"]:
            self.assertEqual(agent["status"], AgentState.DONE.name)

    def test_start_attack_successfully_teardown(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        test_plan.attack.agents = test_plan.attack.agents[-1:]
        coordinator = Coordinator(test_plan)
        coordinator.configure_agent_in_test_plan()
        when(coordinator).get_next_agent_for_teardown().thenReturn(
            coordinator.configured_agents[0]
        ).thenReturn(None)
        coordinator.start_attack()
        self.assertFalse(coordinator.get_exit_status())
        report = coordinator.generate_attack_report()
        for agent in report["agents"]:
            self.assertEqual(agent["status"], AgentState.DONE.name)

    def test_start_attack_failed_test(self):
        test_plan = self.test_plan.copy()
        test_plan.attack.mode = AttackMode.CONCURRENT
        test_plan.attack.agents = test_plan.attack.agents[-1:]
        coordinator = Coordinator(test_plan)
        coordinator.configure_agent_in_test_plan()
        coordinator.configured_agents[-1].agent.exception.put(Exception("testing"))
        coordinator.start_attack()
        self.assertTrue(coordinator.get_exit_status())
        report = coordinator.generate_attack_report()
        self.assertEqual(report["agents"][0]["status"], AgentState.ERROR.name)

        self.assertEqual(len(coordinator.get_all_exceptions()), 1)
        self.assertIsInstance(coordinator.get_all_exceptions()[0], Exception)
