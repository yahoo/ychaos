from unittest import TestCase
from pathlib import Path
from typing import Union
from vzmi.ychaos.settings import DevSettings, ProdSettings, Settings
from vzmi.ychaos.app_logger import AppLogger


class TestAppLogger(TestCase):
    def test_logging_prod_setup(self):
        Settings("prod")
        settings: Union[DevSettings, ProdSettings] = Settings.get_instance()
        AppLogger._AppLogger__instance = None
        logger = AppLogger.get_logger("test")
        AppLogger.get_logger("test1")
        self.assertTrue(Path(settings.LOG_FILE_PATH).is_file())
        print(settings.LOG_FILE_PATH)

        logger.bind(env="prod", name="test")
        logger.debug("testing")
        logger.info("testing", name="ychaos")
        logger.unbind(("env",))
        logger.warning("testing")
        logger.unbind()
        logger.error("testing")
        logger.exception("testing")
        logger.unbind()

    def test_logging_dev_setup(self):
        Settings("dev")
        settings: Union[DevSettings, ProdSettings] = Settings.get_instance()
        AppLogger()
        AppLogger().get_logger("test1").info(env="dev")
        self.assertFalse(Path(settings.LOG_FILE_PATH).is_file())
