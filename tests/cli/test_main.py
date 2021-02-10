#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from unittest import TestCase

from vzmi.ychaos.cli.main import YChaos


class TestYChaosCLI(TestCase):
    def test_ychaos_cli_builds(self):
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(["-v"])

        self.assertEqual(0, _exit.exception.code)
