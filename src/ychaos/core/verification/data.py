#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ...testplan import SystemState
from ...testplan.verification import VerificationType


class VerificationStateData(BaseModel):
    rc: int = Field(
        ...,
        description="The return code of the verification plugin. 0, +x and -x respectively indicate success, failure and error.",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp at which this state data was recorded.",
    )
    type: VerificationType = Field(
        ...,
        description="The type of verification plugin that ran to record this state data",
    )

    data: Union[Dict[Any, Any], List[Any]] = Field(
        default=dict(),
        description="Plugin level data that can be consumed by the respective plugin",
    )

    class Config:
        json_encoders = {datetime: lambda v: int(v.timestamp())}


class VerificationData(BaseModel):
    __root__: Dict[SystemState, Optional[VerificationStateData]] = Field(
        default=dict.fromkeys(SystemState, None)
    )

    def encoded_dict(self):
        return {
            state.value: json.loads(state_data.json()) if state_data else None
            for state, state_data in self.__root__.items()
        }

    @classmethod
    def parse_obj(
        cls, obj: Dict[SystemState, Optional[VerificationStateData]]
    ) -> "VerificationData":
        for system_state in SystemState:
            obj.setdefault(system_state, None)
        return super(VerificationData, cls).parse_obj(obj)

    def add_data(
        self,
        system_state: SystemState,
        state_data: Optional[VerificationStateData],
        overwrite=False,
    ):
        if overwrite:
            self.__root__[system_state] = state_data
        else:
            self.__root__.setdefault(system_state, state_data)

    def replace_data(
        self, system_state: SystemState, state_data: VerificationStateData
    ):
        self.add_data(system_state, state_data, overwrite=True)

    def is_data_present(self, system_state: SystemState):
        return self.get_data(system_state) is not None

    def get_data(self, system_state: SystemState):
        return self.__root__[system_state]
