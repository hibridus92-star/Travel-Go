"""Trip: an aggregation of activities, with JSON persistence."""
from __future__ import annotations

import json

from models.activity import Activity, Pubcrawl


class Trip:
    def __init__(self, id_number: int, destination: str, activities: list[Activity]) -> None:
        self.id_number: int = id_number
        self.destination: str = destination
        self.activities: list[Activity] = activities

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
        return cls(data['id_number'], data['destination'], activities)
