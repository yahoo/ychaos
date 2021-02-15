#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from typing import Any, Iterable, List


class BuiltinUtils:
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
