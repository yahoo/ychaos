from tempfile import NamedTemporaryFile
from unittest import TestCase

from ychaos.testplan.attack import (
    AgentExecutionConfig,
    AttackConfig,
    MachineTargetDefinition,
    SSHConfig,
    TargetType,
)


class TestMachineTargetDefinitionSchema(TestCase):
    def test_machine_target_definition_for_hosts_from_file(self):
        temp_hostsfile = NamedTemporaryFile("w+")
        temp_hostsfile.write("mockhost1.yahoo.com")
        temp_hostsfile.seek(0)
        defnition = MachineTargetDefinition(
            blast_radius=50,
            ssh_config=SSHConfig(),
            hostfiles=[
                temp_hostsfile.name,
            ],
        )
        self.assertListEqual(
            [
                "mockhost1.yahoo.com",
            ],
            defnition.get_effective_hosts(),
        )


class TestAttackConfig(TestCase):
    def test_get_agent_config(self):
        defnition = AttackConfig(
            target_type=TargetType.MACHINE,
            agents=[AgentExecutionConfig(type="cpu_burn")],
        )
        agent_config = defnition.agents[0].get_agent_config()
        self.assertEqual(agent_config.name, "cpu_burn")
