"""Tests for Trip: cost, alcohol count, participants and JSON persistence."""
import json
from pathlib import Path

import pytest

from exceptions.errors import (
    DuplicateParticipantError,
    ParticipantError,
    ParticipantNotFoundError,
)
from models.activity import GuideTour, Pubcrawl
from models.trip import Trip


@pytest.fixture
def walk() -> GuideTour:
    return GuideTour("Historic Walk", "Central Square", 10.00, True)


@pytest.fixture
def pub_night() -> Pubcrawl:
    return Pubcrawl("Drinkers Night", "The Dolphin Shire", 25.90, 2)


# --- cost and description -------------------------------------------------

def test_total_cost_is_the_sum_of_the_activity_prices(walk: GuideTour, pub_night: Pubcrawl) -> None:
    trip: Trip = Trip(1, "La Valleta", [walk, pub_night])
    # Prices are floats today, so compare with a tolerance (this changes in 'chore/decimal-prices').
    assert trip.event_total_cost() == pytest.approx(35.90)


def test_total_cost_of_a_trip_without_activities_is_zero() -> None:
    assert Trip(1, "Rome", []).event_total_cost() == 0


def test_alcoholic_events_counts_only_pubcrawls(walk: GuideTour, pub_night: Pubcrawl) -> None:
    trip: Trip = Trip(1, "La Valleta", [walk, pub_night, pub_night])
    assert trip.alcoholic_events() == 2


def test_describe_joins_the_descriptions_of_all_activities(walk: GuideTour, pub_night: Pubcrawl) -> None:
    text: str = Trip(1, "La Valleta", [walk, pub_night]).describe()
    assert "Historic Walk" in text
    assert "Drinkers Night" in text


# --- participants ---------------------------------------------------------

def test_a_new_trip_has_no_participants(walk: GuideTour) -> None:
    assert Trip(1, "Rome", [walk]).participant_ids == []


def test_participants_are_not_shared_between_trips() -> None:
    first: Trip = Trip(1, "Rome", [])
    second: Trip = Trip(2, "Paris", [])
    first.add_participant("a")
    assert second.participant_ids == []


def test_participants_keep_their_order() -> None:
    trip: Trip = Trip(1, "Rome", [])
    trip.add_participant("a")
    trip.add_participant("b")
    assert trip.participant_ids == ["a", "b"]


def test_duplicate_participant_is_rejected_and_the_list_is_unchanged() -> None:
    trip: Trip = Trip(1, "Rome", [])
    trip.add_participant("a")
    with pytest.raises(DuplicateParticipantError) as error:
        trip.add_participant("a")
    assert error.value.user_id == "a"
    assert trip.participant_ids == ["a"]


def test_removing_a_participant() -> None:
    trip: Trip = Trip(1, "Rome", [])
    trip.add_participant("a")
    trip.add_participant("b")
    trip.remove_participant("a")
    assert trip.participant_ids == ["b"]


def test_removing_someone_who_is_not_there_is_rejected() -> None:
    trip: Trip = Trip(1, "Rome", [])
    trip.add_participant("a")
    with pytest.raises(ParticipantNotFoundError) as error:
        trip.remove_participant("z")
    assert error.value.user_id == "z"
    assert trip.participant_ids == ["a"]


def test_participant_errors_share_a_base_exception() -> None:
    trip: Trip = Trip(1, "Rome", [])
    trip.add_participant("a")
    with pytest.raises(ParticipantError):
        trip.add_participant("a")
    with pytest.raises(ParticipantError):
        trip.remove_participant("z")


def test_participant_ids_returns_a_copy() -> None:
    trip: Trip = Trip(1, "Rome", [])
    trip.add_participant("a")
    trip.participant_ids.append("x")
    assert trip.participant_ids == ["a"]


def test_constructor_copies_the_list_it_receives() -> None:
    ids: list[str] = ["a", "b"]
    trip: Trip = Trip(3, "Lima", [], ids)
    ids.append("c")
    assert trip.participant_ids == ["a", "b"]


# --- persistence ----------------------------------------------------------

def test_round_trip_keeps_every_field(tmp_path: Path, walk: GuideTour, pub_night: Pubcrawl) -> None:
    path: str = str(tmp_path / "trip.json")
    trip: Trip = Trip(2334, "La Valleta", [walk, pub_night])
    trip.add_participant("a")
    trip.add_participant("b")
    trip.save(path)

    loaded: Trip = Trip.load(path)

    assert loaded.id_number == 2334
    assert loaded.destination == "La Valleta"
    assert loaded.participant_ids == ["a", "b"]
    assert loaded.to_dict() == trip.to_dict()


def test_loading_rebuilds_the_right_activity_subclasses(tmp_path: Path, walk: GuideTour, pub_night: Pubcrawl) -> None:
    path: str = str(tmp_path / "trip.json")
    Trip(1, "La Valleta", [walk, pub_night]).save(path)

    loaded: Trip = Trip.load(path)

    assert isinstance(loaded.activities[0], GuideTour)
    assert isinstance(loaded.activities[1], Pubcrawl)


def test_validation_still_works_after_loading(tmp_path: Path) -> None:
    path: str = str(tmp_path / "trip.json")
    trip: Trip = Trip(1, "Malta", [])
    trip.add_participant("a")
    trip.save(path)

    loaded: Trip = Trip.load(path)
    with pytest.raises(DuplicateParticipantError):
        loaded.add_participant("a")


def test_old_files_without_participant_ids_still_load(tmp_path: Path) -> None:
    path: Path = tmp_path / "old_trip.json"
    path.write_text(
        json.dumps({"id_number": 2334, "destination": "La Valleta", "activities": []})
    )

    loaded: Trip = Trip.load(str(path))

    assert loaded.destination == "La Valleta"
    assert loaded.participant_ids == []


def test_loading_a_missing_file_returns_an_empty_trip(tmp_path: Path) -> None:
    # Documents a KNOWN LIMITATION (it can hide errors). 'feature/repositories' will make
    # this raise an exception instead, and this test must change with it.
    loaded: Trip = Trip.load(str(tmp_path / "does_not_exist.json"))
    assert loaded.id_number == 0
    assert loaded.destination == ""
    assert loaded.activities == []