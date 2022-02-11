#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validate_arguments

from ....testplan.verification import OpenTSDBVerification
from ....testplan.verification.plugins.metrics import MetricsComparator
from ....utils.types import Json
from ..data import VerificationData, VerificationStateData
from .BaseVerificationPlugin import RequestVerificationPlugin


class OpenTSDBVerificationPlugin(RequestVerificationPlugin):
    class OpenTSDBVerificationData(BaseModel):
        url: str  # Making this string since this is built with only trusted data
        status_code: Optional[int]
        data: Dict[datetime, float]
        response: Optional[Json]

    __verification_type__ = "tsdb"

    @validate_arguments
    def __init__(
        self,
        config: OpenTSDBVerification,
        state_data: VerificationData = VerificationData.parse_obj(dict()),
    ):
        super(OpenTSDBVerificationPlugin, self).__init__(config, state_data)
        self._session = self._build_session()

    def run_verification(self) -> VerificationStateData:
        _rc = 0

        tsdb_response = self._session.request(
            self.config.method,
            url=str(self.config.url),
            timeout=self.config.timeout / 1000,
            json=self.config.query,
        )

        if tsdb_response.status_code != 200:
            return VerificationStateData(
                rc=-1,
                type=self.__verification_type__,
                data=self.OpenTSDBVerificationData(
                    url=self.config.url,
                    status_code=tsdb_response.status_code,
                    data=dict(),
                    response=tsdb_response.json(),
                ).dict(),
            )

        else:
            if len(self.config.criteria) != 0:
                _rc = self.validate_criteria(tsdb_response.json())
            else:
                # TODO: Verify State Bound Critieria
                pass

        return VerificationStateData(
            rc=_rc, type=self.__verification_type__, data=tsdb_response.json()
        )

    def validate_criteria(self, response_data: List[Dict[str, Any]]):
        def _get_comparator_args(condition, aggregated_data):
            if condition.comparator == MetricsComparator.RANGE:
                return condition._comparator_raw, aggregated_data, condition.value
            return aggregated_data, condition.value

        for _query_data in response_data:

            for _criteria in self.config.criteria:

                _aggregated_data = _criteria.aggregator.metadata.aggregate(  # type: ignore
                    _query_data["dps"]
                )

                for _condition in _criteria.conditionals:
                    if _condition.comparator.metadata.compare(
                        *_get_comparator_args(_condition, _aggregated_data)
                    ):
                        break
                else:
                    return 1

        else:
            return 0
