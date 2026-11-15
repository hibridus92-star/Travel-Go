"""Tests for the money helpers: price validation and reading saved prices."""
from decimal import Decimal

import pytest

from exceptions.errors import ActivityError, InvalidPriceError
from models.money import parse_price, price_from_json


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("10"), "10.00"),
        (Decimal("10.500"), "10.50"),  # a trailing zero is not a third decimal
        (10, "10.00"),
        ("25.90", "25.90"),
        ("25.9", "25.90"),
        (" 7.5 ", "7.50"),
        (Decimal("0"), "0.00"),  # free activities are allowed
        (0, "0.00"),
        ("-0", "0.00"),  # a negative zero is shown as plain zero
    ],
)
def test_valid_prices_are_stored_with_exactly_two_decimals(value: object, expected: str) -> None:
    result: Decimal = parse_price(value)  # type: ignore[arg-type]
    assert isinstance(result, Decimal)
    assert str(result) == expected


@pytest.mark.parametrize(
    "bad_value",
    [
        -1,
        "-0.01",
        Decimal("-5.00"),
        "12.345",
        Decimal("0.001"),
        "abc",
        "",
        "NaN",
        Decimal("Infinity"),
        Decimal("1E+30"),  # too large to keep two decimals
        9.99,  # floats are never accepted
        0.0,
        True,  # bool is an int in Python, but it is not a price
        None,
        [10],
    ],
)
def test_invalid_prices_are_rejected_and_keep_the_offending_value(bad_value: object) -> None:
    with pytest.raises(InvalidPriceError) as error:
        parse_price(bad_value)  # type: ignore[arg-type]
    assert error.value.price is bad_value


def test_the_error_explains_why_the_price_was_rejected() -> None:
    with pytest.raises(InvalidPriceError) as negative:
        parse_price("-1")
    with pytest.raises(InvalidPriceError) as too_precise:
        parse_price("1.234")
    with pytest.raises(InvalidPriceError) as float_price:
        parse_price(1.5)

    assert "negative" in negative.value.reason
    assert "two decimals" in too_precise.value.reason
    assert "float" in float_price.value.reason


def test_decimal_sums_are_exact() -> None:
    assert parse_price("0.10") + parse_price("0.20") == parse_price("0.30")


def test_price_errors_belong_to_the_activity_error_family() -> None:
    with pytest.raises(ActivityError):
        parse_price("-1")


# --- reading prices from saved files --------------------------------------

@pytest.mark.parametrize(
    ("saved", "expected"),
    [
        ("25.90", "25.90"),  # the new format: text
        (25.9, "25.90"),  # the old format: a JSON number that Python reads as a float
        (10.0, "10.00"),
        (10, "10.00"),
    ],
)
def test_saved_prices_are_read_in_both_formats(saved: object, expected: str) -> None:
    assert str(price_from_json(saved)) == expected


def test_a_saved_float_that_is_not_a_clean_price_is_rejected() -> None:
    with pytest.raises(InvalidPriceError):
        price_from_json(0.1 + 0.2)  # 0.30000000000000004
