#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

import logging
import os
import time
from tempfile import NamedTemporaryFile
from typing import Optional, Union

from vzmi.ychaos.settings import DevSettings, ProdSettings, Settings
from vzmi.ychaos.utils.logging import StructLogger


class AppLogger:

    __instance: Optional[StructLogger] = None

    def __init__(self):
        """
        Configures the root logger to custom logging structure and adds log handlers based on the env
        """
        if not self.__class__.__instance:
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

            if settings.CONFIG == "prod":
                settings.LOG_FILE_PATH = NamedTemporaryFile(
                    delete=False,
                    prefix=settings.PROG,
                    suffix=settings.LOG_FILE_NAME_SUFFIX,
                ).name

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
