"""Tests for the Activity hierarchy: Activity, GuideTour and Pubcrawl."""
import json
from decimal import Decimal

import pytest

from exceptions.errors import (
    ActivityError,
    InvalidActivityNameError,
    InvalidPriceError,
    InvalidTypeError,
)
from models.activity import Activity, GuideTour, Pubcrawl


@pytest.fixture
def walk() -> GuideTour:
    return GuideTour("Historic Walk", "Central Square", Decimal("10.00"), True)


@pytest.fixture
def pub_night() -> Pubcrawl:
    return Pubcrawl("Drinkers Night", "The Dolphin Shire", Decimal("25.90"), 2)


# --- description, ordering and counter ------------------------------------

def test_describe_includes_the_common_fields(walk: GuideTour) -> None:
    text: str = walk.describe()
    assert "Historic Walk" in text
    assert "Central Square" in text
    assert "Price: 10.00" in text


def test_subclasses_extend_describe(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert "Tips included: True" in walk.describe()
    assert "Drinks included: 2" in pub_night.describe()


def test_activities_are_ordered_by_price(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert walk < pub_night
    assert not pub_night < walk
    assert sorted([pub_night, walk]) == [walk, pub_night]


def test_events_count_grows_with_each_activity() -> None:
    before: int = Activity.events_count
    GuideTour("A", "Somewhere", "1.00", False)
    Pubcrawl("B", "Elsewhere", "2.00", 1)
    assert Activity.events_count == before + 2


# --- prices ---------------------------------------------------------------

def test_the_price_is_a_decimal_with_two_decimals() -> None:
    activity: Activity = Activity("A", "Somewhere", 10)
    assert isinstance(activity.price, Decimal)
    assert str(activity.price) == "10.00"


def test_a_free_activity_is_allowed() -> None:
    assert Activity("Free Walk", "Somewhere", 0).price == Decimal("0.00")


@pytest.mark.parametrize("bad_price", [-5, "12.345", 9.99, "abc", None])
def test_an_invalid_price_is_rejected_and_the_activity_is_not_counted(bad_price: object) -> None:
    before: int = Activity.events_count
    with pytest.raises(InvalidPriceError) as error:
        GuideTour("A", "Somewhere", bad_price, False)  # type: ignore[arg-type]
    assert error.value.price is bad_price
    assert Activity.events_count == before


def test_subclasses_validate_the_price_too() -> None:
    with pytest.raises(InvalidPriceError):
        Pubcrawl("A", "Somewhere", "-1", 2)


def test_the_price_can_be_changed_to_another_valid_price(walk: GuideTour) -> None:
    walk.price = "12.5"
    assert walk.price == Decimal("12.50")


def test_an_invalid_price_assignment_is_rejected_and_keeps_the_old_price(walk: GuideTour) -> None:
    with pytest.raises(InvalidPriceError):
        walk.price = 12.5  # type: ignore[assignment]
    assert walk.price == Decimal("10.00")


# --- names ----------------------------------------------------------------

def test_the_name_is_stored_without_surrounding_spaces() -> None:
    assert Activity("  Historic Walk ", "Somewhere", "1.00").name == "Historic Walk"


@pytest.mark.parametrize("bad_name", ["", "   ", "\t\n", None, 5])
def test_an_invalid_name_is_rejected_and_the_activity_is_not_counted(bad_name: object) -> None:
    before: int = Activity.events_count
    with pytest.raises(InvalidActivityNameError) as error:
        Activity(bad_name, "Somewhere", "1.00")  # type: ignore[arg-type]
    assert error.value.name is bad_name
    assert Activity.events_count == before


def test_an_invalid_name_assignment_is_rejected_and_keeps_the_old_name(walk: GuideTour) -> None:
    with pytest.raises(InvalidActivityNameError):
        walk.name = "  "
    assert walk.name == "Historic Walk"


def test_activity_errors_share_a_base_exception() -> None:
    with pytest.raises(ActivityError):
        Activity("", "Somewhere", "1.00")
    with pytest.raises(ActivityError):
        Activity("A", "Somewhere", "-1")
    with pytest.raises(ActivityError):
        Activity.activity_from_dict({"type": "Museum"})


# --- dictionary conversion ------------------------------------------------

def test_to_dict_adds_the_type_field(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert walk.to_dict()["type"] == "GuideTour"
    assert pub_night.to_dict()["type"] == "Pubcrawl"


def test_to_dict_saves_the_price_as_text_so_it_can_be_written_as_json(walk: GuideTour) -> None:
    data: dict = walk.to_dict()
    assert data["price"] == "10.00"
    assert json.loads(json.dumps(data)) == data  # Decimal alone would not be accepted by json


def test_guide_tour_round_trip(walk: GuideTour) -> None:
    rebuilt: Activity = Activity.activity_from_dict(walk.to_dict())
    assert isinstance(rebuilt, GuideTour)
    assert rebuilt.to_dict() == walk.to_dict()


def test_pubcrawl_round_trip(pub_night: Pubcrawl) -> None:
    rebuilt: Activity = Activity.activity_from_dict(pub_night.to_dict())
    assert isinstance(rebuilt, Pubcrawl)
    assert rebuilt.to_dict() == pub_night.to_dict()
    assert rebuilt.price == Decimal("25.90")


def test_an_activity_saved_with_a_float_price_still_loads() -> None:
    old_data: dict = {
        "type": "Pubcrawl", "name": "Drinkers Night", "location": "The Dolphin Shire",
        "price": 25.9, "drinks_included": 2,
    }
    rebuilt: Activity = Activity.activity_from_dict(old_data)
    assert rebuilt.price == Decimal("25.90")
    assert str(rebuilt.price) == "25.90"


def test_unknown_type_is_rejected_and_keeps_the_offending_value() -> None:
    with pytest.raises(InvalidTypeError) as error:
        Activity.activity_from_dict({"type": "Museum", "name": "Prado"})
    assert error.value.type == "Museum"
