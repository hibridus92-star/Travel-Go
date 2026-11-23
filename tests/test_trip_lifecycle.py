"""Tests for the lifecycle of a trip: draft and purchased."""
from pathlib import Path

import pytest

from exceptions.errors import InvalidTripFileError, TripError, TripLockedError
from models.activity import GuideTour, Pubcrawl
from models.trip import Trip, TripStatus


@pytest.fixture
def purchased_trip(empty_trip: Trip, walk: GuideTour) -> Trip:
    """A trip with one activity and one participant that has already been purchased."""
    empty_trip.add_activity(walk)
    empty_trip.add_participant("a")
    empty_trip.mark_purchased()
    return empty_trip


def test_a_new_trip_is_a_draft(empty_trip: Trip) -> None:
    assert empty_trip.status is TripStatus.DRAFT


def test_a_draft_can_be_purchased(empty_trip: Trip) -> None:
    empty_trip.mark_purchased()
    assert empty_trip.status is TripStatus.PURCHASED


def test_the_status_cannot_be_assigned_directly(empty_trip: Trip) -> None:
    with pytest.raises(AttributeError):
        empty_trip.status = TripStatus.PURCHASED  # type: ignore[misc]


# --- a purchased trip is locked -------------------------------------------

def test_a_purchased_trip_rejects_new_activities(purchased_trip: Trip, pub_night: Pubcrawl) -> None:
    with pytest.raises(TripLockedError) as error:
        purchased_trip.add_activity(pub_night)
    assert error.value.trip_id == 1
    assert len(purchased_trip.activities) == 1


def test_a_purchased_trip_rejects_removing_activities(purchased_trip: Trip, walk: GuideTour) -> None:
    with pytest.raises(TripLockedError):
        purchased_trip.remove_activity(walk)
    assert purchased_trip.activities == [walk]


def test_a_purchased_trip_rejects_new_participants(purchased_trip: Trip) -> None:
    with pytest.raises(TripLockedError):
        purchased_trip.add_participant("b")
    assert purchased_trip.participant_ids == ["a"]


def test_a_purchased_trip_rejects_removing_participants(purchased_trip: Trip) -> None:
    with pytest.raises(TripLockedError):
        purchased_trip.remove_participant("a")
    assert purchased_trip.participant_ids == ["a"]


def test_a_trip_cannot_be_purchased_twice(purchased_trip: Trip) -> None:
    with pytest.raises(TripLockedError):
        purchased_trip.mark_purchased()
    assert purchased_trip.status is TripStatus.PURCHASED


def test_a_locked_trip_can_still_be_read(purchased_trip: Trip) -> None:
    assert "Historic Walk" in purchased_trip.describe()
    assert str(purchased_trip.price_per_person()) == "10.00"
    assert str(purchased_trip.total_price()) == "10.00"


def test_the_lock_error_belongs_to_the_trip_error_family(purchased_trip: Trip) -> None:
    with pytest.raises(TripError):
        purchased_trip.add_participant("b")


# --- the status survives saving -------------------------------------------

def test_the_status_survives_a_round_trip(tmp_path: Path, purchased_trip: Trip) -> None:
    path: str = str(tmp_path / "trip.json")
    purchased_trip.save(path)

    loaded: Trip = Trip.load(path)

    assert loaded.status is TripStatus.PURCHASED
    with pytest.raises(TripLockedError):
        loaded.add_participant("b")


def test_a_draft_stays_a_draft_after_a_round_trip(tmp_path: Path, empty_trip: Trip) -> None:
    path: str = str(tmp_path / "trip.json")
    empty_trip.save(path)
    assert Trip.load(path).status is TripStatus.DRAFT


def test_a_saved_status_that_does_not_exist_is_rejected(empty_trip: Trip) -> None:
    data: dict = empty_trip.to_dict()
    data["status"] = "cancelled"
    with pytest.raises(InvalidTripFileError) as error:
        Trip.from_dict(data)
    assert error.value.field == "status"