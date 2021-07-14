#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import os
import shlex
import subprocess  # nosec
from pathlib import Path
from typing import Union

from pydantic import validate_arguments


class SysCtl:
    """
    Provides a Utility class to operate with sysctl command.
    """

    ROOT_PATH = Path("/proc/sys")

    _cmd = "sysctl"
    _sudo = "sudo"

    @classmethod
    def get(cls, variable: str) -> bytes:
        """
        Get a sysctl variable's value as bytes.
        Args:
            variable: Variable name. Can contain `.`

        Raises:
            PermissionError: If the sysctl variable not visible to the current user

        Returns:
            A bytes object that contains the value
        """
        sysctl_var_path = cls.ROOT_PATH.joinpath(variable.replace(".", "/"))
        cls.is_variable(variable, raise_error=True)
        return sysctl_var_path.read_bytes()

    @classmethod
    @validate_arguments
    def set(cls, variable: str, value: Union[str, bytes]) -> bool:
        """
        Set a sysctl variable with a custom value. The value and the variable are shell escaped to
        avoid shell injection.
        Args:
            variable: Variable name. This can contain `.`
            value: value for the variable.

        Returns:
            True if the method was able to set the variable, False otherwise
        """
        # Protect against shell injection vuln using shlex.quote
        if isinstance(value, bytes):
            value = str(value, "UTF-8")
        _variable, _value = shlex.quote(variable), shlex.quote(value)
        _cmd = [cls._cmd, _variable, _value]
        if os.geteuid() != 0:
            _cmd.insert(0, cls._sudo)
        proc = subprocess.run(  # nosec
            _cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode == 0:
            return True
        return False

    @classmethod
    def is_variable(cls, key: str, raise_error: bool = False) -> bool:
        """
        Determine if a key is a valid sysctl variable.
        Args:
            key:
            raise_error: Raise `KeyError` if not a variable

        Raises:
            KeyError: if `raise_error` is True and `key` is not a valid sysctl variable.

        Returns:
            True if valid sysctl variable, False otherwise
        """
        sysctl_var_path = cls.ROOT_PATH.joinpath(key.replace(".", "/"))
        if not sysctl_var_path.is_file():
            if raise_error:
                raise KeyError(
                    "Cannot find {sysctl_var_path}. No such sysctl variable.".format(
                        sysctl_var_path=sysctl_var_path
                    )
                )
            else:
                return False
        return True
