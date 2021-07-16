#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from datetime import datetime, timedelta
from pathlib import Path
from unittest import TestCase

from parameterized import parameterized
from pydantic import ValidationError

from ychaos.testplan import SystemState
from ychaos.testplan.schema import TestPlan
from ychaos.testplan.verification import OpenTSDBVerification
from ychaos.testplan.verification.plugins.metrics import (
    MetricsAggregator,
    MetricsComparator,
)


class TestMetricsAggregator(TestCase):
    def setUp(self) -> None:
        now = datetime.now()
        self.data = [1, 4, 8, 9, 2]
        self.metrics_fixture = dict()
        for index, datapoint in enumerate(self.data):
            self.metrics_fixture.setdefault(now + timedelta(seconds=index), datapoint)

    @parameterized.expand(
        [
            (MetricsAggregator.AVG.value, MetricsAggregator.AVG, 4.8),
            (MetricsAggregator.LATEST.value, MetricsAggregator.LATEST, 2),
            (MetricsAggregator.OLDEST.value, MetricsAggregator.OLDEST, 1),
            (MetricsAggregator.MAX.value, MetricsAggregator.MAX, 9),
            (MetricsAggregator.MIN.value, MetricsAggregator.MIN, 1),
        ]
    )
    def test_aggregator(self, _, aggregator: MetricsAggregator, expected_data: float):
        avg_value = aggregator.metadata.aggregate(self.metrics_fixture)
        self.assertEqual(avg_value, expected_data)

    def test_aggregator_random(self):
        self.assertTrue(
            MetricsAggregator.RANDOM.metadata.aggregate(self.metrics_fixture)
            in self.data
        )

    def test_aggregator_slope(self):
        with self.assertRaises(NotImplementedError):
            MetricsAggregator.SLOPE.metadata.aggregate(self.metrics_fixture)


class TestMetricsComparator(TestCase):
    def setUp(self) -> None:
        self.data = 0

    @parameterized.expand(
        [
            (MetricsComparator.EQ.value, MetricsComparator.EQ, 0),
            (MetricsComparator.GE.value, MetricsComparator.GE, -1),
            (MetricsComparator.GT.value, MetricsComparator.GT, -1),
            (MetricsComparator.LT.value, MetricsComparator.LT, 1),
            (MetricsComparator.LE.value, MetricsComparator.LE, 1),
            (MetricsComparator.NEQ.value, MetricsComparator.NEQ, 1),
        ]
    )
    def test_metrics_comparator(self, _, comparator: MetricsComparator, expected_data):
        self.assertTrue(comparator.metadata.compare(self.data, expected_data))

    @parameterized.expand(
        [
            ("()", (-1, 1)),
            ("[)", (0, 1)),
            ("[]", (0, 1)),
            ("(]", (-1, 0)),
            ("range", (-1, 1)),
        ]
    )
    def test_range(self, range_type, expected_range):
        self.assertTrue(
            MetricsComparator.RANGE.metadata.compare(
                range_type, self.data, expected_range
            )
        )

    def test_pct_compare(self):
        self.assertTrue(MetricsComparator.PCT.metadata.compare(10, 4, 150))
        self.assertTrue(MetricsComparator.PCT.metadata.compare(10, 4, (125, 175)))


class TestStateBoundMetricsVerificationCriteria(TestCase):
    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_get_criteria(self):
        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan7.yaml")
        )
        verification_config = testplan.verification[0].get_verification_config()
        self.assertIsInstance(verification_config, OpenTSDBVerification)
        comparator = verification_config.state_bound_criteria[0].get_criteria(
            SystemState.STEADY
        )
        self.assertEqual(MetricsComparator.LE, comparator.comparator)
        self.assertEqual("<=", comparator._comparator)
        self.assertEqual(300, comparator.value)

    def test_metrics_when_no_criteria_is_defined(self):
        with self.assertRaises(ValidationError):
            OpenTSDBVerification(url="https://mock.metrics.reslience.yahoo.com")
