

"""User: a traveller who owns trips and accumulates travel points."""
from __future__ import annotations

from datetime import date

from models.trip import Trip


class User:
    def __init__(self, name: str, surname: str, birth_date: date, city: str,
                 country: str, languages: list[str]) -> None:
        self.name: str = name
        self.surname: str = surname
        self.birth_date: date = birth_date
        self.city: str = city
        self.country: str = country
        self.languages: list[str] = list(languages)  # copy, so the caller's list is not shared

        # A new user has no points, no trips and is not a guide yet
        self._travel_points: int = 0
        self.guide_profile: object | None = None
        self.trips: list[Trip] = []

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



