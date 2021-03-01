#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from vzmi.ychaos.testplan.schema import TestPlan


class Coordinator:
    """
    The coordinator is responsible for setting up the chaos agents,
    running the agents and monitor the agent currently being run. It also
    takes care of completing the attack by bringing back to the system to its original
    state.
    """

    def __init__(self, test_plan: TestPlan):
        pass
