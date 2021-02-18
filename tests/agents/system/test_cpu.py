#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import multiprocessing
from datetime import datetime, timedelta
from unittest import TestCase

from mockito import when, unstub

from vzmi.ychaos.agents.agent import AgentState
from vzmi.ychaos.agents.system.cpu import _burn, CPUBurnConfig, CPUBurn
from vzmi.ychaos.utils.dependency import DependencyUtils


class TestCpuBurn(TestCase):
    def setUp(self) -> None:
        pass

    def test_burn_while_loop_exits_when_end_datetime_reached(self):
        start = datetime.now()
        _burn(end=start + timedelta(seconds=2))
        end = datetime.now()
        difference = end - start
        self.assertEqual(difference.seconds, 2)
        self.assertEqual(difference.days, 0)

    def test_cpu_burn_updates_state_when_complete(self):
        when(multiprocessing).cpu_count().thenReturn(
            1
        )  # Mock that the system has only one CPU

        cpu_burn_config = CPUBurnConfig(duration=1)
        cpu_burn_agent = CPUBurn(cpu_burn_config)

        cpu_burn_agent.setup()
        self.assertEqual(cpu_burn_agent.current_state, AgentState.SETUP)

        cpu_burn_agent.start()
        self.assertEqual(cpu_burn_agent.current_state, AgentState.COMPLETED)

        cpu_burn_agent.teardown()
        self.assertEqual(cpu_burn_agent.current_state, AgentState.TEARDOWN)

    def test_cpu_burn_init_when_psutil_is_not_installed(self):
        when(DependencyUtils).import_module("psutil", raise_error=False).thenReturn(
            None
        )
        cpu_burn_config = CPUBurnConfig(duration=1)
        cpu_burn_agent = CPUBurn(cpu_burn_config)
        self.assertIsNone(cpu_burn_agent._psutil)

    def test_cpu_burn_when_effective_cpu_count_is_zero(self):
        cpu_burn_config = CPUBurnConfig(duration=1, cores_pct=0)
        cpu_burn_agent = CPUBurn(cpu_burn_config)

        self.assertEqual(cpu_burn_config.effective_cpu_count(), 0)

        cpu_burn_agent.setup()
        self.assertEqual(cpu_burn_agent.current_state, AgentState.SETUP)

        cpu_burn_agent.start()
        self.assertEqual(cpu_burn_agent.current_state, AgentState.COMPLETED)

        cpu_burn_agent.teardown()
        self.assertEqual(cpu_burn_agent.current_state, AgentState.TEARDOWN)

    def tearDown(self) -> None:
        unstub()
