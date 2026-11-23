"""Trip: an aggregation of activities between two dates, with a draft and purchased lifecycle."""
from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from models.activity import Activity, Pubcrawl
from exceptions.errors import (
    ActivityNotInTripError,
    ActivityOutsideTripDatesError,
    DuplicateParticipantError,
    InvalidTripDatesError,
    InvalidTripFileError,
    ParticipantNotFoundError,
    TripLockedError,
)


class TripStatus(Enum):
    """The two states of a trip. A draft can be edited, a purchased trip is locked."""

    DRAFT = "draft"
    PURCHASED = "purchased"


def _is_plain_date(value: object) -> bool:
    """True for a date without time (datetime is a subclass of date, so it is excluded explicitly)."""
    return isinstance(value, date) and not isinstance(value, datetime)


def _read_date(data: dict, field: str) -> date:
    """Read a date saved as text in ISO format (for example '2027-03-12')."""
    try:
        value: object = data[field]
    except KeyError:
        raise InvalidTripFileError(field, "the field is missing") from None
    try:
        return date.fromisoformat(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise InvalidTripFileError(field, f"{value!r} is not a valid ISO date") from None


class Trip:
    def __init__(
        self,
        id_number: int,
        destination: str,
        start_date: date,
        end_date: date,
        activities: list[Activity],
        participant_ids: list[str] | None = None,
    ) -> None:
        if not (_is_plain_date(start_date) and _is_plain_date(end_date)):
            raise InvalidTripDatesError(start_date, end_date, "both must be dates without a time")
        if start_date > end_date:
            raise InvalidTripDatesError(start_date, end_date, "the trip cannot start after it ends")

        self.id_number: int = id_number
        self.destination: str = destination
        self._start_date: date = start_date
        self._end_date: date = end_date
        self._status: TripStatus = TripStatus.DRAFT
        self._activities: list[Activity] = []
        for activity in activities:
            self._check_inside_dates(activity)
            self._activities.append(activity)
        self._participant_ids: list[str] = (
            list(participant_ids) if participant_ids is not None else []
        )

    # --- read-only data ---------------------------------------------------

    @property
    def start_date(self) -> date:
        return self._start_date

    @property
    def end_date(self) -> date:
        return self._end_date

    @property
    def status(self) -> TripStatus:
        return self._status

    @property
    def activities(self) -> list[Activity]:
        """Return a copy of the trip's activities."""
        return list(self._activities)

    @property
    def participant_ids(self) -> list[str]:
        """Return a copy of the trip's participant IDs."""
        return list(self._participant_ids)

    # --- rules shared by the operations below -----------------------------

    def _check_editable(self, action: str) -> None:
        if self._status is TripStatus.PURCHASED:
            raise TripLockedError(self.id_number, action)

    def _check_inside_dates(self, activity: Activity) -> None:
        """An activity must start between the first and the last day of the trip, both included."""
        if not (self._start_date <= activity.starts_at.date() <= self._end_date):
            raise ActivityOutsideTripDatesError(
                activity.name, activity.starts_at, self._start_date, self._end_date
            )

    # --- activities -------------------------------------------------------

    def add_activity(self, activity: Activity) -> None:
        """Add an activity to a draft trip. It must take place within the trip dates."""
        self._check_editable("add an activity")
        self._check_inside_dates(activity)

        self._activities.append(activity)

    def remove_activity(self, activity: Activity) -> None:
        """Remove an activity from a draft trip."""
        self._check_editable("remove an activity")
        if activity not in self._activities:
            raise ActivityNotInTripError(activity.name)

        self._activities.remove(activity)

    # --- participants -----------------------------------------------------

    def add_participant(self, user_id: str) -> None:
        """Add a participant to a draft trip."""
        self._check_editable("add a participant")
        if user_id in self._participant_ids:
            raise DuplicateParticipantError(user_id)

        self._participant_ids.append(user_id)

    def remove_participant(self, user_id: str) -> None:
        """Remove a participant from a draft trip."""
        self._check_editable("remove a participant")
        if user_id not in self._participant_ids:
            raise ParticipantNotFoundError(user_id)

        self._participant_ids.remove(user_id)

    # --- lifecycle --------------------------------------------------------

    def mark_purchased(self) -> None:
        """Lock the trip. The purchase itself (payment and points) is not handled here."""
        self._check_editable("purchase it again")

        self._status = TripStatus.PURCHASED

    # --- prices -----------------------------------------------------------

    def price_per_person(self) -> Decimal:
        """The sum of the prices of the activities. Every price is per person."""
        cost: Decimal = Decimal("0.00")
        for activity in self._activities:
            cost += activity.price
        return cost

    def total_price(self) -> Decimal:
        """The price per person multiplied by the number of participants."""
        return self.price_per_person() * len(self._participant_ids)

    # --- description ------------------------------------------------------

    def describe(self) -> str:
        description: str = ''
        for activity in self._activities:
            description += activity.describe()
        return description

    def alcoholic_events(self) -> int:
        alcoholic: int = 0
        for activity in self._activities:
            alcoholic += isinstance(activity, Pubcrawl)
        return alcoholic

    # --- persistence ------------------------------------------------------

    def to_dict(self) -> dict:
        activities_as_dicts: list[dict] = [activity.to_dict() for activity in self._activities]
        return {
            'id_number': self.id_number,
            'destination': self.destination,
            'start_date': self._start_date.isoformat(),
            'end_date': self._end_date.isoformat(),
            'status': self._status.value,
            'activities': activities_as_dicts,
            'participant_ids': self.participant_ids
        }

    @classmethod
    def from_dict(cls, data: dict) -> Trip:
        """Build a trip from a dictionary. A missing or unreadable field raises InvalidTripFileError."""
        start_date: date = _read_date(data, 'start_date')
        end_date: date = _read_date(data, 'end_date')
        try:
            activities: list[Activity] = [Activity.activity_from_dict(a) for a in data['activities']]
            trip: Trip = cls(
                data['id_number'], data['destination'], start_date, end_date, activities,
                data.get('participant_ids', []),
            )
        except KeyError as error:
            raise InvalidTripFileError(str(error.args[0]), "the field is missing") from None

        saved_status: str = data.get('status', TripStatus.DRAFT.value)
        try:
            # The status is restored from inside the class, as User restores its points.
            trip._status = TripStatus(saved_status)
        except ValueError:
            raise InvalidTripFileError('status', f"{saved_status!r} is not a valid status") from None
        return trip

    def save(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, filename: str) -> Trip:
        """Load a trip from a JSON file. A file that does not exist raises FileNotFoundError."""
        with open(filename, "r") as f:
            data: dict = json.load(f)
        return cls.from_dict(data)