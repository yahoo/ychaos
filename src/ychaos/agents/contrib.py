#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import importlib.util
from pathlib import Path
from typing import Any, Dict

from pydantic import Field, PrivateAttr

from .agent import Agent, AgentConfig


class ContribAgentConfig(AgentConfig):
    name = "contrib"
    path: Path = Field(..., description="The path of the agent python file")

    agent_class: str = Field(
        default="AgentClass", description="The class name of the contributed Agent"
    )
    agent_config_class: str = Field(
        default="AgentConfigClass",
        description="The class name of the contributed Agent config",
    )

    config: Dict[Any, Any] = Field(
        default=dict(),
        description="The configuration that will be passed to the community agent",
    )

    # For storing imported module
    # Initialized late in the _import_module() method
    _module: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super(ContribAgentConfig, self).__init__(**kwargs)
        self._import_module()

        # Validate that `config` adheres to the schema of the contrib agent
        self.config = self.get_agent_config_class()(**self.config)

    def _import_module(self):
        specification = importlib.util.spec_from_file_location(
            name="", location=self.path
        )
        self._module = importlib.util.module_from_spec(specification)

        assert self._module is not None
        assert specification.loader is not None
        specification.loader.exec_module(module=self._module)  # type: ignore

    def get_agent_class(self) -> Any:
        agent_klass = getattr(self._module, self.agent_class)
        assert issubclass(agent_klass, Agent)
        return agent_klass

    def get_agent_config_class(self) -> Any:
        agent_config_klass = getattr(self._module, self.agent_config_class)
        assert issubclass(agent_config_klass, AgentConfig)
        return agent_config_klass

    def get_agent(self):
        return self.get_agent_class()(self.config)
