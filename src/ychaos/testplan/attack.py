#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import getpass
import os
import re
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, TypeVar, Union

from pydantic import Field, FilePath, SecretStr, validator

from ..agents.index import AgentType
from ..utils.builtins import FQDN, AEnum
from . import SchemaModel
from .common import Secret, SecretType


class TargetDefinition(SchemaModel):
    report_dir: Path = Field(
        default=Path("./"),
        description="The report directory to store execution files. Defaults to current directory",
    )


T_TargetDefinition = TypeVar("T_TargetDefinition", bound=TargetDefinition)


class SSHConfig(SchemaModel):
    user: str = Field(
        default=getpass.getuser(),
        description="The login user for SSH connection. Defaults to current user.",
    )
    private_key: Optional[Path] = Field(
        default=None,
        description="The private key file that will be used to login to the hosts.",
    )
    password: Union[SecretStr, Secret] = Field(
        default=Secret(type=SecretType.RAW, id=None),
        description="The password that will be used to login to the hosts.",
    )
    ssh_common_args: str = Field(
        default=os.getenv("ANSIBLE_SSH_COMMON_ARGS", ""),
        description="The common Arguments to be used while SSHing to a host with Ansible (`$ANSIBLE_SSH_COMMON_ARGS`)",
    )

    @validator("ssh_common_args", always=True)
    def set_ssh_common_args_env(cls, v):
        os.environ["ANSIBLE_SSH_COMMON_ARGS"] = v
        return v

    @validator("private_key")
    def set_private_key(cls, v):
        os.environ["ANSIBLE_PRIVATE_KEY_FILE"] = str(v)
        return v


class MachineTargetDefinition(TargetDefinition):
    """
    Represents the configuration when the target is a Virtual machine
    or Baremetal. To use this as a target, `target_type` should be equal to
    `machine`

    Attributes:
        blast_radius: The percentage of targets to be attacked. **This is a required field**
        ssh_config: The SSH Configuration to be used while logging into the hosts. See [SSHConfig][ychaos.testplan.attack.SSHConfig]
        hostnames: List of hosts as targets to run the agents on. These should be valid FQDNs.
        hostpatterns: List of Host patterns with a single number range within the pattern
        hostfiles:
            List of files containing hostnames separated by a newline
            The path provided can be an absolute path or a relative path from which the tool is invoked.
        exclude:
            List of hosts to be always excluded out of the attack.
            The filtering criteria will always exclude the hosts in this list

    Warning:
        Testplan validator will not be able to validate each of the host entries if the targets are provided
        using `hostfiles`. The tool will dynamically validate each of the entry while reading the files.
    """

    blast_radius: int = Field(
        ..., description="The percentage of targets to be attacked", ge=0, le=100
    )

    ssh_config: SSHConfig = Field(
        default=SSHConfig(),
        description="The configuration used to SSH to the target machines.",
    )

    hostnames: List[FQDN] = Field(
        default=list(),
        description="List of hosts as targets to run the agents on. These should be valid FQDNs.",
        examples=[
            ["myhost01.yahoo.com", "myhost02.yahoo.com", "mockhost.web.fe.yahoo.com"],
        ],
    )

    hostpatterns: List[str] = Field(
        default=list(),
        description="List of Host patterns with a single number range within the pattern",
        examples=[
            ["myhost[12-34].yahoo.com", "hostpattern[00-10].mock.yahoo.com"],
        ],
    )

    hostfiles: List[FilePath] = Field(
        default=list(),
        description=(
            "List of files containing hostnames separated by a newline"
            "The path provided can be an absolute path or a relative path from which the tool is invoked."
            "Note that the testplan will not validate each file during static validation."
        ),
        examples=[
            ["/home/awesomeuser/hostlist.txt", "/home/awesomeuser/tmp/inventory.txt"]
        ],
    )

    exclude: List[FQDN] = Field(
        default=list(),
        description=(
            "List of hosts to be always excluded out of the attack."
            "The filtering criteria will always exclude the hosts in this list"
        ),
    )

    def iterate_hostfiles(self):
        for file in self.hostfiles:
            for host in file.read_text().strip().splitlines():
                yield FQDN(host)

    def iterate_hostpattern(self):
        for v in self.hostpatterns:
            match = re.search(r"\[((\d+)-(\d+))\]", v)
            if match is None:
                yield FQDN(v)

            else:
                range_start = match.group(2)
                range_end = match.group(3)

                for num in range(int(range_start), int(range_end) + 1):
                    yield FQDN(
                        v[: match.start()]
                        + str(num).zfill(len(range_start))
                        + v[match.end() :]
                    )

    def expand_hostpatterns(self) -> List[FQDN]:
        expanded_list = list()
        for hostname in self.iterate_hostpattern():
            expanded_list.append(hostname)

        return expanded_list

    def expand_hostfiles(self):
        expanded_list = list()
        for host in self.iterate_hostfiles():
            expanded_list.append(host)
        return expanded_list

    def get_effective_hosts(self):
        return list(
            set(
                self.expand_hostpatterns() + self.expand_hostfiles() + self.hostnames
            ).difference(set(self.exclude))
        )

    @validator("hostpatterns", pre=True, each_item=True)
    def validate_hostpatterns(cls, v):
        match = re.search(r"\[((\d+)-(\d+))\]", v)
        if match is None:
            FQDN(v)

        else:
            range_start = match.group(2)
            range_end = match.group(3)

            for num in range(int(range_start), int(range_end) + 1):
                FQDN(
                    v[: match.start()]
                    + str(num).zfill(len(range_start))
                    + v[match.end() :]
                )
        return v


