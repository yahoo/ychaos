#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from argparse import Namespace
from pathlib import Path
from typing import Optional

from vzmi.ychaos.agents.coordinator import Coordinator
from vzmi.ychaos.cli import YChaosTestplanInputSubCommand
from vzmi.ychaos.testplan.schema import TestPlan
from vzmi.ychaos.utils.dependency import DependencyUtils

(Console,) = DependencyUtils.import_from("rich.console", ("Console",))

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
        self.console: Console = self.app.console
        self.test_plan_path: Path = kwargs.pop("testplan")
        self.test_plan: Optional[TestPlan] = None

    def start_attack(self):
        coordinator = Coordinator(self.test_plan)

    def validate_and_load_test_plan(self) -> int:
        self.test_plan = super(Attack, self).get_validated_test_plan(
            self.test_plan_path
        )
        return self._exitcode

    @classmethod
    def main(cls, args: Namespace):
        agent = Attack(**vars(args))
        if not agent.validate_and_load_test_plan():
            agent.start_attack()
        return agent._exitcode
