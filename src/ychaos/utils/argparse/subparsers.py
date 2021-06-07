#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from abc import ABC, abstractmethod
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentError,
    ArgumentParser,
    Namespace,
    _SubParsersAction,
)
from typing import Any, List, Optional

__all__ = ["SubCommandParsersAction", "SubCommand"]


class SubCommandParsersAction(_SubParsersAction):
    """
    Extends the `_SubParsersAction` class of Argparse that can be used for the
    action attribute of `add_subparsers`.

    ```python3
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(action=CommandSubParsersAction)
    ```

    All the parsers added to the `subparsers` using the `add_parser` method will now require a
    mandatory attribute `cls` that implements the base [SubCommand][ychaos.utils.argparse.subparsers.SubCommand] class.
    This overridden method adds a new default variable to the parser named `cls` that can be called during
    parsing arguments

    The `add_parser` method also calls the command class's `build_parser` method that takes in a parser and builds
    arguments, optionals and returns the built parser back.

    ```python3
    parser_foo = subparsers.add_parser(cls=SubCommand1)

    parser_bar = subparsers.add_parser(cls=SubCommand2)

    parsed_args = parser.parse_args()
    parsed_args.cls.main(parsed_args)
    ```

    In the above example, the two sub-commands `SubCommand1.name` and `SubCommand2.name` are
    handled by their respective classes.

    See [SubCommand][ychaos.utils.argparse.subparsers.SubCommand] for more details.
    """

    def add_parser(self, name=None, **kwargs: Any) -> ArgumentParser:
        try:
            cls = kwargs.pop("cls")
            if not issubclass(cls, SubCommand):
                raise ArgumentError(
                    self, "cls attribute must implement SubCommand class"
                )
        except KeyError as e:
            raise ArgumentError(
                self, "cls attribute is required for SubCommandParser object"
            )

        # Class command-name is given more importance
        _name = cls.name or name
        if _name is None:
            raise ArgumentError(self, "Command name cannot be None")

        # Add Aliases from Sub-Command Class
        aliases = kwargs.get("aliases", list())
        aliases.extend(cls.aliases)
        kwargs.update(dict(aliases=aliases))
        kwargs.setdefault("help", cls.help)
        kwargs.setdefault("epilog", cls.epilog)
        kwargs.setdefault("formatter_class", ArgumentDefaultsHelpFormatter)

        parser = super(SubCommandParsersAction, self).add_parser(_name, **kwargs)

        # Set Executable methods for the parser.
        parser.set_defaults(cls=cls)

        return cls.build_parser(parser)


class SubCommand(ABC):
    """
    Abstract base class for an Argparse subcommand. This is used along with the
    [SubCommandParsersAction][ychaos.utils.argparse.subparsers.SubCommandParsersAction].

    The subcommands can implement this method along with adding the action `SubCommandParsersAction` to
    `add_subparsers` method. Each class inheriting the command will implement the `build_parser` method
    to build the sub parser and return the parser.

    On parsing the arguments, the parser's `cls` attribute can be used to run the `main` function.
    """

    name: Optional[str] = None
    help: Optional[str] = None
    aliases: List[str] = list()
    epilog: Optional[str] = None

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        """
        Called from the SubCommandParser to add arguments, parsers to the subparser
        created from Argparse. The subclasses inheriting this class, can add arguments
        to this subparser

        Args:
            parser: Subparser object

        Returns:
            Parser object with arguments, optionals, subparsers attached.
        """
        return parser

    @classmethod
    @abstractmethod
    def main(cls, args: Namespace) -> Any:  # pragma: no cover
        """
        Defines the Program Logic to be executed when this subcommand is invoked. This method
        is called with one argument args of type Namespace which contains the parsed values.

        Args:
            args: Namespace arguments parsed from the input

        Returns:
            Any
        """
        raise NotImplementedError("execute method must be implemented by the subclass")
