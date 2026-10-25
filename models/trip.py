"""Trip: an aggregation of activities, with JSON persistence."""
from __future__ import annotations

import json

from models.activity import Activity, Pubcrawl
from exceptions.errors import (
    DuplicateParticipantError,
    ParticipantNotFoundError,
)


class Trip:
    def __init__(self, id_number: int, destination: str, activities: list[Activity],participant_ids: list[str] | None = None):
        self.id_number: int = id_number
        self.destination: str = destination
        self.activities: list[Activity] = activities
        self._participant_ids: list[str] = (
            list(participant_ids) if participant_ids is not None else []
        )

    @property
    def participant_ids(self) -> list[str]:
        """Return a copy of the trip's participant IDs."""
        return list(self._participant_ids)

    def add_participant(self, user_id: str) -> None:
        """Add a participant to the trip."""
        if user_id in self._participant_ids:
            raise DuplicateParticipantError(user_id)

        self._participant_ids.append(user_id)

    def remove_participant(self, user_id: str) -> None:
        """Remove a participant from the trip."""
        if user_id not in self._participant_ids:
            raise ParticipantNotFoundError(user_id)

        self._participant_ids.remove(user_id)

    def event_total_cost(self) -> float:
        cost: float = 0.0
        for activity in self.activities:
            cost += activity.price
        return cost

    def describe(self) -> str:
        description: str = ''
        for activity in self.activities:
            description += activity.describe()
        return description

    def alcoholic_events(self) -> int:
        alcoholic: int = 0
        for activity in self.activities:
            alcoholic += isinstance(activity, Pubcrawl)
        return alcoholic

    def to_dict(self) -> dict:
        activities_as_dicts: list[dict] = [activity.to_dict() for activity in self.activities]
        return {
            'id_number': self.id_number,
            'destination': self.destination,
            'activities': activities_as_dicts,
            'participant_ids': self.participant_ids
        }

    def save(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, filename: str) -> Trip:
        """Load a trip from a JSON file. If the file does not exist, return an empty trip."""
        try:
            with open(filename, "r") as f:
                data: dict = json.load(f)
        except FileNotFoundError:
            print("File not found")
            return cls(0, "", [])

        activities: list[Activity] = [
            Activity.activity_from_dict(a) for a in data['activities']
        ]

        participant_ids: list[str] = data.get('participant_ids', [])
        return cls(data['id_number'], data['destination'], activities, participant_ids)
