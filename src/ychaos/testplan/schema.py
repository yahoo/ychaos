#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import UUID, uuid4

import yaml
from pydantic import Field

from ..utils.yaml import Dumper
from . import SchemaModel, SystemState
from .attack import AttackConfig
from .verification import VerificationConfig


class TestPlanSchema(SchemaModel):
    """
    Defines the schema for the Test Plan.
    """

    __test__ = False

    description: str = Field(
        default="", description="Description of the Test performed in this test plan"
    )

    verification: List[VerificationConfig] = Field(
        default=list(),
        description="List of verification configurations that will be executed to verify the system is in favorable condition",
    )

    attack: AttackConfig = Field(
        ..., description="The configuration that will be used to create chaos"
    )

    def filter_verification_by_state(
        self, system_state: SystemState
    ) -> List[VerificationConfig]:
        """
        Get all the verification configurations for a particular state
        Args:
            system_state: SystemState to filter the list

        Returns:
            Filtered list of verification configuration that are to be executed in a particular state
        """
        _filtered_config = list()
        for verification_config in self.verification:
            assert isinstance(verification_config.states, list)
            if system_state in verification_config.states:
                _filtered_config.append(verification_config)

        return _filtered_config

    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model) -> None:
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)

            schema_extra = {
                "$schema": "https://json-schema.org/draft-07/schema",
                "$id": "https://resilience.yahoo.com/schema.json",
            }
            schema.update(schema_extra)


class TestPlan(TestPlanSchema):
    """
    The Test Plan Dataclass.
    """

    __test__ = False

    id: UUID = Field(
        default_factory=uuid4,
        description="Schema for the test plan identifier",
        examples=[
            "061fc077-b95b-478b-87b6-73c29cb33c04",
            "6402e065-9c90-4719-b98c-ad03152e1238",
        ],
    )

    @classmethod
    def load_file(cls, path: Union[str, Path]) -> "TestPlan":
        path = Path(path)
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return cls(**data)

    def to_serialized_dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> dict:
        return json.loads(
            self.json(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                encoder=encoder,
                **dumps_kwargs,
            )
        )

    def export_to_file(
        self, path: Union[str, Path], *, yaml_format: bool = False, **kwargs
    ):
        path = Path(path)
        json_data = self.to_serialized_dict(**kwargs)
        with open(path, "w") as file:
            if yaml_format:
                yaml.dump(
                    json_data,
                    file,
                    default_flow_style=False,
                    sort_keys=False,
                    Dumper=Dumper,
                    **kwargs,
                )
            else:
                json.dump(json_data, file, indent=4)
