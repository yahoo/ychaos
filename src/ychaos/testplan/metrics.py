import math
import random
from datetime import datetime
from types import SimpleNamespace
from typing import Dict, List

from pydantic import Field

from ..utils.builtins import AEnum, BuiltinUtils
from . import SchemaModel


class TimeSeriesDataAggregator:
    @classmethod
    def get_filtered_data(cls, data: Dict[datetime, float]) -> Dict[datetime, float]:
        """
        Filter the time series data by removing NAN data
        Args:
            data: Time series data

        Returns:
            Filtered data
        """
        return dict([(_k, _v) for _k, _v in data.items() if not math.isnan(_v)])

    @classmethod
    def avg(cls, data: Dict[datetime, float]) -> float:
        """
        Returns the Average value of a time series data filtering out NAN
        Args:
            data: Time series data

        Returns:
            Average value over the time
        """
        _filtered_data = cls.get_filtered_data(data)
        return BuiltinUtils.return_if_true(
            sum(_filtered_data.values()) / len(_filtered_data),
            _filtered_data,
            BuiltinUtils.Float.NAN,
        )

    @classmethod
    def latest(cls, data: Dict[datetime, float]) -> float:
        """
        Returns the latest value of a time series data filtering out NAN
        Args:
            data: Time series data

        Returns:
            Latest value over the time
        """
        _filtered_data = cls.get_filtered_data(data)
        return BuiltinUtils.return_if_true(
            _filtered_data[max(_filtered_data)], _filtered_data, BuiltinUtils.Float.NAN
        )

    @classmethod
    def oldest(cls, data: Dict[datetime, float]) -> float:
        """
        Returns the oldest value of a time series data filtering out NAN
        Args:
            data: Time series data

        Returns:
            Latest value over the time
        """
        _filtered_data = cls.get_filtered_data(data)
        return BuiltinUtils.return_if_true(
            _filtered_data[min(_filtered_data)], _filtered_data, BuiltinUtils.Float.NAN
        )

    @classmethod
    def max(cls, data: Dict[datetime, float]) -> float:
        """
        Returns the max value of a time series data filtering out NAN
        Args:
            data: Time series data

        Returns:
            Max value
        """
        _filtered_data = cls.get_filtered_data(data)
        return BuiltinUtils.return_if_true(
            max(_filtered_data.values()), _filtered_data, BuiltinUtils.Float.NAN
        )

    @classmethod
    def min(cls, data: Dict[datetime, float]) -> float:
        """
        Returns the min value of a time series data filtering out NAN
        Args:
            data: Time series data

        Returns:
            Min value
        """
        _filtered_data = cls.get_filtered_data(data)
        return BuiltinUtils.return_if_true(
            min(_filtered_data.values()), _filtered_data, BuiltinUtils.Float.NAN
        )

    @classmethod
    def random(cls, data: Dict[datetime, float]) -> float:
        """
        Returns the random value of a time series data filtering out NAN
        Args:
            data: Time series data

        Returns:
            Random value
        """
        _filtered_data = cls.get_filtered_data(data)
        return BuiltinUtils.return_if_true(
            random.choice(  # nosec : Not using for Crypto purpose
                list(_filtered_data.values())
            ),
            _filtered_data,
            BuiltinUtils.Float.NAN,
        )


class MetricsAggregator(AEnum):
    """
    The Metrics aggregator options. Allows the user to transform the
    time series data into some comparable data.
    """

    AVG = "avg", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.avg,
        description="Gets the Average of all the datapoints",
    )

    LATEST = "latest", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.latest,
        description="Gets the latest valid datapoint",
    )

    OLDEST = "oldest", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.oldest,
        description="Gets the oldest valid datapoint",
    )

    RANDOM = "random", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.random,
        description="Gets a random valid datapoint",
    )

    MAX = "max", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.max,
        description="Gets the largest valid datapoint",
    )

    MIN = "min", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.min,
        description="Gets the smallest valid datapoint",
    )

    SLOPE = "slope", SimpleNamespace(
        aggregate=lambda: BuiltinUtils.raise_error(
            NotImplementedError("This aggregator is not implemented")
        ),
        description="Gets the slope of the datapoints",
    )


class MetricsComparator(AEnum):

    LT = "lt", SimpleNamespace(
        aliases=("<",), compare=lambda data, expected: data < expected
    )

    LE = "le", SimpleNamespace(
        aliases=("<=",), compare=lambda data, expected: data <= expected
    )

    GT = "gt", SimpleNamespace(
        aliases=(">",), compare=lambda data, expected: data > expected
    )

    GE = "ge", SimpleNamespace(
        aliases=(">=",), compare=lambda data, expected: data >= expected
    )

    EQ = "eq", SimpleNamespace(
        aliases=("==",), compare=lambda data, expected: data == expected
    )

    NEQ = "neq", SimpleNamespace(
        aliases=("!=",), compare=lambda data, expected: data != expected
    )


class ComparisonCondition(SchemaModel):

    comparator: MetricsComparator = Field(
        ...,
        description="Comparison condition to compare between the metrics data and fetched value",
    )

    value: float = Field(..., description="Numerical value to be used for comparison")


class MetricsVerificationCriteria(SchemaModel):
    """
    Defines the Metrics Verification criteria
    """

    aggeragator: MetricsAggregator = Field(
        default=MetricsAggregator.AVG, description="Data aggregator"
    )

    conditionals: List[ComparisonCondition] = Field(
        min_items=1,
        description="The conditionals out of which any one needs to pass for the criteria to be marked as passed",
    )
