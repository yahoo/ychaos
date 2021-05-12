#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import os
from types import SimpleNamespace
from typing import Any

from pydantic import Field

from ychaos.testplan import SchemaModel
from ychaos.utils.builtins import AEnum


class SecretType(AEnum):
    """
    Defines the type of secret the caller wants to fetch

    Attributes:
        env: The secret is to be fetched from Environment variable.

    """

    ENV = "env", SimpleNamespace(parser=lambda v: os.getenv(v))
    # Defines the secret to be fetched from environment variable


class Secret(SchemaModel):
    """
    Secret object defines the ways of fetching a secret to populate a value. For example, the login
    password to a host. The type of secret defines what kind of secret, the tool is trying to fetch
    and id is the unique identifier for that secret.

    A simple example is a Environment Variable. If the type=`env` and id=`HOST_PASSWORD`, then the tool
    will read the environment variable to determine the secret to use. This will allow the users
    to not reveal the secrets in testplan.
    """

    type: SecretType = Field(
        default=SecretType.ENV, description="defines the type of secret to be fetched. "
    )
    id: Any = Field(
        ...,
        description="The public identifier data which can be used to fetch the secret",
    )

    def get_secret_value(self):
        """
        Return the secret value.
        Returns:
            the secret value fetched from the parser.
        """
        return self.type.metadata.parser(self.id)
