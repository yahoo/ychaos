from unittest import TestCase

from vzmi.ychaos.cli.main import YChaos


class TestYChaosCLI(TestCase):
    def test_ychaos_cli_builds(self):
        with self.assertRaises(SystemExit) as _exit:
            YChaos.main(["-v"])

        self.assertEqual(0, _exit.exception.code)
