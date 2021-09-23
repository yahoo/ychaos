#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from typing import Optional

from pydantic import BaseModel, validate_arguments

from ....testplan.verification import HTTPRequestVerification
from ..data import VerificationData, VerificationStateData
from .BaseVerificationPlugin import RequestVerificationPlugin


class HTTPRequestVerificationPlugin(RequestVerificationPlugin):
    class HttpVerificationData(BaseModel):
        url: str  # Making this string since this is built with only trusted data
        status_code: Optional[int]
        latency: Optional[int]
        error: Optional[str]
        error_desc: Optional[str]

    __verification_type__ = "http_request"

    @validate_arguments
    def __init__(
        self,
        config: HTTPRequestVerification,
        state_data: VerificationData = VerificationData.parse_obj(dict()),
    ):
        super(HTTPRequestVerificationPlugin, self).__init__(config, state_data)
        self._session = self._build_session()

    def run_verification(self) -> VerificationStateData:
        _rc = 0
        _data = list()

        for _ in range(self.config.count):
            counter_data = list()

            for url in self.config.urls:
                try:
                    response = self._session.request(
                        self.config.method,
                        url=str(url),
                        timeout=self.config.timeout / 1000,
                    )
                    if (
                        response.status_code not in self.config.status_codes
                        or (response.elapsed.microseconds / 1000) > self.config.latency
                    ):
                        _rc = 1
                        counter_data.append(
                            self.HttpVerificationData(
                                url=response.url,
                                status_code=response.status_code,
                                latency=response.elapsed.microseconds / 1000,
                            ).dict()
                        )
                except Exception as e:
                    _rc = 1
                    counter_data.append(
                        self.HttpVerificationData(
                            url=str(url), error=e.__class__.__name__, error_desc=str(e)
                        ).dict()
                    )
            _data.append(counter_data)

        return VerificationStateData(
            rc=_rc, type=self.__verification_type__, data=_data
        )
