#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

import math
import random
from datetime import datetime
from types import SimpleNamespace
from typing import Dict, List, Tuple, Union

from pydantic import Field, validate_arguments, validator

from ....utils.builtins import AEnum, BuiltinUtils
from ... import SchemaModel, SystemState


class TimeSeriesDataAggregator:
    """
    The class containing the implementations of different Time Series data Aggregator
    """

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
    The Metrics aggregator options. Allows the user to transform a
    time series data into comparable data.
    """

    AVG = "avg", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.avg,
        __desc__="Gets the Average of all valid datapoints",
    )

    LATEST = "latest", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.latest,
        __desc__="Gets the latest valid datapoint",
    )

    OLDEST = "oldest", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.oldest,
        __desc__="Gets the oldest valid datapoint",
    )

    RANDOM = "random", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.random,
        __desc__="Gets a random valid datapoint",
    )

    MAX = "max", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.max,
        __desc__="Gets the largest valid datapoint",
    )

    MIN = "min", SimpleNamespace(
        aggregate=TimeSeriesDataAggregator.min,
        __desc__="Gets the smallest valid datapoint",
    )

    SLOPE = "slope", SimpleNamespace(
        aggregate=lambda data: BuiltinUtils.raise_error(
            NotImplementedError("This aggregator is not implemented")
        ),
        __desc__="Gets the slope of the datapoints",
    )


class MetricsComparator(AEnum):

    LT = "lt", SimpleNamespace(
        __aliases__=("<",),
        compare=lambda data, expected: data < expected,
        relational=True,
    )

    LE = "le", SimpleNamespace(
        __aliases__=("<=",),
        compare=lambda data, expected: data <= expected,
        relational=True,
    )

    GT = "gt", SimpleNamespace(
        __aliases__=(">",),
        compare=lambda data, expected: data > expected,
        relational=True,
    )

    GE = "ge", SimpleNamespace(
        __aliases__=(">=",),
        compare=lambda data, expected: data >= expected,
        relational=True,
    )

    EQ = "eq", SimpleNamespace(
        __aliases__=("==",),
        compare=lambda data, expected: data == expected,
        relational=True,
    )

    NEQ = "neq", SimpleNamespace(
        __aliases__=("!=",),
        compare=lambda data, expected: data != expected,
        relational=True,
    )

    RANGE = "range", SimpleNamespace(
        __aliases__=("()", "(]", "[)", "[]"),
        compare=lambda range_type, data, expected_range: MetricsComparator.range_compare(  # type: ignore
            range_type, data, expected_range
        ),
        relational=False,
    )

    # The below comparators can only be used for state bound criteria

    PCT = "pct", SimpleNamespace(
        __aliases__=("%%",),
        compare=lambda new_data, old_data, expected: MetricsComparator.pct_compare(  # type: ignore
            new_data, old_data, expected
        ),
        relational=False,
    )

    @classmethod
    @validate_arguments
    def pct_compare(
        cls, new_data: float, old_data: float, expected: Union[float, Tuple]
    ) -> bool:
        """
        Calculate the percentage variation from new_val and old_val

        Args:
            new_data: New Value from data
            old_data: Old value from saved data
            expected: Expected percentage change

        Returns:
            True if the condition meets
        """
        pct_change = ((new_data - old_data) / old_data) * 100
        if isinstance(expected, tuple):
            return (
                BuiltinUtils.Float.parse(expected[0], -math.inf)
                <= pct_change
                <= BuiltinUtils.Float.parse(expected[1], math.inf)
            )
        else:
            return pct_change == expected

    @classmethod
    @validate_arguments
    def range_compare(
        cls,
        range_type: str,
        data: float,
        expected_range: Tuple,
    ) -> bool:
        """

        Args:
            range_type: The range type that depicts inclusiveness
            data: Data to be compared
            expected_range: Expected range for the data to be within

        Returns:

        """
        if range_type == MetricsComparator.RANGE.value:
            range_type = "()"

        if range_type == "()":
            return (
                BuiltinUtils.Float.parse(expected_range[0], -math.inf)
                < data
                < BuiltinUtils.Float.parse(expected_range[1], math.inf)
            )
        elif range_type == "[)":
            return (
                BuiltinUtils.Float.parse(expected_range[0], -math.inf)
                <= data
                < BuiltinUtils.Float.parse(expected_range[1], math.inf)
            )
        elif range_type == "(]":
            return (
                BuiltinUtils.Float.parse(expected_range[0], -math.inf)
                < data
                <= BuiltinUtils.Float.parse(expected_range[1], math.inf)
            )
        else:
            return (
                BuiltinUtils.Float.parse(expected_range[0], -math.inf)
                <= data
                <= BuiltinUtils.Float.parse(expected_range[1], math.inf)
            )


class ComparisonCondition(SchemaModel):

    comparator: MetricsComparator = Field(
        ...,
        description="Comparison condition to compare between the metrics data and fetched value",
    )

    value: Union[float, Tuple] = Field(
        ..., description="Numerical value/range to be used for comparison"
    )

    # Resolve Aliases
    @validator("comparator", pre=True)
    def resolve_comparator(cls, v, values):
        values["_comparator"] = v  # Store the actual value in a private attribute
        return v


class MultipleConditionalsMetricsVerificationCriteria(SchemaModel):
    """
    Defines the Metrics Verification criteria
    """

    aggeragator: MetricsAggregator = Field(
        default=MetricsAggregator.AVG, description="Data aggregator"
    )

    conditionals: List[ComparisonCondition] = Field(
        default=list(),
        description="The conditionals out of which any one needs to pass for the criteria to be marked as passed",
    )


class StateBoundMetricsVerificationCriteria(SchemaModel):

    aggeragator: MetricsAggregator = Field(
        default=MetricsAggregator.AVG, description="Data aggregator"
    )

    criteria: Dict[SystemState, ComparisonCondition] = Field(
        ...,
        description="Metrics verification criteria with state.",
    )

    def get_criteria(self, state: SystemState):
        return self.criteria[state.value]  # type: ignore

    class Config:
        use_enum_values = True  # To make the model JSON serializable
