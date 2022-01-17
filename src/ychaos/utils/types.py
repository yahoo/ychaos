from typing import Dict, List, TypeVar, Union

JsonTypeVar = TypeVar("JsonTypeVar")

JsonPrimitive = Union[str, float, int, bool, None]

JsonDict = Dict[str, JsonTypeVar]
JsonArray = List[JsonTypeVar]

Json = Union[JsonPrimitive, JsonDict, JsonArray]
