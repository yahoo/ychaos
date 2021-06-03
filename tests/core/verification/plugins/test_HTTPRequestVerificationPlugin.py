#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from unittest import TestCase

import requests
from mockito import mock, unstub, when
from pydantic import SecretStr
from requests import Response

from ychaos.core.verification.plugins.HTTPRequestVerificationPlugin import (
    HTTPRequestVerificationPlugin,
)
from ychaos.testplan.verification import HTTPRequestVerification


class TestHTTPVerificationPlugin(TestCase):
    def setUp(self) -> None:
        self.verification_config = HTTPRequestVerification(
            urls=[
                "https://ychaos.yahoo.com",
            ],
            count=1,
            method="GET",
        )

    def test_plugin_for_unknown_http_method(self):
        with self.assertRaises(ValueError):
            HTTPRequestVerification(
                urls=[
                    "https://ychaos.yahoo.com",
                ],
                method="UNKNOWN",
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
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
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
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertDictEqual(
            state_data.data[0][0],
            dict(
                latency=23.0,
                status_code=500,
                url="https://ychaos.yahoo.com",
                error=None,
                error_desc=None,
            ),
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
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertDictEqual(
            state_data.data[0][0],
            dict(
                latency=52.0,
                status_code=200,
                url="https://ychaos.yahoo.com",
                error=None,
                error_desc=None,
            ),
        )

    def test_plugin_run_verification_for_request_raises_timeout(self):
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)

        when(verification_plugin._session).request(
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
        ).thenRaise(requests.Timeout)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 1)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertDictEqual(
            state_data.data[0][0],
            dict(
                latency=None,
                status_code=None,
                url="https://ychaos.yahoo.com",
                error="Timeout",
                error_desc="",
            ),
        )

    def test_plugin_run_verification_for_verify_set_to_false(self):
        self.verification_config.verify = False

        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)
        self.assertEqual(verification_plugin._session.verify, False)

        mock_response = mock(
            dict(status_code=200, elapsed=mock(dict(microseconds=34000)), spec=Response)
        )
        when(verification_plugin._session).request(
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 0)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertListEqual(state_data.data[0], list())

    def test_plugin_run_verification_with_basic_auth(self):
        self.verification_config.basic_auth = "mock_username", SecretStr(
            "mock_password"
        )
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)
        self.assertTupleEqual(
            verification_plugin._session.auth, ("mock_username", "mock_password")
        )

        mock_response = mock(
            dict(status_code=200, elapsed=mock(dict(microseconds=34000)), spec=Response)
        )
        when(verification_plugin._session).request(
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 0)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertListEqual(state_data.data[0], list())

    def test_plugin_run_verification_with_bearer_token(self):
        self.verification_config.bearer_token = SecretStr("mock_token")
        verification_plugin = HTTPRequestVerificationPlugin(self.verification_config)
        self.assertDictEqual(
            verification_plugin._session.headers,
            dict(Authorization="Bearer mock_token"),
        )

        mock_response = mock(
            dict(status_code=200, elapsed=mock(dict(microseconds=34000)), spec=Response)
        )
        when(verification_plugin._session).request(
            "GET",
            url="https://ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()

        self.assertEqual(state_data.rc, 0)
        self.assertEqual(len(state_data.data), self.verification_config.count)
        self.assertListEqual(state_data.data[0], list())

    def tearDown(self) -> None:
        unstub()
