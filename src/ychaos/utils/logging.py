#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import logging
from logging import DEBUG, ERROR, INFO, WARNING, Logger
from typing import Optional, Set


class StructLogger(Logger):
    def __init__(self, name):
        super().__init__(name)
        logging.setLoggerClass(self.__class__)
        self._binder = dict()

    def _build_msg(self, msg="", **kwargs) -> str:
        bind_msg = " ".join([f"{k}={v}" for k, v in self._binder.items()])
        kwargs_msg = " ".join([f"{k}={v}" for k, v in kwargs.items()])

        return f"{bind_msg} {kwargs_msg} {msg}"

    def getChild(self, suffix: str, bind_parent_attributes=False) -> "StructLogger":
        """
        Get Child Logger and bind Parent attributes to child if needed.
        Args:
            suffix: Suffix to be added to the child logger
            bind_parent_attributes: Bind Parent Attributes to Child if needed
        Returns:
            Child Struct Logger
        """
        _logger: StructLogger = super(StructLogger, self).getChild(suffix)  # type: ignore
        if bind_parent_attributes:
            assert isinstance(_logger, StructLogger)
            _logger.bind(**self._binder)

        return _logger

    def debug(self, msg="", *args, **kwargs) -> None:
        level = DEBUG
        exc_info, extra, stack_info = (
            kwargs.pop("exc_info", None),
            kwargs.pop("extra", None),
            kwargs.pop("stack_info", False),
        )
        if self.isEnabledFor(level):
            self._log(
                level,
                self._build_msg(msg, **kwargs),
                args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
            )

    def info(self, msg="", *args, **kwargs) -> None:
        level = INFO
        exc_info, extra, stack_info = (
            kwargs.pop("exc_info", None),
            kwargs.pop("extra", None),
            kwargs.pop("stack_info", False),
        )
        if self.isEnabledFor(level):
            self._log(
                level,
                self._build_msg(msg, **kwargs),
                args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
            )

    def error(self, msg="", *args, **kwargs) -> None:
        level = ERROR
        exc_info, extra, stack_info = (
            kwargs.pop("exc_info", None),
            kwargs.pop("extra", None),
            kwargs.pop("stack_info", False),
        )
        if self.isEnabledFor(level):
            self._log(
                level,
                self._build_msg(msg, **kwargs),
                args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
            )

    def warning(self, msg="", *args, **kwargs) -> None:
        level = WARNING
        exc_info, extra, stack_info = (
            kwargs.pop("exc_info", None),
            kwargs.pop("extra", None),
            kwargs.pop("stack_info", False),
        )
        if self.isEnabledFor(level):
            self._log(
                level,
                self._build_msg(msg, **kwargs),
                args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
            )

    def exception(self, msg="", *args, **kwargs) -> None:
        level = ERROR
        exc_info, extra, stack_info = (
            kwargs.pop("exc_info", True),
            kwargs.pop("extra", None),
            kwargs.pop("stack_info", False),
        )
        if self.isEnabledFor(level):
            self._log(
                level,
                self._build_msg(msg, **kwargs),
                args,
                exc_info=exc_info,
                extra=extra,
                stack_info=stack_info,
            )

    def bind(self, **kwargs) -> None:
        self._binder = kwargs

    def unbind(self, unbind_keys: Optional[Set] = None) -> None:
        """
        unbind certain/all keys

        Args:
            unbind_keys: Set of keys to unbind Or None to unbind all keys
        """
        if unbind_keys:
            for k in unbind_keys:
                self._binder.pop(k, None)
        else:
            self._binder.clear()
