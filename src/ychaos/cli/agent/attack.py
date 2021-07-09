#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional

from rich.table import Column, Table

from ...agents.coordinator import Coordinator
from ...testplan.schema import TestPlan
from ...utils.yaml import Dumper
from .. import YChaosCLIHook, YChaosTestplanInputSubCommand

__all__ = ["Attack"]


class Attack(YChaosTestplanInputSubCommand):
    """
    Agent Attack subcommand is used to perform the attack on the target. This
    subcommand requires a valid testplan to perforrm the required attack on
    the target system.
    """

    name = "attack"
    help = "YChaos Agent Attack Subcommand"

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        super(Attack, cls).build_parser(parser)
        parser.add_argument(
            "--attack-report-yaml",
            type=Path,
            help="File Path to store attack report in YAML format",
            default=None,
            metavar="path",
        )
        return parser

    def __init__(self, **kwargs):
        super(Attack, self).__init__(**kwargs)

        self.test_plan_path: Path = kwargs.pop("testplan")
        self.attack_report_yaml_path: Optional[Path] = kwargs.pop("attack_report_yaml")
        if self.attack_report_yaml_path and self.attack_report_yaml_path.is_dir():
            self.console.log(f"{self.attack_report_yaml_path} is not a valid file path")
            self.attack_report_yaml_path = None
        self.test_plan: Optional[TestPlan] = None
        self.coordinator: Optional[Coordinator] = None

    def validate_and_load_test_plan(self) -> int:
        self.test_plan = super(Attack, self).get_validated_test_plan(
            self.test_plan_path
        )
        return self._exitcode

    def configure_attack(self):
        self.coordinator = Coordinator(self.test_plan)

        class YChaosAgentAttackCLIHook(YChaosCLIHook):
            def __init__(self, app):
                super(YChaosAgentAttackCLIHook, self).__init__(app)

        class OnAttackStart(YChaosAgentAttackCLIHook):
            def __call__(self):
                self.console.log("Attack Started")

        class OnAttackCompleted(YChaosCLIHook):
            def __call__(self):
                self.console.log("Attack Ended")

        class OnAgentStart(YChaosAgentAttackCLIHook):
            def __call__(self, agent_name: str):
                self.console.log(f"Agent: {agent_name} - Started")

        class OnAgentTeardown(YChaosAgentAttackCLIHook):
            def __call__(self, agent_name: str):
                self.console.log(f"Agent: {agent_name} - Teardown started")

        class OnAgentStop(YChaosAgentAttackCLIHook):
            def __call__(self, agent_name: str):
                self.console.log(f"Agent: {agent_name} - Stopped")

        self.coordinator.register_hook("on_attack_start", OnAttackStart(self.app))
        self.coordinator.register_hook(
            "on_attack_completed",
            OnAttackCompleted(self.app),
        )
        self.coordinator.register_hook("on_each_agent_start", OnAgentStart(self.app))
        self.coordinator.register_hook(
            "on_each_agent_teardown",
            OnAgentTeardown(self.app),
        )
        self.coordinator.register_hook("on_each_agent_stop", OnAgentStop(self.app))

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

    def dump_attack_report(self):
        if self.attack_report_yaml_path:
            import yaml

            with open(
                self.attack_report_yaml_path,
                "w",
            ) as fp:
                yaml.dump(
                    self.coordinator.generate_attack_report(),
                    fp,
                    default_flow_style=False,
                    sort_keys=False,
                    Dumper=Dumper,
                    indent=4,
                )
            self.console.log(f"Attack report stored at {self.attack_report_yaml_path}")

    @classmethod
    def main(cls, args: Namespace) -> Any:
        agent = cls(**vars(args))
        if agent._exitcode:
            return agent._exitcode
        if not agent.validate_and_load_test_plan():
            agent.configure_attack()
            assert agent.coordinator is not None

            agent.coordinator.start_attack()

            agent.print_all_errors()

            agent.dump_attack_report()

            if agent._exitcode or agent.coordinator.get_exit_status():
                agent.console.log("Attack failed")
                agent.set_exitcode(1)
        return agent._exitcode