class SelfTargetDefinition(TargetDefinition):
    """
    Represents the configuration when the target is your local machine
    . To use this as a target, `target_type` should be equal to
    `self`.
     You can avoid specifying `target_config` for this target type.
    """

    pass


class TargetType(AEnum):

    SELF = "self", SimpleNamespace(schema=SelfTargetDefinition)
    # The machine running the toolkit registers itself as the target to run all the agents

    MACHINE = "machine", SimpleNamespace(schema=MachineTargetDefinition)
    # Registers some virtual machines, Baremetals etc.


class AttackMode(Enum):
    """
    Defines the type of execution mode for executing the configured Agents
    """

    CONCURRENT = "concurrent"
    SEQUENTIAL = "sequential"


class AgentExecutionConfig(SchemaModel):

    type: AgentType = Field(
        ...,
        description=(
            "Defines the agent type to be executed on the target. "
            "The configuration of agent is determined by this attribute"
        ),
        examples=["cpu_burn", "no_op", "ping_disable"],
    )

    config: Dict[Any, Any] = Field(
        default=dict(),
        description="The Agent configuration for a particular agent type",
    )

    def get_agent_config(self):
        return self.type.metadata.schema(**self.config)

    @validator("config", pre=True)
    def _parse_agent_configuration(cls, v, values):
        if "type" in values:
            return AgentType(values["type"]).metadata.schema(**v)
        else:  # pragma: no cover
            return v


class AttackConfig(SchemaModel):

    target_type: TargetType = Field(
        ...,
        description=(
            "Defines the target type which will be used as a target for the execution of agents. "
            "The target_type configuration is determined the type mentioned in this attribute"
        ),
        examples=["self", "machine"],
    )

    target_config: Dict[Any, Any] = Field(
        default=dict(),
        description=(
            "Defines the targets for running the agents."
            "This can be set to null to imply that the framework should run all the agents within the same system where the executor has been invoked"
        ),
    )

    mode: AttackMode = Field(
        default=AttackMode.SEQUENTIAL,
        description="Define the execution mode for the attack",
    )

    agents: List[AgentExecutionConfig] = Field(
        default=list(),
        description=(
            "List of agents to be executed on the Target. "
            "Each of the item of execution configuration will infer a type of agent and a configuration of the agent"
        ),
        min_items=1,
    )

    def get_target_config(self) -> T_TargetDefinition:
        return self.target_type.metadata.schema(**self.target_config)

    @validator("target_config", pre=True)
    def _parse_target_configuration(cls, v, values):
        if "target_type" in values:
            return TargetType(values["target_type"]).metadata.schema(**v)
        else:  # pragma: no cover
            return v
