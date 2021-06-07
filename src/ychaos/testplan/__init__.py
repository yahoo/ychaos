#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


class SystemState(Enum):
    STEADY = "STEADY"
    CHAOS = "CHAOS"
    RECOVERED = "RECOVERED"


class SchemaModel(BaseModel):
    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model) -> None:
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
