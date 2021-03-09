#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import functools
import shlex
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import AnyHttpUrl, Field, SecretStr, validator

from vzmi.ychaos.testplan import SchemaModel, SystemState
from vzmi.ychaos.testplan.common import Secret
from vzmi.ychaos.utils.builtins import AEnum, BuiltinUtils


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

    def safe_arguments(self):
        return [shlex.quote(x) for x in self.arguments]


class HTTPRequestVerification(SchemaModel):

    _http_methods = ("GET", "POST", "HEAD", "PATCH", "DELETE")

    count: int = Field(
        default=1,
        description="Number of HTTP calls to be sent to each of the URL",
        ge=1,
    )
    latency: int = Field(
        default=50,
        description="Expected Latency in ms. A latency below this value indicates successful verification",
        ge=1,
    )

    status_codes: List[int] = Field(
        default_factory=functools.partial(list, range(200, 300)),
        description="The list of status code which will be the comparison factor for the HTTP responses",
    )

    urls: List[AnyHttpUrl] = Field(
        default=list(), description="List of HTTP/s URLs to be requested"
    )
    method: str = Field(default="GET", description="HTTP method to be used")
    headers: Dict[str, Union[SecretStr, Secret]] = Field(
        default=dict(), description="Headers to be sent with the request"
    )
    params: Dict[str, str] = Field(
        default=dict(), description="Query params to be sent with the request"
    )
    verify: bool = Field(
        default=True, description="Verify the target URL SSL certificates"
    )

    # Authentication
    basic_auth: Optional[Tuple[str, Union[SecretStr, Secret]]] = Field(
        default=None, description="Basic Auth authentication for the HTTP call"
    )
    bearer_token: Optional[Union[SecretStr, Secret]] = Field(
        default=None, description="Bearer token authentication for the HTTP call"
    )

    # Certificate
    cert: Tuple[Path, Path] = Field(
        default=None,
        description="The certificate to be sent for HTTP call. The tuple should contain Certificate and Key File path",
    )

    timeout: int = Field(
        default=10000,
        description="Timeout in milliseconds at which the HTTP requests will timeout",
        gt=0,
    )

    @validator("method", pre=True)
    def validate_method(cls, v):
        if v in cls._http_methods:
            return v
        else:
            raise ValueError("Unknown HTTP method")


class VerificationType(AEnum):
    """
    Defines the Type of plugin to be used for verification.
    """

    # The metadata object will contain the following attributes
    # 1. schema : The Schema class of the VerificationType

    PYTHON_MODULE = "python_module", SimpleNamespace(schema=PythonModuleVerification)
    HTTP_REQUEST = "http_request", SimpleNamespace(schema=HTTPRequestVerification)


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

    def get_verification_config(self):
        return self.type.metadata.schema(**self.config)

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
            return VerificationType(values["type"]).metadata.schema(**v)
        else:
            return v
