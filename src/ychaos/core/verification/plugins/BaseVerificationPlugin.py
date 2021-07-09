#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from abc import abstractmethod

from ....app_logger import AppLogger
from ..data import VerificationData, VerificationStateData


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
