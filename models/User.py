

"""User: a traveller who owns trips and accumulates travel points."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from models.trip import Trip

from exceptions.errors import (
    InvalidPointsAmountError,
    InsufficientPointsError,
)



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
        self.trips: list[Trip] = []

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




