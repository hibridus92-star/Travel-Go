"""Activity hierarchy: Activity, GuideTour and Pubcrawl."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from exceptions.errors import InvalidActivityNameError, InvalidStartTimeError, InvalidTypeError
from models.money import parse_price, price_from_json


def _validate_name(name: object) -> str:
    """Return the name without surrounding spaces, or raise if it is not usable."""
    if not isinstance(name, str) or not name.strip():
        raise InvalidActivityNameError(name)
    return name.strip()


def _validate_start(starts_at: object) -> datetime:
    """Return the start if it is a datetime without time zone, or raise."""
    # A plain date is not accepted: datetime is a subclass of date, but not the other way round.
    if not isinstance(starts_at, datetime):
        raise InvalidStartTimeError(starts_at, "it must be a datetime (a date and a time)")
    if starts_at.tzinfo is not None:
        raise InvalidStartTimeError(starts_at, "it must not have a time zone, use the local time of the destination")
    return starts_at


def _start_from_json(value: object) -> datetime:
    """Read a start saved as text in ISO format (for example '2027-03-14T10:00:00')."""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InvalidStartTimeError(value, "it is not a valid ISO date and time") from None
    return _validate_start(value)


class Activity:
    events_count: int = 0

    def __init__(self, name: str, location: str, price: Decimal | int | str, starts_at: datetime) -> None:
        self._name: str = _validate_name(name)
        self.location: str = location
        self._price: Decimal = parse_price(price)
        self._starts_at: datetime = _validate_start(starts_at)
        # Only reached when name, price and start are valid, so a rejected activity is not counted.
        Activity.events_count += 1

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = _validate_name(value)

    @property
    def price(self) -> Decimal:
        return self._price

    @price.setter
    def price(self, value: Decimal | int | str) -> None:
        self._price = parse_price(value)

    @property
    def starts_at(self) -> datetime:
        """The start of the activity. It has no setter: an activity that is already part of a trip cannot move."""
        return self._starts_at

    def describe(self) -> str:
        return (
            f'\nEvent: {self.name}\nLocation: {self.location}'
            f'\nStarts: {self.starts_at:%Y-%m-%d %H:%M}\nPrice: {self.price}'
        )

    def __lt__(self, other: Activity) -> bool:
        return self.price < other.price

    def to_dict(self) -> dict:
        """Convert the activity to a dictionary. Subclasses extend it with their own fields.

        The price is saved as text because JSON has no exact decimal type.
        """
        return {
            'name': self.name,
            'location': self.location,
            'price': str(self.price),
            'starts_at': self.starts_at.isoformat(),
        }

    @staticmethod
    def activity_from_dict(data: dict) -> Activity:
        """Build the right subclass from a dictionary, based on its 'type' field."""
        activity_type: str = data['type']
        if activity_type == 'GuideTour':
            return GuideTour.to_activity(data)
        if activity_type == 'Pubcrawl':
            return Pubcrawl.to_activity(data)
        raise InvalidTypeError(activity_type)


class GuideTour(Activity):
    def __init__(self, name: str, location: str, price: Decimal | int | str, starts_at: datetime, tips_included: bool) -> None:
        super().__init__(name, location, price, starts_at)
        self.tips_included: bool = tips_included

    def describe(self) -> str:
        return f'{super().describe()}\nTips included: {self.tips_included}\n'

    def to_dict(self) -> dict:
        data: dict = super().to_dict()
        data['tips_included'] = self.tips_included
        data['type'] = 'GuideTour'  # lets activity_from_dict know which class to rebuild
        return data

    @classmethod
    def to_activity(cls, data: dict) -> GuideTour:
        return cls(data['name'], data['location'], price_from_json(data['price']), _start_from_json(data['starts_at']),
                   data['tips_included'])


class Pubcrawl(Activity):
    def __init__(self, name: str, location: str, price: Decimal | int | str, starts_at: datetime, drinks_included: int) -> None:
        super().__init__(name, location, price, starts_at)
        self.drinks_included: int = drinks_included

    def describe(self) -> str:
        return f'{super().describe()}\nDrinks included: {self.drinks_included}\n'

    def to_dict(self) -> dict:
        data: dict = super().to_dict()
        data['drinks_included'] = self.drinks_included
        data['type'] = 'Pubcrawl'
        return data

    @classmethod
    def to_activity(cls, data: dict) -> Pubcrawl:
        return cls(data['name'], data['location'], price_from_json(data['price']), _start_from_json(data['starts_at']),
                   data['drinks_included'])