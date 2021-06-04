#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import re
from enum import Enum
from types import DynamicClassAttribute, SimpleNamespace
from typing import Any, Iterable, List, Optional, Type, TypeVar

T = TypeVar("T")


class BuiltinUtils:
    class Float:
        NAN = float("NaN")

    @classmethod
    def wrap_if_non_iterable(cls, obj: Any):
        """
        Wraps an object into a List only if the object is not
        an iterable. If the object is already an Iterable, the method returns
        the object type converted to List.

        Args:
            obj: Any object

        Returns:
            Wrapped list if non iterable
        """
        if isinstance(obj, Iterable):
            return list(obj)
        else:
            return cls.wrap_as_list(obj)

    @classmethod
    def wrap_as_list(cls, obj) -> List:
        """
        Wrap an object to a List.
        Args:
            obj:

        Returns:
            Wrapped list
        """
        return [
            obj,
        ]

    @classmethod
    def pass_coroutine(cls, *args, **kwargs):
        """This method literally does nothing"""
        pass


class AEnum(Enum):
    """
    Advanced Enumeration to add a metadata to each of the Enum object.
    This will add a 2 level mapping for NAME -> VALUE -> METADATA. The label
    is optional and can be set to a simple
    """

    def __new__(cls: Type[T], value, metadata: Optional[SimpleNamespace] = None):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.metadata = metadata
        return obj

    @DynamicClassAttribute
    def value(self) -> str:
        # mypy causes issues without this
        return self._value_


class FQDN(str):
    _regex = r"^((?![-])[-A-Z\d]{1,63}(?<!-)[.])*(?!-)[-A-Z\d]{1,63}(?<!-)[.]?$"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, fqdn: str):
        if len(fqdn) > 255:
            raise ValueError(f"{fqdn} is not a valid FQDN")
        fqdn = fqdn[:-1] if fqdn[-1] == "." else fqdn
        allowed = re.compile(cls._regex, re.IGNORECASE)
        if all(allowed.match(x) for x in fqdn.split(".")):
            return fqdn
        else:
            raise ValueError(f"{fqdn} is not a valid FQDN")

    def __new__(cls, *args, **kwargs):
        return cls.validate(args[0])
