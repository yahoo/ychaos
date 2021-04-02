#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import tempfile
from unittest import TestCase

from vzmi.ychaos.app_logger import AppLogger
from vzmi.ychaos.settings import DevSettings, ProdSettings, Settings
from vzmi.ychaos.utils.logging import StructLogger


class TestAppLogger(TestCase):
    def test_logging_prod_setup(self):
        Settings("prod")
        settings: ProdSettings = Settings.get_instance()
        settings.LOG_FILE_PATH = tempfile.NamedTemporaryFile().name
        AppLogger._AppLogger__instance = None

        AppLogger()

        self.assertIsInstance(AppLogger.get_logger("test"), StructLogger)
        self.assertEqual(len(AppLogger._AppLogger__instance.handlers), 1)

    def test_logging_dev_setup(self):
        Settings("dev")
        settings: DevSettings = Settings.get_instance()
        settings.LOG_FILE_PATH = tempfile.NamedTemporaryFile().name
        AppLogger._AppLogger__instance = None

        AppLogger()
        self.assertEqual(len(AppLogger._AppLogger__instance.handlers), 0)

    def test_logging_when_instance_not_initialized(self):
        Settings("prod")
        AppLogger._AppLogger__instance = None
        self.assertIsInstance(AppLogger.get_logger("test"), StructLogger)
