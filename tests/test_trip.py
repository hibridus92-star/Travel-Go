"""Tests for Trip: prices, alcohol count, participants and JSON persistence."""
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from exceptions.errors import (
    DuplicateParticipantError,
    InvalidTripFileError,
    ParticipantError,
    ParticipantNotFoundError,
)
from models.activity import GuideTour, Pubcrawl
from models.trip import Trip

START: date = date(2027, 3, 12)
END: date = date(2027, 3, 16)


def datetime_at(hour: int) -> datetime:
    return datetime(2027, 3, 14, hour, 0)


def make_trip(activities: list, participant_ids: list | None = None) -> Trip:
    return Trip(1, "La Valleta", START, END, activities, participant_ids)


# --- prices and description -----------------------------------------------

def test_price_per_person_is_the_sum_of_the_activity_prices(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert make_trip([walk, pub_night]).price_per_person() == Decimal("35.90")


def test_price_per_person_is_a_decimal_and_has_no_rounding_errors() -> None:
    cheap: list = [
        GuideTour("A", "Somewhere", "0.10", datetime_at(10), False),
        GuideTour("B", "Somewhere", "0.20", datetime_at(11), False),
    ]
    price: Decimal = make_trip(cheap).price_per_person()
    assert isinstance(price, Decimal)
    assert price == Decimal("0.30")  # with floats, 0.1 + 0.2 is 0.30000000000000004


def test_price_per_person_of_a_trip_without_activities_is_zero() -> None:
    price: Decimal = make_trip([]).price_per_person()
    assert isinstance(price, Decimal)
    assert price == Decimal("0.00")


def test_total_price_is_the_price_per_person_times_the_participants(walk: GuideTour, pub_night: Pubcrawl) -> None:
    trip: Trip = make_trip([walk, pub_night], ["a", "b", "c"])
    assert trip.total_price() == Decimal("107.70")  # 35.90 x 3


def test_total_price_follows_the_number_of_participants(walk: GuideTour) -> None:
    trip: Trip = make_trip([walk])
    trip.add_participant("a")
    assert trip.total_price() == Decimal("10.00")
    trip.add_participant("b")
    assert trip.total_price() == Decimal("20.00")
    trip.remove_participant("a")
    assert trip.total_price() == Decimal("10.00")


def test_total_price_without_participants_is_zero(walk: GuideTour) -> None:
    # Once trips have an owner (a later step) a trip always has at least one participant.
    assert make_trip([walk]).total_price() == Decimal("0.00")


def test_alcoholic_events_counts_only_pubcrawls(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert make_trip([walk, pub_night, pub_night]).alcoholic_events() == 2


def test_describe_joins_the_descriptions_of_all_activities(walk: GuideTour, pub_night: Pubcrawl) -> None:
    text: str = make_trip([walk, pub_night]).describe()
    assert "Historic Walk" in text
    assert "Drinkers Night" in text


# --- participants ---------------------------------------------------------

def test_a_new_trip_has_no_participants(walk: GuideTour) -> None:
    assert make_trip([walk]).participant_ids == []


def test_participants_are_not_shared_between_trips() -> None:
    first: Trip = make_trip([])
    second: Trip = Trip(2, "Paris", START, END, [])
    first.add_participant("a")
    assert second.participant_ids == []


def test_participants_keep_their_order() -> None:
    trip: Trip = make_trip([])
    trip.add_participant("a")
    trip.add_participant("b")
    assert trip.participant_ids == ["a", "b"]


def test_duplicate_participant_is_rejected_and_the_list_is_unchanged() -> None:
    trip: Trip = make_trip([])
    trip.add_participant("a")
    with pytest.raises(DuplicateParticipantError) as error:
        trip.add_participant("a")
    assert error.value.user_id == "a"
    assert trip.participant_ids == ["a"]


def test_removing_a_participant() -> None:
    trip: Trip = make_trip([])
    trip.add_participant("a")
    trip.add_participant("b")
    trip.remove_participant("a")
    assert trip.participant_ids == ["b"]


def test_removing_someone_who_is_not_there_is_rejected() -> None:
    trip: Trip = make_trip([])
    trip.add_participant("a")
    with pytest.raises(ParticipantNotFoundError) as error:
        trip.remove_participant("z")
    assert error.value.user_id == "z"
    assert trip.participant_ids == ["a"]


def test_participant_errors_share_a_base_exception() -> None:
    trip: Trip = make_trip([])
    trip.add_participant("a")
    with pytest.raises(ParticipantError):
        trip.add_participant("a")
    with pytest.raises(ParticipantError):
        trip.remove_participant("z")


def test_participant_ids_returns_a_copy() -> None:
    trip: Trip = make_trip([])
    trip.add_participant("a")
    trip.participant_ids.append("x")
    assert trip.participant_ids == ["a"]


def test_constructor_copies_the_list_it_receives() -> None:
    ids: list[str] = ["a", "b"]
    trip: Trip = Trip(3, "Lima", START, END, [], ids)
    ids.append("c")
    assert trip.participant_ids == ["a", "b"]


# --- persistence ----------------------------------------------------------

def test_round_trip_keeps_every_field(tmp_path: Path, walk: GuideTour, pub_night: Pubcrawl) -> None:
    path: str = str(tmp_path / "trip.json")
    trip: Trip = Trip(2334, "La Valleta", START, END, [walk, pub_night])
    trip.add_participant("a")
    trip.add_participant("b")
    trip.save(path)

    loaded: Trip = Trip.load(path)

    assert loaded.id_number == 2334
    assert loaded.destination == "La Valleta"
    assert loaded.start_date == START
    assert loaded.end_date == END
    assert loaded.participant_ids == ["a", "b"]
    assert loaded.to_dict() == trip.to_dict()


def test_loading_rebuilds_the_right_activity_subclasses(tmp_path: Path, walk: GuideTour, pub_night: Pubcrawl) -> None:
    path: str = str(tmp_path / "trip.json")
    make_trip([walk, pub_night]).save(path)

    loaded: Trip = Trip.load(path)

    assert isinstance(loaded.activities[0], GuideTour)
    assert isinstance(loaded.activities[1], Pubcrawl)


def test_dates_and_prices_are_saved_as_text(tmp_path: Path, walk: GuideTour, pub_night: Pubcrawl) -> None:
    path: Path = tmp_path / "trip.json"
    make_trip([walk, pub_night]).save(str(path))

    saved: dict = json.loads(path.read_text())

    assert saved["start_date"] == "2027-03-12"
    assert saved["end_date"] == "2027-03-16"
    assert saved["status"] == "draft"
    assert saved["activities"][0]["price"] == "10.00"
    assert saved["activities"][0]["starts_at"] == "2027-03-14T10:00:00"
    assert Trip.load(str(path)).price_per_person() == Decimal("35.90")


def test_validation_still_works_after_loading(tmp_path: Path) -> None:
    path: str = str(tmp_path / "trip.json")
    trip: Trip = make_trip([])
    trip.add_participant("a")
    trip.save(path)

    loaded: Trip = Trip.load(path)
    with pytest.raises(DuplicateParticipantError):
        loaded.add_participant("a")


def test_files_without_participant_ids_or_status_still_load(tmp_path: Path) -> None:
    path: Path = tmp_path / "older_trip.json"
    path.write_text(json.dumps({
        "id_number": 2334, "destination": "La Valleta",
        "start_date": "2027-03-12", "end_date": "2027-03-16", "activities": [],
    }))

    loaded: Trip = Trip.load(str(path))

    assert loaded.destination == "La Valleta"
    assert loaded.participant_ids == []
    assert loaded.status.value == "draft"


def test_files_with_float_prices_still_load(tmp_path: Path) -> None:
    path: Path = tmp_path / "float_prices.json"
    path.write_text(json.dumps({
        "id_number": 2334,
        "destination": "La Valleta",
        "start_date": "2027-03-12",
        "end_date": "2027-03-16",
        "activities": [
            {"type": "GuideTour", "name": "Historic Walk", "location": "Central Square",
             "price": 10.0, "starts_at": "2027-03-14T10:00:00", "tips_included": True},
            {"type": "Pubcrawl", "name": "Drinkers Night", "location": "The Dolphin Shire",
             "price": 25.9, "starts_at": "2027-03-14T21:00:00", "drinks_included": 2},
        ],
    }))

    assert Trip.load(str(path)).price_per_person() == Decimal("35.90")


def test_a_file_saved_before_trips_had_dates_is_rejected_with_a_clear_error(tmp_path: Path) -> None:
    # Dates are mandatory now, and nothing sensible can be invented for old files.
    path: Path = tmp_path / "no_dates.json"
    path.write_text(json.dumps({"id_number": 2334, "destination": "La Valleta", "activities": []}))

    with pytest.raises(InvalidTripFileError) as error:
        Trip.load(str(path))

    assert error.value.field == "start_date"


@pytest.mark.parametrize("bad_date", ["next week", "2027-13-45", 20270312, None])
def test_a_saved_date_that_is_not_valid_is_rejected(empty_trip: Trip, bad_date: object) -> None:
    data: dict = empty_trip.to_dict()
    data["end_date"] = bad_date
    with pytest.raises(InvalidTripFileError) as error:
        Trip.from_dict(data)
    assert error.value.field == "end_date"


def test_an_activity_without_a_start_in_a_saved_trip_is_rejected(empty_trip: Trip) -> None:
    data: dict = empty_trip.to_dict()
    data["activities"] = [
        {"type": "GuideTour", "name": "Walk", "location": "Square", "price": "1.00", "tips_included": True}
    ]
    with pytest.raises(InvalidTripFileError) as error:
        Trip.from_dict(data)
    assert error.value.field == "starts_at"


def test_loading_a_missing_file_raises_instead_of_returning_an_empty_trip(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Trip.load(str(tmp_path / "does_not_exist.json"))