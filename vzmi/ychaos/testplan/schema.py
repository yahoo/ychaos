from typing import Any, Dict, List
from uuid import UUID, uuid4

from pydantic import Field

from vzmi.ychaos.testplan import SchemaModel, SystemState
from vzmi.ychaos.testplan.verification import VerificationConfig


class TestPlanSchema(SchemaModel):

    description: str = Field(
        default="", description="Description of the Test performed in this test plan"
    )

    verification: List[VerificationConfig] = Field(
        default=list(),
        description="List of verification configurations that will be executed to verify the system is in favorable condition",
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
                "$schema": "http://json-schema.org/draft-07/schema",
                "$id": "http://resilience.yahoo.com/test-plan-schema.json",
            }
            schema.update(schema_extra)


class TestPlan(TestPlanSchema):
    """
    The Test Plan Dataclass
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Schema for the test plan identifier",
        examples=[
            "061fc077-b95b-478b-87b6-73c29cb33c04",
            "6402e065-9c90-4719-b98c-ad03152e1238",
        ],
    )
