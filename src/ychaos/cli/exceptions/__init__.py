#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from abc import abstractmethod
from typing import Any, Dict


class YChaosCLIError(Exception):

    exitcode = 1

    def __init__(self, app, message, **kwargs):
        self.app = app
        self.message: str = message
        self.attrs: Dict[str, Any] = kwargs

    @abstractmethod
    def handle(self) -> None:
        """
        Handle is the method that is called during teardown to handle a particular type of error
        Any subcommand can raise a sub class of YChaosCLIError and forget about the exception.
        The main teardown module takes responsibility of calling the handle method

        This can be used to print message of exception or handle the panic in a suitable way
        """
        if self.app.is_debug_mode():
            self.app.console.print_exception(extra_lines=2)
