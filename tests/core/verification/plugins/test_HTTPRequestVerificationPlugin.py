#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from unittest import TestCase

from mockito import when, mock
from requests import Response

from vzmi.ychaos.core.verification.plugins.HTTPRequestVerificationPlugin import (
    HTTPRequestVerificationPlugin,
)
from vzmi.ychaos.testplan.verification import HTTPRequestVerification


class TestHTTPVerificationPlugin(TestCase):
    def setUp(self) -> None:
        self.verification_config = HTTPRequestVerification(
            urls=[
                "https://ychaos.yahoo.com",
            ],
            count=1,
        )

    def test_plugin_init(self):
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)
        self.assertDictEqual(verification_plugin._session.headers, dict())
        self.assertIsNone(verification_plugin._session.cert)
        self.assertDictEqual(verification_plugin._session.params, dict())

    def test_plugin_run_verification_for_success_response(self):
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(status_code=200, elapsed=mock(dict(microseconds=34000)), spec=Response)
        )
        when(verification_plugin._session).request(
            "GET", url="https://ychaos.yahoo.com"
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 0)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertListEqual(state_data.data[0], list())

    def test_plugin_run_verification_for_failure_response(self):
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(
                status_code=500,
                elapsed=mock(dict(microseconds=23000)),
                url="https://ychaos.yahoo.com",
            ),
            spec=Response,
        )
        when(verification_plugin._session).request(
            "GET", url="https://ychaos.yahoo.com"
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertDictEqual(
            state_data.data[0][0],
            dict(latency=23.0, status_code=500, url="https://ychaos.yahoo.com"),
        )

    def test_plugin_run_verification_for_latency_above_threshold(self):
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(
                status_code=200,
                elapsed=mock(dict(microseconds=52000)),
                url="https://ychaos.yahoo.com",
            ),
            spec=Response,
        )
        when(verification_plugin._session).request(
            "GET", url="https://ychaos.yahoo.com"
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertDictEqual(
            state_data.data[0][0],
            dict(latency=52.0, status_code=200, url="https://ychaos.yahoo.com"),
        )
