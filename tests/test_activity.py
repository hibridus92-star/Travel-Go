"""Tests for the Activity hierarchy: Activity, GuideTour and Pubcrawl."""
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from exceptions.errors import (
    ActivityError,
    InvalidActivityNameError,
    InvalidPriceError,
    InvalidStartTimeError,
    InvalidTypeError,
)
from models.activity import Activity, GuideTour, Pubcrawl

NOON: datetime = datetime(2027, 3, 14, 12, 0)


# --- description, ordering and counter ------------------------------------

def test_describe_includes_the_common_fields(walk: GuideTour) -> None:
    text: str = walk.describe()
    assert "Historic Walk" in text
    assert "Central Square" in text
    assert "Starts: 2027-03-14 10:00" in text
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
    GuideTour("A", "Somewhere", "1.00", NOON, False)
    Pubcrawl("B", "Elsewhere", "2.00", NOON, 1)
    assert Activity.events_count == before + 2


# --- start date and time --------------------------------------------------

def test_the_start_is_stored_as_given(walk: GuideTour) -> None:
    assert walk.starts_at == datetime(2027, 3, 14, 10, 0)


def test_the_start_cannot_be_changed(walk: GuideTour) -> None:
    # A fixed start is what lets a trip trust that its activities stay inside its dates.
    with pytest.raises(AttributeError):
        walk.starts_at = NOON  # type: ignore[misc]


@pytest.mark.parametrize(
    "bad_start",
    [
        date(2027, 3, 14),  # a date without a time is not enough
        "2027-03-14T10:00:00",  # text is not accepted by the constructor
        None,
        datetime(2027, 3, 14, 10, 0, tzinfo=timezone.utc),  # no time zones: local time of the destination
        datetime(2027, 3, 14, 10, 0, tzinfo=timezone(timedelta(hours=1))),
    ],
)
def test_an_invalid_start_is_rejected_and_the_activity_is_not_counted(bad_start: object) -> None:
    before: int = Activity.events_count
    with pytest.raises(InvalidStartTimeError) as error:
        GuideTour("A", "Somewhere", "1.00", bad_start, False)  # type: ignore[arg-type]
    assert error.value.starts_at is bad_start
    assert Activity.events_count == before


def test_subclasses_validate_the_start_too() -> None:
    with pytest.raises(InvalidStartTimeError):
        Pubcrawl("A", "Somewhere", "1.00", date(2027, 3, 14), 2)  # type: ignore[arg-type]


# --- prices ---------------------------------------------------------------

def test_the_price_is_a_decimal_with_two_decimals() -> None:
    activity: Activity = Activity("A", "Somewhere", 10, NOON)
    assert isinstance(activity.price, Decimal)
    assert str(activity.price) == "10.00"


def test_a_free_activity_is_allowed() -> None:
    assert Activity("Free Walk", "Somewhere", 0, NOON).price == Decimal("0.00")


@pytest.mark.parametrize("bad_price", [-5, "12.345", 9.99, "abc", None])
def test_an_invalid_price_is_rejected_and_the_activity_is_not_counted(bad_price: object) -> None:
    before: int = Activity.events_count
    with pytest.raises(InvalidPriceError) as error:
        GuideTour("A", "Somewhere", bad_price, NOON, False)  # type: ignore[arg-type]
    assert error.value.price is bad_price
    assert Activity.events_count == before


def test_subclasses_validate_the_price_too() -> None:
    with pytest.raises(InvalidPriceError):
        Pubcrawl("A", "Somewhere", "-1", NOON, 2)


def test_the_price_can_be_changed_to_another_valid_price(walk: GuideTour) -> None:
    walk.price = "12.5"
    assert walk.price == Decimal("12.50")


def test_an_invalid_price_assignment_is_rejected_and_keeps_the_old_price(walk: GuideTour) -> None:
    with pytest.raises(InvalidPriceError):
        walk.price = 12.5  # type: ignore[assignment]
    assert walk.price == Decimal("10.00")


