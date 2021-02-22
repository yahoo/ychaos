from unittest import TestCase
from pathlib import Path
from vzmi.ychaos.settings import DevSettings, ProdSettings, Settings
from vzmi.ychaos.app_logger import AppLogger
from vzmi.ychaos.utils.logging import StructLogger


class TestAppLogger(TestCase):
    def test_logging_prod_setup(self):
        Settings("prod")
        settings: ProdSettings = Settings.get_instance()
        AppLogger._AppLogger__instance = None

        AppLogger()

        self.assertIsInstance(AppLogger.get_logger("test"), StructLogger)
        self.assertTrue(Path(settings.LOG_FILE_PATH).is_file())

    def test_logging_dev_setup(self):
        Settings("dev")
        settings: DevSettings = Settings.get_instance()
        AppLogger._AppLogger__instance = None

        AppLogger()
        self.assertFalse(Path(settings.LOG_FILE_PATH).is_file())

    def test_logging_when_instance_not_initialized(self):
        Settings("prod")
        settings: ProdSettings = Settings.get_instance()
        AppLogger._AppLogger__instance = None

        self.assertIsInstance(AppLogger.get_logger("test"), StructLogger)
        self.assertTrue(Path(settings.LOG_FILE_PATH).is_file())
