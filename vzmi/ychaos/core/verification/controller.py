#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import time
from typing import Dict, List, Optional

from pydantic import validate_arguments

from vzmi.ychaos.core.verification.data import (
    VerificationData,
    VerificationStateData,
)
from vzmi.ychaos.core.verification.plugins.HTTPRequestVerificationPlugin import (
    HTTPRequestVerificationPlugin,
)
from vzmi.ychaos.core.verification.plugins.PythonModuleVerificationPlugin import (
    PythonModuleVerificationPlugin,
)
from vzmi.ychaos.testplan import SystemState
from vzmi.ychaos.testplan.schema import TestPlan
from vzmi.ychaos.utils.yaml import Dumper

# Enum value to corresponding Plugin Map

VERIFICATION_PLUGIN_MAP = {
    "python_module": PythonModuleVerificationPlugin,
    "http_request": HTTPRequestVerificationPlugin,
}


class VerificationController:
    @validate_arguments
    def __init__(
        self,
        testplan: TestPlan,
        current_state: SystemState,
        verification_data: List[Dict[SystemState, Optional[VerificationStateData]]],
    ):
        self.testplan = testplan
        self.current_state = current_state

        if not verification_data:
            verification_data = [
                dict(),
            ] * len(self.testplan.verification)
        elif len(verification_data) != len(self.testplan.verification):
            raise ValueError("Data and verification config size mismatch")

        self.verification_data = list()
        for data in verification_data:
            self.verification_data.append(VerificationData.parse_obj(data))

    def execute(self):
        _verify_list = list()
        for verification_plugin, data in zip(
            self.testplan.verification, self.verification_data
        ):

            # Delay before verifying
            time.sleep(verification_plugin.delay_before)

            if self.current_state in verification_plugin.states:
                plugin = VERIFICATION_PLUGIN_MAP.get(verification_plugin.type.value)(
                    verification_plugin.config, data
                )
                state_data = plugin.run_verification()
                data.replace_data(self.current_state, state_data)
                if verification_plugin.strict:
                    _verify_list.append(state_data.rc == 0)
            else:
                data.add_data(self.current_state, None)

            # Delay after verifying
            time.sleep(verification_plugin.delay_after)

        return all(_verify_list)

    def get_encoded_verification_data(self):
        return [data.encoded_dict() for data in self.verification_data]

    def dump_verification_json(self, fp):
        import json

        json.dump(self.get_encoded_verification_data(), fp=fp, indent=4)

    def dump_verification_yaml(self, fp):
        import yaml

        yaml.dump(
            self.get_encoded_verification_data(),
            fp,
            default_flow_style=False,
            sort_keys=False,
            Dumper=Dumper,
            indent=4,
        )
