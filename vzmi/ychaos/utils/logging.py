from logging import DEBUG, ERROR, INFO, WARNING, Logger
from typing import Optional, Set


class StructLogger(Logger):
    def __init__(self, name):
        super().__init__(name)
        self._binder = dict()

    def _build_msg(self, msg="", log_dict=None, **kwargs) -> str:
        if log_dict is None:  # pragma: no cover
            log_dict = dict()

        dict_msg = " ".join([f"{k}={v}" for k, v in log_dict.items()])
        bind_msg = " ".join([f"{k}={v}" for k, v in self._binder.items()])
        kwargs_msg = " ".join([f"{k}={v}" for k, v in kwargs.items()])

        return f"{bind_msg} {dict_msg} {kwargs_msg} {msg}"

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
                self._build_msg(msg, kwargs),
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
                self._build_msg(msg, kwargs),
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
                self._build_msg(msg, kwargs),
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
                self._build_msg(msg, kwargs),
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
                self._build_msg(msg, kwargs),
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
