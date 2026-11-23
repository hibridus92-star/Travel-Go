"""Tests for the dates of a trip and the rule that its activities fall inside them."""
from datetime import date, datetime
from decimal import Decimal

import pytest

from exceptions.errors import (
    ActivityNotInTripError,
    ActivityOutsideTripDatesError,
    InvalidTripDatesError,
    TripError,
)
from models.activity import GuideTour, Pubcrawl
from models.trip import Trip

START: date = date(2027, 3, 12)
END: date = date(2027, 3, 16)


def make_activity(starts_at: datetime) -> GuideTour:
    return GuideTour("Walk", "Somewhere", Decimal("10.00"), starts_at, True)


# --- the dates themselves -------------------------------------------------

def test_the_dates_are_stored_and_read_only(empty_trip: Trip) -> None:
    assert empty_trip.start_date == START
    assert empty_trip.end_date == END
    with pytest.raises(AttributeError):
        empty_trip.start_date = date(2027, 1, 1)  # type: ignore[misc]
    with pytest.raises(AttributeError):
        empty_trip.end_date = date(2027, 12, 31)  # type: ignore[misc]


def test_a_one_day_trip_is_allowed() -> None:
    trip: Trip = Trip(1, "Rome", START, START, [])
    assert trip.start_date == trip.end_date


def test_a_trip_cannot_end_before_it_starts() -> None:
    with pytest.raises(InvalidTripDatesError) as error:
        Trip(1, "Rome", END, START, [])
    assert error.value.start_date == END
    assert error.value.end_date == START


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (datetime(2027, 3, 12, 9, 0), datetime(2027, 3, 16, 9, 0)),  # datetimes, not dates
        ("2027-03-12", "2027-03-16"),  # text
        (None, END),
    ],
)
def test_the_dates_must_be_plain_dates(start: object, end: object) -> None:
    with pytest.raises(InvalidTripDatesError):
        Trip(1, "Rome", start, end, [])  # type: ignore[arg-type]


# --- activities must start inside the trip --------------------------------

@pytest.mark.parametrize(
    "starts_at",
    [
        datetime(2027, 3, 12, 0, 0),  # first minute of the first day
        datetime(2027, 3, 14, 12, 0),
        datetime(2027, 3, 16, 23, 59, 59),  # last second of the last day
    ],
)
def test_activities_inside_the_dates_are_accepted_limits_included(empty_trip: Trip, starts_at: datetime) -> None:
    activity: GuideTour = make_activity(starts_at)
    empty_trip.add_activity(activity)
    assert empty_trip.activities == [activity]


@pytest.mark.parametrize(
    "starts_at",
    [
        datetime(2027, 3, 11, 23, 59, 59),  # one second before the trip
        datetime(2027, 3, 17, 0, 0),  # the first minute after the trip
    ],
)
def test_an_activity_outside_the_dates_is_rejected_and_the_trip_is_unchanged(
    empty_trip: Trip, starts_at: datetime
) -> None:
    activity: GuideTour = make_activity(starts_at)
    with pytest.raises(ActivityOutsideTripDatesError) as error:
        empty_trip.add_activity(activity)
    assert error.value.activity_name == "Walk"
    assert error.value.starts_at == starts_at
    assert error.value.start_date == START
    assert error.value.end_date == END
    assert empty_trip.activities == []


def test_the_constructor_applies_the_same_rule() -> None:
    outside: GuideTour = make_activity(datetime(2027, 4, 1, 10, 0))
    with pytest.raises(ActivityOutsideTripDatesError):
        Trip(1, "Rome", START, END, [outside])


def test_the_same_activity_can_belong_to_several_trips(walk: GuideTour) -> None:
    first: Trip = Trip(1, "Rome", START, END, [walk])
    second: Trip = Trip(2, "Rome", date(2027, 3, 14), date(2027, 3, 14), [walk])
    assert first.activities == second.activities == [walk]


# --- removing activities and copies ---------------------------------------

def test_removing_an_activity(empty_trip: Trip, walk: GuideTour, pub_night: Pubcrawl) -> None:
    empty_trip.add_activity(walk)
    empty_trip.add_activity(pub_night)
    empty_trip.remove_activity(walk)
    assert empty_trip.activities == [pub_night]


def test_removing_an_activity_that_is_not_there_is_rejected(empty_trip: Trip, walk: GuideTour, pub_night: Pubcrawl) -> None:
    empty_trip.add_activity(walk)
    with pytest.raises(ActivityNotInTripError) as error:
        empty_trip.remove_activity(pub_night)
    assert error.value.activity_name == "Drinkers Night"
    assert empty_trip.activities == [walk]


def test_activities_returns_a_copy(empty_trip: Trip, walk: GuideTour, pub_night: Pubcrawl) -> None:
    empty_trip.add_activity(walk)
    empty_trip.activities.append(pub_night)
    assert empty_trip.activities == [walk]


def test_the_constructor_copies_the_list_it_receives(walk: GuideTour, pub_night: Pubcrawl) -> None:
    activities: list = [walk]
    trip: Trip = Trip(1, "Rome", START, END, activities)
    activities.append(pub_night)
    assert trip.activities == [walk]


def test_trip_errors_share_a_base_exception(empty_trip: Trip, walk: GuideTour) -> None:
    with pytest.raises(TripError):
        Trip(1, "Rome", END, START, [])
    with pytest.raises(TripError):
        empty_trip.add_activity(make_activity(datetime(2030, 1, 1, 10, 0)))
    with pytest.raises(TripError):
        empty_trip.remove_activity(walk)