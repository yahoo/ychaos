#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import json
from argparse import Namespace
from pathlib import Path
from typing import Optional

from vzmi.ychaos.agents.coordinator import Coordinator
from vzmi.ychaos.cli import YChaosTestplanInputSubCommand
from vzmi.ychaos.testplan.schema import TestPlan
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))
(Table, Column) = DependencyUtils.import_from("rich.table", ("Table", "Column"))

__all__ = ["Attack"]


class Attack(YChaosTestplanInputSubCommand):
    """
    Agent Attack subcommand is used to perform the attack on the target. This
    subcommand requires a valid testplan to perforrm the required attack on
    the target system.
    """

    name = "attack"
    help = "YChaos Agent Attack Subcommand"

    def __init__(self, **kwargs):
        super(Attack, self).__init__(**kwargs)
        assert kwargs.pop("cls") == self.__class__
        self.app = kwargs.pop("app")
        self.console = self.app.console
        self.test_plan_path: Path = kwargs.pop("testplan")
        self.test_plan: Optional[TestPlan] = None
        self.coordinator: Optional[Coordinator] = None

    def validate_and_load_test_plan(self) -> int:
        self.test_plan = super(Attack, self).get_validated_test_plan(
            self.test_plan_path
        )
        return self._exitcode

    def configure_attack(self):
        self.coordinator = Coordinator(self.test_plan)
        self.coordinator.configure_agent_in_test_plan()
        table = Table(
            Column("Agent", style="green"),
            Column("Start Delay", justify="center", style="green"),
            Column("Start Time", style="green"),
            Column("End Time", style="green"),
            title="Configured Agents",
            show_header=True,
            header_style="bold magenta",
        )
        for configured_agent in self.coordinator.configured_agents:
            table.add_row(
                configured_agent.agent.config.name,
                str(configured_agent.agent.config.start_delay),
                str(configured_agent.start_time),
                str(configured_agent.end_time)
                if hasattr(configured_agent.agent.config, "duration")
                else "Unknown",
            )
        self.console.print(table)

    def print_all_errors(self):
        all_exceptions = self.coordinator.get_all_exceptions()
        for e in all_exceptions:
            try:
                raise e
            except Exception:
                self.console.print_exception()

    @classmethod
    def main(cls, args: Namespace):
        agent = Attack(**vars(args))
        if not agent.validate_and_load_test_plan():
            agent.configure_attack()
            agent.console.log("Starting The Attack")
            assert agent.coordinator is not None
            agent.coordinator.start_attack()
            agent.console.log("Attack Completed")
            agent.console.log(
                json.dumps(agent.coordinator.generate_attack_report(), indent=4)
            )

            agent.print_all_errors()

            if not agent._exitcode:
                agent.set_exitcode(agent.coordinator.get_exit_status())

            if agent._exitcode:
                agent.console.log("Attack Failed")
        return agent._exitcode
