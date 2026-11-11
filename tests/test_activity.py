"""Tests for the Activity hierarchy: Activity, GuideTour and Pubcrawl."""
import pytest

from exceptions.errors import InvalidTypeError
from models.activity import Activity, GuideTour, Pubcrawl


@pytest.fixture
def walk() -> GuideTour:
    return GuideTour("Historic Walk", "Central Square", 10.00, True)


@pytest.fixture
def pub_night() -> Pubcrawl:
    return Pubcrawl("Drinkers Night", "The Dolphin Shire", 25.90, 2)


def test_describe_includes_the_common_fields(walk: GuideTour) -> None:
    text: str = walk.describe()
    assert "Historic Walk" in text
    assert "Central Square" in text
    assert "10.0" in text


def test_subclasses_extend_describe(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert "Tips included: True" in walk.describe()
    assert "Drinks included: 2" in pub_night.describe()


def test_activities_are_ordered_by_price(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert walk < pub_night
    assert not pub_night < walk
    assert sorted([pub_night, walk]) == [walk, pub_night]


def test_events_count_grows_with_each_activity() -> None:
    before: int = Activity.events_count
    GuideTour("A", "Somewhere", 1.0, False)
    Pubcrawl("B", "Elsewhere", 2.0, 1)
    assert Activity.events_count == before + 2


def test_to_dict_adds_the_type_field(walk: GuideTour, pub_night: Pubcrawl) -> None:
    assert walk.to_dict()["type"] == "GuideTour"
    assert pub_night.to_dict()["type"] == "Pubcrawl"


def test_guide_tour_round_trip(walk: GuideTour) -> None:
    rebuilt: Activity = Activity.activity_from_dict(walk.to_dict())
    assert isinstance(rebuilt, GuideTour)
    assert rebuilt.to_dict() == walk.to_dict()


def test_pubcrawl_round_trip(pub_night: Pubcrawl) -> None:
    rebuilt: Activity = Activity.activity_from_dict(pub_night.to_dict())
    assert isinstance(rebuilt, Pubcrawl)
    assert rebuilt.to_dict() == pub_night.to_dict()


def test_unknown_type_is_rejected_and_keeps_the_offending_value() -> None:
    with pytest.raises(InvalidTypeError) as error:
        Activity.activity_from_dict({"type": "Museum", "name": "Prado"})
    assert error.value.type == "Museum"