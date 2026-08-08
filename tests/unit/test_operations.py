"""Unit tests for the arithmetic functions, with no web layer involved."""

import pytest

from app.operations import add, divide, multiply, subtract


@pytest.mark.parametrize(
    "operation, a, b, expected",
    [
        (add, 23, 34, 57),
        (add, -23, 23, 0),
        (add, 2.5, 2.5, 5.0),
        (add, 0, 0, 0),
        (subtract, 34, 23, 11),
        (subtract, 23, 34, -11),
        (subtract, 2, 2, 0),
        (subtract, 0, 23, -23),
        (multiply, 23, 2, 46),
        (multiply, 34, 0, 0),
        (multiply, -2, 23, -46),
        (multiply, 2.5, 2, 5.0),
        (divide, 34, 2, 17),
        (divide, 23, 2, 11.5),
        (divide, 46, 23, 2),
        (divide, -46, 2, -23),
    ],
)
def test_operations_return_expected(operation, a, b, expected):
    assert operation(a, b) == expected


@pytest.mark.parametrize("a", [23, 0, -34, 2.5])
def test_divide_refuses_a_zero_divisor(a):
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        divide(a, 0)


def test_divide_always_returns_a_float():
    # The docstring promises a float even for whole-number inputs, and
    # the API declares its response as a float too, so it is worth
    # pinning down rather than assuming.
    assert isinstance(divide(46, 2), float)


@pytest.mark.parametrize("operation", [add, subtract, multiply])
def test_integer_inputs_stay_integers(operation):
    assert isinstance(operation(34, 2), int)
