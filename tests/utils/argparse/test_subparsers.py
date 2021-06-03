#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import argparse
from argparse import ArgumentParser, Namespace
from typing import Any
from unittest import TestCase

from ychaos.utils.argparse import SubCommand, SubCommandParsersAction


class SubCommandMock(SubCommand):
    name = "mock"

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument("-x", type=int, default=10)
        super(SubCommandMock, cls).build_parser(parser)

    @classmethod
    def main(cls, args: Namespace) -> Any:
        return args


class TestSubCommand(TestCase):
    def setUp(self):
        # create the top-level parser
        self.main_parser = argparse.ArgumentParser()
        self.subparsers = self.main_parser.add_subparsers(
            action=SubCommandParsersAction, dest="subcommand_name"
        )
        self.assertTrue(isinstance(self.subparsers, SubCommandParsersAction))

    def test_subcommand_build_parser(self):
        self.subparsers.add_parser(cls=SubCommandMock)

        args = self.main_parser.parse_args("mock -x 50".split())

        self.assertEqual(args.x, 50)
        self.assertEqual(args.cls, SubCommandMock)
        self.assertEqual(args.subcommand_name, SubCommandMock.name)

    def test_subcommand_with_command_name_none(self):
        SubCommandMock.name = None
        with self.assertRaises(argparse.ArgumentError):
            self.subparsers.add_parser(cls=SubCommandMock)

    def test_subcommand_with_no_cls(self):
        with self.assertRaises(argparse.ArgumentError):
            self.subparsers.add_parser()

    def test_subcommand_with_cls_not_inherited_from_subcommand_class(self):
        class InvalidSubCommand:
            pass

        with self.assertRaises(argparse.ArgumentError):
            self.subparsers.add_parser(cls=InvalidSubCommand)
