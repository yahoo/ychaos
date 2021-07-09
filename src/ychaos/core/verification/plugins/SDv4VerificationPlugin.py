#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
import time
from datetime import datetime, timedelta
from typing import Any, Dict

import requests
from pydantic import validate_arguments
from requests import HTTPError, Session, Timeout

from ....testplan.verification import SDv4Verification
from ..data import VerificationData, VerificationStateData
from .BaseVerificationPlugin import BaseVerificationPlugin


class SDv4VerificationPlugin(BaseVerificationPlugin):

    __verification_type__ = "sdv4"

    @validate_arguments
    def __init__(
        self,
        config: SDv4Verification,
        state_data: VerificationData = VerificationData.parse_obj(dict()),
    ):
        super(SDv4VerificationPlugin, self).__init__(config, state_data)
        self._session = Session()

    def _get_bearer_token(self):
        response = requests.get(
            url=f"{self.config.sd_api_url}/v4/auth/token",
            params=dict(api_token=self.config.sd_api_token.get_secret_value()),
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("token")

    def _monitor_job(self, sdv4_event: Dict[Any, Any]):

        _job_monitor_end_time = datetime.now() + timedelta(
            seconds=self.config.job_timeout
        )

        event_id = sdv4_event.get("id")
        self.logger.info(
            pipeline_id=self.config.pipeline_id,
            job_name=self.config.job_name,
            event_id=event_id,
            msg="Monitoring SDv4 job",
        )
        while datetime.now() < _job_monitor_end_time:
            sdv4_event_get_response = self._session.get(
                url=f"{self.config.sd_api_url}/v4/events/{event_id}/builds"
            )
            sdv4_event_get_response.raise_for_status()

            sdv4_event_build = sdv4_event_get_response.json()
            build = sdv4_event_build[0]
            if build["status"] in (
                "ABORTED",
                "FAILURE",
                "BLOCKED",
                "UNSTABLE",
                "FROZEN",
            ):
                self.logger.info(
                    status=build["status"], msg="SDv4 job verification failed"
                )
                return VerificationStateData(
                    rc=2,
                    type=self.__verification_type__,
                    data=dict(
                        event_id=build["eventId"],
                        status=build["status"],
                        status_message=build.get("statusMessage", None),
                        job_id=build["jobId"],
                    ),
                )
            elif build["status"] in ("SUCCESS",):
                self.logger.info(
                    status=build["status"], msg="SDv4 job verification successful"
                )
                return VerificationStateData(
                    rc=0,
                    type=self.__verification_type__,
                    data=dict(
                        event_id=build["eventId"],
                        status=build["status"],
                        status_message=build.get("statusMessage", None),
                        job_id=build["jobId"],
                    ),
                )
            else:
                # Status = ("CREATED", "QUEUED", "RUNNING")
                # Wait for 60 seconds and check for the status of the build again
                time.sleep(60)

    def run_verification(self) -> VerificationStateData:
        self.logger.info(msg="Starting SDv4 job verification")
        try:
            bearer_token = self._get_bearer_token()

            self._session.headers["Authorization"] = bearer_token
            self._session.headers["accept"] = "application/json"
            self._session.headers["Content-Type"] = "application/json"

            self.logger.info(
                pipeline_id=self.config.pipeline_id,
                job_name=self.config.job_name,
                msg="Starting SDv4 job",
            )
            sdv4_event_post_response = self._session.post(
                url=f"{self.config.sd_api_url}/v4/events",
                json=dict(
                    causeMessage="YChaos SDv4 Verification",
                    creator=dict(name="ychaos", username="ychaos"),
                    pipelineId=self.config.pipeline_id,
                    startFrom=self.config.job_name,
                ),
            )
            sdv4_event_post_response.raise_for_status()

            self.logger.info(
                pipeline_id=self.config.pipeline_id,
                job_name=self.config.job_name,
                msg="Started SDv4 job",
            )
            time.sleep(2)  # 2 second sleep for SDv4 to start the Job
            return self._monitor_job(sdv4_event_post_response.json())

        except HTTPError as http_error:
            self.logger.info(msg="SDv4 job verification failed")
            return VerificationStateData(
                rc=1,
                type=self.__verification_type__,
                data=dict(
                    url=http_error.response.url,
                    status_code=http_error.response.status_code,
                    json=http_error.response.json(),
                    error=http_error.__class__.__name__,
                ),
            )
        except Timeout as timeout_error:
            self.logger.info(msg="SDv4 job verification failed")
            return VerificationStateData(
                rc=1,
                type=self.__verification_type__,
                data=dict(error=timeout_error.__class__.__name__),
            )
