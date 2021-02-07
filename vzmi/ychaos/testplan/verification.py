import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import Field, validator

from vzmi.ychaos.testplan import SchemaModel, SystemState
from vzmi.ychaos.utils.builtins import BuiltinUtils


class PythonModuleVerification(SchemaModel):
    """
    The Python Module verification. Runs an custom python script given
    the path of the script. The executable of the script is set to `sys.executable` by
    default which can be overridden by a custom executable. The script can also be passed
    a list of arguments that are provided in the arguments argument which are passed to
    the script by separating each element of the argument by space.

    The user of this plugin takes the entire responsibility of the script executed. YChaos
    is only responsible of running the script and collecting the exitcode of the script
    with which the state of the system is verified/monitored.
    """

    path: Path = Field(..., description="The absolute path of the python script")
    executable: str = Field(
        default=sys.executable,
        description="The python shell to be used for executing the script",
    )
    arguments: List[str] = Field(
        default=list(),
        description="List of arguments to be sent to the script. The arguments in the list will be sent to the script space separated",
    )


class VerificationType(Enum):
    """
    Defines the Type of plugin to be used for verification.
    """

    __CONFIG_MAPPER__ = {"python_module": PythonModuleVerification}

    PYTHON_MODULE = "python_module"

    def get_mapper(
        self,
    ):
        return self.__CONFIG_MAPPER__.get(self.value)


class VerificationConfig(SchemaModel):
    """
    The verification configuration that is executed during some state of the system
    to verify the system is in a favorable conditions or not.
    """

    delay_before: float = Field(
        default=0,
        description="delay (in ms) to be introduced before running this plugin",
    )

    delay_after: float = Field(
        default=0,
        description="delay (in ms) to be introduced after running this plugin",
    )

    states: Union[SystemState, List[SystemState]] = Field(
        ...,
        description="A system state or a list of system states in which this verification plugin should be executed.",
    )

    type: VerificationType = Field(..., description="The verification type to be used.")

    config: Dict[str, Any] = Field(
        ..., description="The verification type configuration"
    )

    def get_parsed_config(self):
        return self.type.get_mapper()(**self.config)

    @validator("states", pre=True)
    def _parse_states_to_list(cls, v):
        """
        Parses the state object to List of states to keep
        the access consistent
        Args:
            v: SystemState object/ List of SystemState

        Returns:
            List of SystemState
        """
        return BuiltinUtils.wrap_if_non_iterable(v)

    @validator("config", pre=True)
    def _parse_plugin_configuration(cls, v, values):
        """
        Validates the plugin configuration to match with the
        mapper class of the plugin.
        Args:
            v: Plugin configuration
            values: verification configuration

        Returns:
            Parsed mapper object
        """
        if "type" in values:
            return VerificationType(values["type"]).get_mapper()(**v)
        else:
            return v
