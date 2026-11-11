"""Tests for User: age, travel points, dictionary conversion and file storage."""
from datetime import date
from pathlib import Path

import pytest

from exceptions.errors import (
    InsufficientPointsError,
    InvalidPointsAmountError,
    InvalidTravelPointsBalanceError,
    InvalidUserIdError,
    PointsError,
    UserNotFoundError,
    UserStorageError,
)
from models.user import User

FIXED_TODAY: date = date(2026, 6, 15)


@pytest.fixture
def ana() -> User:
    return User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])


@pytest.fixture
def fixed_today(monkeypatch: pytest.MonkeyPatch) -> None:
    """Freeze 'today' inside models.user so age tests give the same result on any day."""

    class FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return FIXED_TODAY

    monkeypatch.setattr("models.user.date", FrozenDate)


# --- identity and age -----------------------------------------------------

def test_a_new_user_gets_a_unique_id() -> None:
    first: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])
    second: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])
    assert first.user_id != second.user_id


def test_a_given_id_is_kept() -> None:
    user: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"], user_id="abc-1")
    assert user.user_id == "abc-1"


def test_the_id_cannot_be_reassigned(ana: User) -> None:
    with pytest.raises(AttributeError):
        ana.user_id = "another-id"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("birth_date", "expected_age"),
    [
        (date(2000, 6, 14), 26),  # birthday was yesterday
        (date(2000, 6, 15), 26),  # birthday is today
        (date(2000, 6, 16), 25),  # birthday is tomorrow
        (date(2000, 12, 31), 25),  # birthday is later this year
    ],
)
def test_age_depends_on_whether_the_birthday_has_passed(
    fixed_today: None, birth_date: date, expected_age: int
) -> None:
    user: User = User("Ana", "Lopez", birth_date, "Murcia", "Spain", ["es"])
    assert user.age == expected_age


def test_languages_are_copied_on_the_way_in() -> None:
    languages: list[str] = ["es"]
    user: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", languages)
    languages.append("en")
    assert user.languages == ["es"]


# --- travel points --------------------------------------------------------

def test_a_new_user_has_zero_points(ana: User) -> None:
    assert ana.travel_points == 0


def test_earning_and_redeeming(ana: User) -> None:
    ana.earn_points(100)
    ana.redeem_points(30)
    assert ana.travel_points == 70


def test_redeeming_the_whole_balance_is_allowed(ana: User) -> None:
    ana.earn_points(50)
    ana.redeem_points(50)
    assert ana.travel_points == 0


def test_redeeming_more_than_the_balance_is_rejected_and_keeps_the_balance(ana: User) -> None:
    ana.earn_points(100)
    with pytest.raises(InsufficientPointsError) as error:
        ana.redeem_points(500)
    assert error.value.amount == 500
    assert error.value.balance == 100
    assert ana.travel_points == 100


@pytest.mark.parametrize("amount", [0, -5])
def test_earning_a_non_positive_amount_is_rejected(ana: User, amount: int) -> None:
    with pytest.raises(InvalidPointsAmountError) as error:
        ana.earn_points(amount)
    assert error.value.amount == amount
    assert ana.travel_points == 0


@pytest.mark.parametrize("amount", [0, -5])
def test_redeeming_a_non_positive_amount_is_rejected(ana: User, amount: int) -> None:
    ana.earn_points(100)
    with pytest.raises(InvalidPointsAmountError):
        ana.redeem_points(amount)
    assert ana.travel_points == 100


def test_points_cannot_be_assigned_directly(ana: User) -> None:
    with pytest.raises(AttributeError):
        ana.travel_points = 999  # type: ignore[misc]


def test_points_errors_share_a_base_exception(ana: User) -> None:
    with pytest.raises(PointsError):
        ana.earn_points(-1)
    with pytest.raises(PointsError):
        ana.redeem_points(1)


# --- dictionary conversion ------------------------------------------------

def test_dictionary_round_trip(ana: User) -> None:
    ana.earn_points(100)

    loaded: User = User.from_dict(ana.to_dict())

    assert loaded.user_id == ana.user_id
    assert loaded.name == "Ana"
    assert loaded.birth_date == date(2000, 3, 10)
    assert isinstance(loaded.birth_date, date)
    assert loaded.travel_points == 100
    assert loaded.languages == ["es"]


def test_a_user_with_zero_points_can_be_restored(ana: User) -> None:
    assert User.from_dict(ana.to_dict()).travel_points == 0


def test_to_dict_returns_an_independent_copy_of_the_languages(ana: User) -> None:
    data: dict = ana.to_dict()
    data["languages"].append("en")
    assert ana.languages == ["es"]


def test_a_negative_saved_balance_is_rejected(ana: User) -> None:
    corrupted: dict = ana.to_dict()
    corrupted["travel_points"] = -50
    with pytest.raises(InvalidTravelPointsBalanceError) as error:
        User.from_dict(corrupted)
    assert error.value.balance == -50


# --- file storage ---------------------------------------------------------

def test_save_creates_the_directory_and_one_file_per_user(tmp_path: Path, ana: User) -> None:
    directory: Path = tmp_path / "users"  # does not exist yet
    luis: User = User("Luis", "Gil", date(1990, 1, 3), "Madrid", "Spain", ["es", "en"])

    ana.save(str(directory))
    luis.save(str(directory))

    assert sorted(p.name for p in directory.iterdir()) == sorted(
        [f"{ana.user_id}.json", f"{luis.user_id}.json"]
    )


def test_load_returns_the_saved_user(tmp_path: Path, ana: User) -> None:
    ana.earn_points(100)
    ana.save(str(tmp_path))

    loaded: User = User.load(ana.user_id, str(tmp_path))

    assert loaded.user_id == ana.user_id
    assert loaded.name == "Ana"
    assert loaded.travel_points == 100


def test_loading_an_unknown_id_raises_instead_of_returning_an_empty_user(tmp_path: Path) -> None:
    missing: str = "00000000-0000-0000-0000-000000000000"
    with pytest.raises(UserNotFoundError) as error:
        User.load(missing, str(tmp_path))
    assert error.value.user_id == missing


@pytest.mark.parametrize(
    "bad_id", ["../secret", "..\\secret", "a/b", "a b", "a.b", "", "abc\n"]
)
def test_load_rejects_ids_that_are_not_safe_file_names(tmp_path: Path, bad_id: str) -> None:
    with pytest.raises(InvalidUserIdError) as error:
        User.load(bad_id, str(tmp_path))
    assert error.value.user_id == bad_id


def test_save_rejects_an_unsafe_id_and_writes_nothing(tmp_path: Path) -> None:
    directory: Path = tmp_path / "users"
    sneaky: User = User(
        "Eve", "Ruiz", date(2000, 6, 1), "Lima", "Peru", ["es"], user_id="../escape"
    )

    with pytest.raises(InvalidUserIdError):
        sneaky.save(str(directory))

    assert not directory.exists()  # not even the folder is created
    assert list(tmp_path.iterdir()) == []


def test_storage_errors_share_a_base_exception(tmp_path: Path) -> None:
    with pytest.raises(UserStorageError):
        User.load("nobody", str(tmp_path))
    with pytest.raises(UserStorageError):
        User.load("../x", str(tmp_path))