#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import logging
import os
import time
from typing import Optional, Union

from .settings import DevSettings, ProdSettings, Settings
from .utils.logging import StructLogger


class AppLogger:

    __instance: Optional[StructLogger] = None

    def __init__(self):
        """
        Configures the root logger to custom logging structure and adds log handlers based on the env
        """
        settings: Union[DevSettings, ProdSettings] = Settings.get_instance()

        logging.setLoggerClass(StructLogger)
        self.__class__.__instance = logging.getLogger(settings.PROG)
        self.__class__.__instance.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            (
                f"%(asctime)s [%(levelname)-s] host={os.uname()[1]} application=%(name)s module=%(module)s "
                f"method=%(funcName)s line=%(lineno)d %(message)s"
            )
        )
        formatter.converter = time.gmtime
        formatter.datefmt = "%Y-%m-%d %H:%M:%S"

        if settings.CONFIG == "prod" and settings.LOG_FILE_PATH is not None:
            file_handler = logging.FileHandler(settings.LOG_FILE_PATH, "w")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.__class__.__instance.addHandler(file_handler)

    @classmethod
    def get_logger(cls, name: str):
        if cls.__instance is None:
            cls()

        assert isinstance(cls.__instance, StructLogger)
        return cls.__instance.getChild(name)
