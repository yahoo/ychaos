#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import sys
from argparse import Namespace
from tempfile import NamedTemporaryFile
from unittest import TestCase

from mockito import captor, unstub, verify, when

from ychaos.cli import YChaosSubCommand
from ychaos.cli.main import YChaos, main
from ychaos.cli.mock import MockApp


class TestYChaosCLI(TestCase):
    def test_ychaos_cli_builds(self):
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(["-v"])

        self.assertEqual(0, _exit.exception.code)

    def test_ychaos_cli_for_no_subcommand(self):
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main([])

        self.assertEqual(0, _exit.exception.code)

    def test_ychaos_cli_complex_command(self):
        ychaos_command = [
            "ychaos",
            "--log-file",
            "/dev/null",
            "testplan",
            "validate",
            "tests/resources/testplans/valid/",
            "tests/resources/testplans/valid/testplan4.json",
        ]
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command[1:])

        self.assertEqual(1, _exit.exception.code)

    def test_ychaos_cli_manual_command(self):
        ychaos_command = "ychaos manual"
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

        self.assertEqual(0, _exit.exception.code)

    def test_ychaos_cli_manual_command_with_valid_file(self):
        ychaos_command = "ychaos manual --file /dev/null"

        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

        self.assertEqual(0, _exit.exception.code)

    def test_ychaos_cli_manual_command_file_not_found(self):
        ychaos_command = "ychaos manual --file unknownDirectory/validfile.txt"

        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

        self.assertEqual(1, _exit.exception.code)

    def test_ychaos_cli_manual_command_directory(self):
        ychaos_command = "ychaos manual --file /tmp"

        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

        self.assertEqual(1, _exit.exception.code)

    def test_ychaos_cli_saves_reports(self):
        txt_report = NamedTemporaryFile("w+", suffix=".txt")
        html_report = NamedTemporaryFile("w+", suffix=".html")
        ychaos_command = (
            f"ychaos --text-report {txt_report.name} --html-report {html_report.name}"
        )

        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

        self.assertEqual(0, _exit.exception.code)

        txt_report.seek(0)
        self.assertTrue("YChaos, The resilience testing framework" in txt_report.read())

    def test_ychaos_entrypoint(self):
        sys.argv = [
            "ychaos",
        ]
        with self.assertRaises(SystemExit) as _exit:
            main()


class TestYChaosCLIApp(TestCase):
    def test_app_handles_unknown_errors(self):
        args = Namespace()
        app = MockApp(args=args)
        when(app.console).print_exception(extra_lines=2).thenReturn(0)

        app.unknown_error()
        verify(app.console, times=1).print_exception(extra_lines=2)

    def test_app_in_debug_mode(self):
        args = Namespace(debug=True)
        app = MockApp(args=args)
        self.assertTrue(app.is_debug_mode())

    def tearDown(self) -> None:
        unstub()


class TestYChaosCLISubcommand(TestCase):
    def test_subcommand_for_noop(self):
        args = Namespace()
        args.app = MockApp(args=args)
        log_captor = captor()
        when(args.app.console).log(log_captor).thenReturn(0)

        returncode = YChaosSubCommand.main(args)

        self.assertEqual(returncode, 0)
        self.assertEqual(log_captor.value, "This command does nothing..")

    def tearDown(self) -> None:
        unstub()
