"""Activity hierarchy: Activity, GuideTour and Pubcrawl."""
from __future__ import annotations

from exceptions.errors import InvalidTypeError


class Activity:
    events_count: int = 0

    def __init__(self, name: str, location: str, price: float) -> None:
        self.name: str = name
        self.location: str = location
        self.price: float = price
        Activity.events_count += 1

    def describe(self) -> str:
        return f'\nEvent: {self.name}\nLocation: {self.location}\nPrice: {self.price}'

    def __lt__(self, other: Activity) -> bool:
        return self.price < other.price

    def to_dict(self) -> dict:
        """Convert the activity to a dictionary. Subclasses extend it with their own fields."""
        return {
            'name': self.name,
            'location': self.location,
            'price': self.price,
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
    def __init__(self, name: str, location: str, price: float, tips_included: bool) -> None:
        super().__init__(name, location, price)
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
        return cls(data['name'], data['location'], data['price'], data['tips_included'])


class Pubcrawl(Activity):
    def __init__(self, name: str, location: str, price: float, drinks_included: int) -> None:
        super().__init__(name, location, price)
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
        return cls(data['name'], data['location'], data['price'], data['drinks_included'])
