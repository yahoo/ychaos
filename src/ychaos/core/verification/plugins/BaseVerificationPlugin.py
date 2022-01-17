#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from abc import ABC, abstractmethod

import requests
from requests import Session

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


class RequestVerificationPlugin(BaseVerificationPlugin, ABC):
    def _build_session(self):
        session = Session()

        session.params = self.config.params
        session.headers = self.config.headers

        if not self.config.verify:
            # Disable Insecure Request Warning if verify=False (Users know what they are doing)
            from requests.packages.urllib3.exceptions import (
                InsecureRequestWarning,
            )

            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        session.verify = self.config.verify

        if self.config.basic_auth:
            session.auth = (
                self.config.basic_auth[0],
                self.config.basic_auth[1].get_secret_value(),
            )

        if self.config.bearer_token:
            session.headers["Authorization"] = (
                "Bearer " + self.config.bearer_token.get_secret_value()
            )

        session.cert = self.config.get_request_cert()

        return session

    @abstractmethod
    def run_verification(self) -> VerificationStateData:
        pass  # Abstract method
