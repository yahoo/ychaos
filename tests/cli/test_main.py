#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from unittest import TestCase

from vzmi.ychaos.cli.main import YChaos


class TestYChaosCLI(TestCase):
    def test_ychaos_cli_builds(self):
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(["-v"])

        self.assertEqual(0, _exit.exception.code)

    def test_ychaos_cli_complex_command(self):
        ychaos_command = "ychaos testplan validate tests/resources/testplans/valid/ tests/resources/testplans/valid/testplan4.json"
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

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
        ychaos_command = "ychaos manual --file vzmi/"

        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(ychaos_command.split()[1:])

        self.assertEqual(1, _exit.exception.code)
