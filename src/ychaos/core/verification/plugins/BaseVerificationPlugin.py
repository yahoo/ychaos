#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from abc import abstractmethod

from ychaos.app_logger import AppLogger
from ychaos.core.verification.data import (
    VerificationData,
    VerificationStateData,
)


class BaseVerificationPlugin:

    __verification_type__: str

    def __init__(
        self,
        config,
        state_data: VerificationData = VerificationData.parse_obj(dict()),
        **kwargs
    ):
        self.config = config
        self.state_data = state_data
        self.logger = AppLogger.get_logger(self.__class__.__name__)

        self.logger.bind(event="verification", type=self.__verification_type__)

    @abstractmethod
    def run_verification(self) -> VerificationStateData:
        pass  # Abstract method
