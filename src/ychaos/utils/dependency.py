#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import importlib
import warnings
from typing import Any, Optional, Tuple

from pydantic import validate_arguments


class DependencyUtils:
    """
    DependencyUtils provides utility methods to handle and import optional dependencies
    in the YChaos package.
    """

    @classmethod
    def import_module(
        cls, name: str, message: str = None, raise_error: bool = True
    ) -> Optional[Any]:
        """
        Calling this method with a module name is similar to calling
        `import ...`. This can be used to import optional dependencies in the package.

        Args:
            name: Module name
            message: Error message to be printed on console when the import fails
            raise_error: Raise an error if the import fails

        Raises:
            ImportError: when `raise_error` is True and the module is not present

        Returns:
            Optional Module
        """
        try:
            module = importlib.import_module(name)
        except ImportError as import_error:
            if not message:
                message = f"Dependency {name} is not installed."

            warnings.warn(message)
            if raise_error:
                raise ImportError(message) from None
            else:
                return None

        return module

    @classmethod
    @validate_arguments
    def import_from(
        cls,
        module_name: str,
        attrs: Tuple[str, ...],
        message: str = None,
        raise_error: bool = True,
    ) -> Tuple[Any, ...]:
        """
        Calling this method with a module and an attribute is similar to calling
        `from ... import ...`. This can be used to import optional dependency in the package.

        Examples:

            ```python
            from ychaos.utils.dependency import DependencyHandler
            BaseModel, Field = DependencyHandler.import_from("pydantic", ("BaseModel", "Field"))
            ```

            The above code snippet is same as
            ```python
            from pydantic import BaseModel, Field
            ```

        Args:
            module_name: Valid Python Module name
            attrs: Tuple of attribute names from the module
            message: message to be printed in case of an error
            raise_error: Raise an error if the import fails

        Raises:
            ImportError: when `raise_error` is true and `attr_name` cannot be imported from the `module_name`

        Returns:
            An attribute from module_name if exists, None otherwise
        """
        module = cls.import_module(
            name=module_name, message=message, raise_error=raise_error
        )

        if not module:
            return (None,) * len(attrs)
        else:
            _attr_list = list()
            for _attr_name in attrs:
                try:
                    attr = getattr(module, _attr_name)
                    _attr_list.append(attr)
                except AttributeError as attr_error:
                    if not message:
                        message = f"cannot import {_attr_name} from {module_name}"
                    warnings.warn(message)
                    if raise_error:
                        raise ImportError(message) from None
                    else:
                        _attr_list.append(None)
            return tuple(_attr_list)
