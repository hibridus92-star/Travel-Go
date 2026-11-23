"""Fixtures shared by several test files. pytest finds this file by itself."""
from datetime import date, datetime
from decimal import Decimal

import pytest

from models.activity import GuideTour, Pubcrawl
from models.trip import Trip


@pytest.fixture
def walk() -> GuideTour:
    return GuideTour("Historic Walk", "Central Square", Decimal("10.00"), datetime(2027, 3, 14, 10, 0), True)


@pytest.fixture
def pub_night() -> Pubcrawl:
    return Pubcrawl("Drinkers Night", "The Dolphin Shire", Decimal("25.90"), datetime(2027, 3, 14, 21, 0), 2)


@pytest.fixture
def empty_trip() -> Trip:
    """A draft trip from 12 to 16 March 2027, with no activities and no participants."""
    return Trip(1, "La Valleta", date(2027, 3, 12), date(2027, 3, 16), [])