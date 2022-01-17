#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from tempfile import NamedTemporaryFile
from unittest import TestCase

from mockito import mock, unstub, when
from requests import Response

from ychaos.core.verification.plugins.OpenTSDBVerificationPlugin import (
    OpenTSDBVerificationPlugin,
)
from ychaos.testplan.verification import (
    MultipleConditionalsMetricsVerificationCriteria,
    OpenTSDBVerification,
)
from ychaos.testplan.verification.plugins.metrics import ComparisonCondition


class TestOpenTSDBVerificationPlugin(TestCase):
    def setUp(self) -> None:
        file = NamedTemporaryFile()
        self.verification_config = OpenTSDBVerification(
            url="https://tsdb.ychaos.yahoo.com",
            method="POST",
            cert=(file.name, file.name),
            query=dict(),  # For testing only
            criteria=[
                MultipleConditionalsMetricsVerificationCriteria(
                    conditionals=[
                        ComparisonCondition(comparator="==", value=25625991360)
                    ]
                )
            ],
        )

        # Mock Response from http://opentsdb.net/docs/build/html/api_http/query/index.html
        self.mock_tsdb_response = [
            dict(
                metric="tsd.hbase.puts",
                tags={},
                aggregatedTags=["host"],
                annotations=[
                    dict(
                        tsuid="00001C0000FB0000FB",
                        description="Testing Annotations",
                        notes="These would be details about the event, the description is just a summary",
                        custom={"owner": "jdoe", "dept": "ops"},
                        endTime=0,
                        startTime=1365966062,
                    )
                ],
                globalAnnotations=[
                    dict(
                        description="Notice",
                        notes="DAL was down during this period",
                        custom=None,
                        endTime=1365966164,
                        startTime=1365966064,
                    )
                ],
                tsuids=["0023E3000002000008000006000001"],
                dps={
                    "1365966001": 25595461080,
                    "1365966061": 25595542522,
                    "1365966062": 25595543979,
                    "1365973801": 25717417859,
                },
            )
        ]

    def test_plugin_init(self):
        verification_plugin = OpenTSDBVerificationPlugin(self.verification_config)
        self.assertDictEqual(verification_plugin._session.headers, dict())
        self.assertIsNotNone(verification_plugin._session.cert)
        self.assertDictEqual(verification_plugin._session.params, dict())

    def test_plugin_run_verification_for_success_response_from_tsdb(self):
        verification_plugin = OpenTSDBVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(status_code=200, json=lambda: self.mock_tsdb_response, spec=Response)
        )
        when(verification_plugin._session).request(
            "POST",
            url="https://tsdb.ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
            json=dict(),
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()
        self.assertEqual(state_data.rc, 0)

    def test_plugin_run_verification_for_success_response_from_tsdb_fails_validation(
        self,
    ):
        self.verification_config.criteria[0].conditionals[0].value = 0
        verification_plugin = OpenTSDBVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(status_code=200, json=lambda: self.mock_tsdb_response, spec=Response)
        )
        when(verification_plugin._session).request(
            "POST",
            url="https://tsdb.ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
            json=dict(),
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()
        self.assertEqual(state_data.rc, 1)

    def test_plugin_run_verification_for_failure_response(self):
        self.verification_config.criteria[0].conditionals[0].value = 0
        verification_plugin = OpenTSDBVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(status_code=400, json=lambda: self.mock_tsdb_response, spec=Response)
        )
        when(verification_plugin._session).request(
            "POST",
            url="https://tsdb.ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
            json=dict(),
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()
        self.assertEqual(state_data.rc, -1)
        self.assertEqual(state_data.data["status_code"], 400)

    def test_plugin_run_verification_for_success_response_for_no_criteria(
        self,
    ):
        self.verification_config.criteria.pop()
        verification_plugin = OpenTSDBVerificationPlugin(self.verification_config)

        mock_response = mock(
            dict(status_code=200, json=lambda: self.mock_tsdb_response, spec=Response)
        )
        when(verification_plugin._session).request(
            "POST",
            url="https://tsdb.ychaos.yahoo.com",
            timeout=self.verification_config.timeout / 1000,
            json=dict(),
        ).thenReturn(mock_response)

        state_data = verification_plugin.run_verification()
        self.assertEqual(state_data.rc, 0)

    def tearDown(self) -> None:
        unstub()
