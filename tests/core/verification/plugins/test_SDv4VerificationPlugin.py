#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
import time
from unittest import TestCase

import requests
from mockito import when, mock, ANY, unstub
from requests import Response

from vzmi.ychaos.core.verification.plugins.SDv4VerificationPlugin import (
    SDv4VerificationPlugin,
)
from vzmi.ychaos.testplan.verification import SDv4Verification


class TestSDv4VerificationPlugin(TestCase):
    def setUp(self) -> None:
        self.verification_config = SDv4Verification(
            pipeline_id=123456,
            job_name="mock_verify",
            sd_api_url="https://api.screwdriver.ouroath.com",
            sd_api_token="test_token",
        )

    def test_sdv4_verification_execute_when_bearer_token_generation_failed(self):
        verification_plugin = SDv4VerificationPlugin(config=self.verification_config)

        mock_response = mock(
            dict(
                status_code=400,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/auth/token",
            ),
            spec=Response,
        )
        when(mock_response).raise_for_status().thenRaise(
            requests.HTTPError(response=mock_response)
        )

        when(requests).get(
            url="https://api.screwdriver.ouroath.com/v4/auth/token",
            params=dict(api_token="test_token"),
            timeout=10,
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertDictEqual(
            state_data.data,
            dict(
                url="https://api.screwdriver.ouroath.com/v4/auth/token",
                status_code=400,
                json=dict(),
                error="HTTPError",
            ),
        )

    def test_sdv4_verification_execute_when_bearer_token_generation_failed_with_timeout(
        self,
    ):
        verification_plugin = SDv4VerificationPlugin(config=self.verification_config)

        when(requests).get(
            url="https://api.screwdriver.ouroath.com/v4/auth/token",
            params=dict(api_token="test_token"),
            timeout=10,
        ).thenRaise(requests.Timeout)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertDictEqual(state_data.data, dict(error="Timeout"))

    def test_sdv4_verification_execute_job_start_failed(self):
        verification_plugin = SDv4VerificationPlugin(config=self.verification_config)

        # Mock for Token fetch
        mock_response = mock(
            dict(
                status_code=200,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/auth/token",
            ),
            spec=Response,
        )
        when(mock_response).raise_for_status().thenReturn(None)
        when(requests).get(
            url="https://api.screwdriver.ouroath.com/v4/auth/token",
            params=dict(api_token="test_token"),
            timeout=10,
        ).thenReturn(mock_response)

        # Mock for Event start
        mock_response_event_start = mock(
            dict(
                status_code=400,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/events",
            ),
            spec=Response,
        )
        when(mock_response_event_start).raise_for_status().thenRaise(
            requests.HTTPError(response=mock_response_event_start)
        )
        when(verification_plugin._session).post(
            url="https://api.screwdriver.ouroath.com/v4/events", json=ANY
        ).thenReturn(mock_response_event_start)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertDictEqual(
            state_data.data,
            dict(
                url="https://api.screwdriver.ouroath.com/v4/events",
                status_code=400,
                json=dict(),
                error="HTTPError",
            ),
        )

    def test_sdv4_verification_monitor_job_failed_with_http_error(self):
        verification_plugin = SDv4VerificationPlugin(config=self.verification_config)

        # Mock for Token fetch
        mock_response = mock(
            dict(
                status_code=200,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/auth/token",
            ),
            spec=Response,
        )
        when(mock_response).raise_for_status().thenReturn(None)
        when(requests).get(
            url="https://api.screwdriver.ouroath.com/v4/auth/token",
            params=dict(api_token="test_token"),
            timeout=10,
        ).thenReturn(mock_response)

        # Mock for Event start
        mock_response_event_start = mock(
            dict(
                status_code=200,
                json=lambda: dict(id=98765432),
                url="https://api.screwdriver.ouroath.com/v4/events",
            ),
            spec=Response,
        )
        when(mock_response_event_start).raise_for_status().thenReturn(None)
        when(verification_plugin._session).post(
            url="https://api.screwdriver.ouroath.com/v4/events", json=ANY
        ).thenReturn(mock_response_event_start)

        # Mock for Event monitor
        mock_response_event_monitor = mock(
            dict(
                status_code=404,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds",
            ),
            spec=Response,
        )
        when(mock_response_event_monitor).raise_for_status().thenRaise(
            requests.HTTPError(response=mock_response_event_monitor)
        )
        when(verification_plugin._session).get(
            url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds"
        ).thenReturn(mock_response_event_monitor)

        when(time).sleep(ANY).thenReturn(None)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertDictEqual(
            state_data.data,
            dict(
                url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds",
                status_code=404,
                json=dict(),
                error="HTTPError",
            ),
        )

    def test_sdv4_verification_monitor_job_failed_with_job_failure(self):
        verification_plugin = SDv4VerificationPlugin(config=self.verification_config)

        # Mock for Token fetch
        mock_response = mock(
            dict(
                status_code=200,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/auth/token",
            ),
            spec=Response,
        )
        when(mock_response).raise_for_status().thenReturn(None)
        when(requests).get(
            url="https://api.screwdriver.ouroath.com/v4/auth/token",
            params=dict(api_token="test_token"),
            timeout=10,
        ).thenReturn(mock_response)

        # Mock for Event start
        mock_response_event_start = mock(
            dict(
                status_code=200,
                json=lambda: dict(id=98765432),
                url="https://api.screwdriver.ouroath.com/v4/events",
            ),
            spec=Response,
        )
        when(mock_response_event_start).raise_for_status().thenReturn(None)
        when(verification_plugin._session).post(
            url="https://api.screwdriver.ouroath.com/v4/events", json=ANY
        ).thenReturn(mock_response_event_start)

        # Mock for Event monitor
        mock_response_event_monitor = mock(
            dict(
                status_code=200,
                json=lambda: [dict(status="FAILURE", eventId=98765432, jobId=88888)],
                url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds",
            ),
            spec=Response,
        )
        when(mock_response_event_monitor).raise_for_status().thenReturn(None)
        when(verification_plugin._session).get(
            url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds"
        ).thenReturn(mock_response_event_monitor)

        when(time).sleep(ANY).thenReturn(None)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 2)
        self.assertDictEqual(
            state_data.data,
            dict(
                event_id=98765432, job_id=88888, status="FAILURE", status_message=None
            ),
        )

    def test_sdv4_verification_monitor_job_failed_with_job_success(self):
        verification_plugin = SDv4VerificationPlugin(config=self.verification_config)

        # Mock for Token fetch
        mock_response = mock(
            dict(
                status_code=200,
                json=lambda: dict(),
                url="https://api.screwdriver.ouroath.com/v4/auth/token",
            ),
            spec=Response,
        )
        when(mock_response).raise_for_status().thenReturn(None)
        when(requests).get(
            url="https://api.screwdriver.ouroath.com/v4/auth/token",
            params=dict(api_token="test_token"),
            timeout=10,
        ).thenReturn(mock_response)

        # Mock for Event start
        mock_response_event_start = mock(
            dict(
                status_code=200,
                json=lambda: dict(id=98765432),
                url="https://api.screwdriver.ouroath.com/v4/events",
            ),
            spec=Response,
        )
        when(mock_response_event_start).raise_for_status().thenReturn(None)
        when(verification_plugin._session).post(
            url="https://api.screwdriver.ouroath.com/v4/events", json=ANY
        ).thenReturn(mock_response_event_start)

        # Mock for Event monitor (1)
        mock_response_event_monitor_1 = mock(
            dict(
                status_code=200,
                json=lambda: [dict(status="QUEUED", eventId=98765432, jobId=88888)],
                url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds",
            ),
            spec=Response,
        )
        when(mock_response_event_monitor_1).raise_for_status().thenReturn(None)

        # Mock for Event monitor (2)
        mock_response_event_monitor_2 = mock(
            dict(
                status_code=200,
                json=lambda: [dict(status="SUCCESS", eventId=98765432, jobId=88888)],
                url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds",
            ),
            spec=Response,
        )
        when(mock_response_event_monitor_2).raise_for_status().thenReturn(None)

        when(verification_plugin._session).get(
            url="https://api.screwdriver.ouroath.com/v4/events/98765432/builds"
        ).thenReturn(mock_response_event_monitor_1).thenReturn(
            mock_response_event_monitor_2
        )

        when(time).sleep(ANY).thenReturn(None)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 0)
        self.assertDictEqual(
            state_data.data,
            dict(
                event_id=98765432, job_id=88888, status="SUCCESS", status_message=None
            ),
        )

    def tearDown(self) -> None:
        unstub()
