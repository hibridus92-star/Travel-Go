"""User: a traveller who owns trips and accumulates travel points."""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import date

from exceptions.errors import (
    InsufficientPointsError,
    InvalidPointsAmountError,
    InvalidTravelPointsBalanceError,
    InvalidUserIdError,
    UserNotFoundError,
)

USERS_DIR: str = os.path.join("data", "users")

# An ID becomes part of a file name, so only these characters are accepted.
_VALID_USER_ID = re.compile(r"[A-Za-z0-9_-]+")


def _user_path(user_id: str, directory: str) -> str:
    """Return the file path of a user, rejecting IDs that could escape the directory."""
    if not _VALID_USER_ID.fullmatch(user_id):
        raise InvalidUserIdError(user_id)
    return os.path.join(directory, f"{user_id}.json")


class User:
    def __init__(self, name: str, surname: str, birth_date: date, city: str,
                 country: str, languages: list[str], user_id: str | None = None):

        self.name: str = name
        self.surname: str = surname
        self.birth_date: date = birth_date
        self.city: str = city
        self.country: str = country
        self.languages: list[str] = list(languages)  # copy, so the caller's list is not shared

        # A new user gets a fresh ID; a user loaded from disk keeps the one it had
        if user_id is None:
            user_id = str(uuid.uuid4())
        self._user_id: str = user_id

        # A new user has no points, no trips and is not a guide yet
        self._travel_points: int = 0
        self.guide_profile: object | None = None

    @property
    def user_id(self) -> str:
        """Return the user's unique ID (read-only)."""
        return self._user_id

    # Calculate age and subtract one year if the birthday hasn't occurred yet this year.
    @property
    def age(self) -> int:
        today: date = date.today()
        age: int = today.year - self.birth_date.year

        if (today.month, today.day) < (
                self.birth_date.month, self.birth_date.day
        ):
            age -= 1

        return age


    @property
    def travel_points(self) -> int:
        """Return the user's current travel points balance."""
        return self._travel_points

    def earn_points(self, amount: int) -> None:
        """Add travel points to the user's balance."""
        if amount <= 0:
            raise InvalidPointsAmountError(amount)

        self._travel_points += amount

    def redeem_points(self, amount: int) -> None:
        """Redeem travel points if the user has enough points."""
        if amount <= 0:
            raise InvalidPointsAmountError(amount)

        if amount > self._travel_points:
            raise InsufficientPointsError(
                amount, self._travel_points
            )

        self._travel_points -= amount

    def to_dict(self) -> dict:
        """Convert the user into a dictionary suitable for JSON."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'surname': self.surname,
            'birth_date': self.birth_date.isoformat(),
            'city': self.city,
            'country': self.country,
            'languages': list(self.languages),
            'travel_points': self.travel_points,
        }

    @classmethod
    def from_dict(cls, data: dict) -> User:
        """Create a user from a dictionary, restoring their travel points."""
        balance: int = data['travel_points']

        # Validate the saved balance before creating the user.
        if balance < 0:
            raise InvalidTravelPointsBalanceError(balance)

        user: User = cls(
            name=data['name'],
            surname=data['surname'],
            birth_date=date.fromisoformat(data['birth_date']),
            city=data['city'],
            country=data['country'],
            languages=data['languages'],
            user_id=data['user_id']

        )

        # Restore the saved points; they cannot go through the constructor.
        user._travel_points = balance

        return user

    def save(self, directory: str = USERS_DIR) -> None:
        """Save the user to '<directory>/<user_id>.json', creating the directory if needed."""
        path: str = _user_path(self.user_id, directory)  # validate before touching the disk
        os.makedirs(directory, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, user_id: str, directory: str = USERS_DIR) -> User:
        """Load the user with the given ID from the directory."""
        path: str = _user_path(user_id, directory)
        try:
            with open(path, "r") as f:
                data: dict = json.load(f)
        except FileNotFoundError:
            # Hide the low-level error: the caller only needs to know the user does not exist.
            raise UserNotFoundError(user_id) from None

        return cls.from_dict(data)






