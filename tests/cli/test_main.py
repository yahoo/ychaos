#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from unittest import TestCase

from ychaos.cli.main import YChaos


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
