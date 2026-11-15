"""Money helpers: validate prices and read them from saved files."""
from decimal import Decimal, InvalidOperation

from exceptions.errors import InvalidPriceError

CENT: Decimal = Decimal("0.01")


def parse_price(value: Decimal | int | str) -> Decimal:
    """Return the price as a Decimal with exactly two decimals.

    A Decimal, an int or a text such as "25.90" are accepted. A float is rejected: most
    decimal fractions (0.1, 25.9) cannot be stored exactly as a float, so using one would
    bring back the rounding errors that Decimal exists to avoid.
    A price must be zero or positive and have at most two decimals.
    """
    if isinstance(value, float):
        raise InvalidPriceError(value, "a float is not exact, use a Decimal or a text like '25.90'")
    # bool is a subclass of int, so True would otherwise be accepted as the price 1.
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise InvalidPriceError(value, "it must be a Decimal, an int or a text")

    try:
        amount: Decimal = Decimal(value)
    except InvalidOperation:
        raise InvalidPriceError(value, "it is not a valid number") from None

    if not amount.is_finite():
        raise InvalidPriceError(value, "it must be a finite number")
    if amount < 0:
        raise InvalidPriceError(value, "it cannot be negative")

    try:
        cents: Decimal = amount.quantize(CENT)
    except InvalidOperation:
        raise InvalidPriceError(value, "it is too large") from None
    if cents != amount:
        raise InvalidPriceError(value, "it cannot have more than two decimals")

    return abs(cents)  # abs turns a negative zero (-0.00) into 0.00


def price_from_json(value: object) -> Decimal:
    """Read a price from a saved file.

    New files store the price as text ("25.90"). Files saved before prices became
    decimals store a JSON number, which Python reads as a float (25.9), so a float is
    converted through its text form before it is validated.
    """
    if isinstance(value, float):
        return parse_price(repr(value))
    return parse_price(value)  # type: ignore[arg-type]