# --- names ----------------------------------------------------------------

def test_the_name_is_stored_without_surrounding_spaces() -> None:
    assert Activity("  Historic Walk ", "Somewhere", "1.00", NOON).name == "Historic Walk"


@pytest.mark.parametrize("bad_name", ["", "   ", "\t\n", None, 5])
def test_an_invalid_name_is_rejected_and_the_activity_is_not_counted(bad_name: object) -> None:
    before: int = Activity.events_count
    with pytest.raises(InvalidActivityNameError) as error:
        Activity(bad_name, "Somewhere", "1.00", NOON)  # type: ignore[arg-type]
    assert error.value.name is bad_name
    assert Activity.events_count == before


def test_an_invalid_name_assignment_is_rejected_and_keeps_the_old_name(walk: GuideTour) -> None:
    with pytest.raises(InvalidActivityNameError):
        walk.name = "  "
    assert walk.name == "Historic Walk"


def test_activity_errors_share_a_base_exception() -> None:
    with pytest.raises(ActivityError):
        Activity("", "Somewhere", "1.00", NOON)
    with pytest.raises(ActivityError):
        Activity("A", "Somewhere", "-1", NOON)
    with pytest.raises(ActivityError):
        Activity("A", "Somewhere", "1.00", date(2027, 3, 14))  # type: ignore[arg-type]
    with pytest.raises(ActivityError):
        Activity.activity_from_dict({"type": "Museum"})


# --- dictionary conversion ------------------------------------------------

def test_to_dict_adds_the_type_field(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert walk.to_dict()["type"] == "GuideTour"
    assert pub_night.to_dict()["type"] == "Pubcrawl"


def test_to_dict_saves_price_and_start_as_text_so_it_can_be_written_as_json(walk: GuideTour) -> None:
    data: dict = walk.to_dict()
    assert data["price"] == "10.00"
    assert data["starts_at"] == "2027-03-14T10:00:00"
    assert json.loads(json.dumps(data)) == data  # Decimal and datetime alone would not be accepted by json


def test_guide_tour_round_trip(walk: GuideTour) -> None:
    rebuilt: Activity = Activity.activity_from_dict(walk.to_dict())
    assert isinstance(rebuilt, GuideTour)
    assert rebuilt.to_dict() == walk.to_dict()
    assert rebuilt.starts_at == walk.starts_at


def test_pubcrawl_round_trip(pub_night: Pubcrawl) -> None:
    rebuilt: Activity = Activity.activity_from_dict(pub_night.to_dict())
    assert isinstance(rebuilt, Pubcrawl)
    assert rebuilt.to_dict() == pub_night.to_dict()
    assert rebuilt.price == Decimal("25.90")
    assert rebuilt.starts_at == datetime(2027, 3, 14, 21, 0)


def test_an_activity_saved_with_a_float_price_still_loads() -> None:
    old_data: dict = {
        "type": "Pubcrawl", "name": "Drinkers Night", "location": "The Dolphin Shire",
        "price": 25.9, "starts_at": "2027-03-14T21:00:00", "drinks_included": 2,
    }
    rebuilt: Activity = Activity.activity_from_dict(old_data)
    assert rebuilt.price == Decimal("25.90")
    assert str(rebuilt.price) == "25.90"


def test_a_saved_start_that_is_not_a_valid_date_is_rejected() -> None:
    data: dict = {
        "type": "GuideTour", "name": "Walk", "location": "Square",
        "price": "1.00", "starts_at": "next tuesday", "tips_included": True,
    }
    with pytest.raises(InvalidStartTimeError) as error:
        Activity.activity_from_dict(data)
    assert error.value.starts_at == "next tuesday"


def test_unknown_type_is_rejected_and_keeps_the_offending_value() -> None:
    with pytest.raises(InvalidTypeError) as error:
        Activity.activity_from_dict({"type": "Museum", "name": "Prado"})
    assert error.value.type == "Museum"