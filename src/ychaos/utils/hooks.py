#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import collections
from typing import Callable, Dict, List


class InvalidEventHookError(KeyError):
    pass


class EventHook(object):
    @classmethod
    def CallableType(cls, *arg_types):
        """
        Returns an Alias of Callable that takes in `arg_types`
        """
        # IGNORE: `Callable' must be used as 'Callable[[arg, ...], result]`
        # The Argument types are casted to List before passing.
        return Callable[list(arg_types), None]

    __hook_events__: Dict[str, Callable[..., None]] = dict()
    """
    Lists the valid hooks (and corresponding valid Callable mapping) that can be registered for this
    particular object. The `register_hook()` method checks this list
    for the hooks that are being registered.
    """

    def __init__(self):
        """
        Initializes an event hook object
        """
        self.hooks: Dict[str, List[Callable]] = collections.defaultdict(list)

    def register_hook(self, event_name: str, hook: Callable) -> None:
        """
        Register a hook to be executed at a certain event `event_name`
        Args:
            event_name: Event name
            hook: A callable

        Returns:
            None
        """
        if event_name not in self.__hook_events__:
            raise InvalidEventHookError(event_name)

        self.hooks[event_name].append(hook)

    def execute_hooks(self, event_name: str, *args) -> None:
        """
        Execute all the hooks registered for a particular event
        Args:
            event_name: Event name
            *args: The arguments that should be passed to the hook

        Returns:
            None
        """
        if event_name not in self.__hook_events__:
            raise InvalidEventHookError(event_name)

        for hook in self.hooks[event_name]:
            try:
                if getattr(hook, "active", True):
                    hook(*args)
            except Exception as hook_error:  # nosec
                if getattr(hook, "raise_error", False):
                    raise hook_error
