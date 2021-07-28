#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import time
from typing import Dict, List, Optional, Type

from pydantic import validate_arguments

from ...app_logger import AppLogger
from ...testplan import SystemState
from ...testplan.schema import TestPlan
from ...utils.hooks import EventHook
from ...utils.yaml import Dumper
from .data import VerificationData, VerificationStateData
from .plugins.BaseVerificationPlugin import BaseVerificationPlugin
from .plugins.HTTPRequestVerificationPlugin import (
    HTTPRequestVerificationPlugin,
)
from .plugins.PythonModuleVerificationPlugin import (
    PythonModuleVerificationPlugin,
)
from .plugins.SDv4VerificationPlugin import SDv4VerificationPlugin

# Enum value to corresponding Plugin Map

VERIFICATION_PLUGIN_MAP: Dict[str, Type[BaseVerificationPlugin]] = {
    "python_module": PythonModuleVerificationPlugin,
    "http_request": HTTPRequestVerificationPlugin,
    "sdv4": SDv4VerificationPlugin,
}


class VerificationController(EventHook):
    """
    Verification controller is used to run all the verification plugins configured in the testplan
    and assert that the system is expected to be in a state expected by the user. Extends the EventHook class,
    that defines the following event hooks.

    ## Valid Hooks

    === "on_start"
        Hook that gets called when the verification execution is about to start.
        No arguments are passed to the callable.

        ```python
            def callable_hook(): ...
        ```

    === "on_each_plugin_start"
        Hook that gets called when a particular plugin execution is about to start. `index` in the signature refers
        to the position in the list

        ```python
            def callable_hook(index: int, config: VerificationConfig): ...
        ```
        References:
            1. [VerificationConfig][ychaos.testplan.verification.VerificationConfig]

    === "on_each_plugin_end"
        Hook that gets called when a particular plugin execution has ended. `index` in the signature refers to the
        position in the list

        ```python
            def callable_hook(index: int, config: VerificationConfig, state_data: VerificationStateData): ...
        ```

        References:
            1. [VerificationConfig][ychaos.testplan.verification.VerificationConfig]
            2. [VerificationStateData][ychaos.core.verification.data.VerificationStateData]

    === "on_end"
        Hook that gets called when the verification execution has ended. Each element in the list
        of boolean corresponds to the result of the plugin, where `True` indicates successful verification
        and `False` is a failure to verify the state

        ```python
            def callable_hook(verify_list: List[bool]): ...
        ```

    === "on_plugin_not_found"
        Hook that gets called when a plugin available in schema is not ready for usage/not implemented.
        This case is possible for the plugins that are in Beta/development phase

        ```python
            def callable_hook(index:int, plugin_type: VerificationType): ...
        ```

    ---
    Each of the hooks get called on a certain event. The caller can register as many hooks for a particular event,
    by calling the `register_hook(event_name, hook_method)` method. All the hooks are executed sequentially. The best example
    of this is to register a hook to print information on CLI.
    """

    __hook_events__ = (
        "on_start",
        "on_each_plugin_start",
        "on_each_plugin_end",
        "on_plugin_not_found",
        "on_end",
    )

    @validate_arguments
    def __init__(
        self,
        testplan: TestPlan,
        current_state: SystemState,
        verification_data: List[Dict[SystemState, Optional[VerificationStateData]]],
    ):
        """
        Initialize a verification controller object.

        Args:
            testplan: A valid testplan object
            current_state: The state in which the system is expected to be in
            verification_data (List[VerificationData]): The verification data probably from previous run.
        """
        super(VerificationController, self).__init__()
        self.logger = AppLogger.get_logger(self.__class__.__name__)
        self.logger.bind(event="controller")

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

    def execute(self) -> bool:
        """
        Execute the Verification controller.

        Returns:
            True if all the verification plugin pass, False otherwise
        """

        # Call all the hooks that were registered for `verification_start`
        # If there were no hooks registered, this will be no-op
        self.execute_hooks("on_start")

        _verify_list = list()
        for index, (verification_plugin, data) in enumerate(
            zip(self.testplan.verification, self.verification_data)
        ):

            # Delay before verifying
            time.sleep(verification_plugin.delay_before)

            assert isinstance(verification_plugin.states, List)  # For mypy
            if self.current_state in verification_plugin.states:
                self.logger.info(
                    msg=f"Starting {verification_plugin.type.value} verification"
                )
                plugin_class = VERIFICATION_PLUGIN_MAP.get(
                    verification_plugin.type.value, None
                )

                if plugin_class is None:
                    # This can happen when a new plugin is not implemented yet, but is
                    # available in the schema
                    self.execute_hooks(
                        "on_plugin_not_found", index, verification_plugin.type
                    )
                    continue

                plugin = plugin_class(verification_plugin.config, data)

                # Call all the hooks that were registered for `verification_plugin_start`.
                self.execute_hooks("on_each_plugin_start", index, verification_plugin)

                state_data = plugin.run_verification()
                self.logger.info(
                    msg=f"Completed {verification_plugin.type.value} verification"
                )

                # Call all the hooks that were registered for `verification_plugin_end`.
                self.execute_hooks(
                    "on_each_plugin_end", index, verification_plugin, state_data
                )

                data.replace_data(self.current_state, state_data)
                if verification_plugin.strict:
                    _verify_list.append(state_data.rc == 0)
            else:
                data.add_data(self.current_state, None)

            # Delay after verifying
            time.sleep(verification_plugin.delay_after)

        # Call all the hooks that were registered for `verification_end`.
        self.execute_hooks("on_end", _verify_list)

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
