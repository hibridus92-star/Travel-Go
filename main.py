"""Demo: exercise the Travel&Go domain model and its JSON persistence.

Usage:
    python main.py                      run every demo
    python main.py activities users     run only the named demos
"""
import json
import os
import shutil
import sys
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal

from exceptions.errors import (
    ActivityNotInTripError,
    ActivityOutsideTripDatesError,
    DuplicateParticipantError,
    InsufficientPointsError,
    InvalidActivityNameError,
    InvalidPriceError,
    InvalidStartTimeError,
    InvalidTripDatesError,
    InvalidTripFileError,
    InvalidTypeError,
    InvalidPointsAmountError,
    InvalidTravelPointsBalanceError,
    InvalidUserIdError,
    ParticipantNotFoundError,
    TripLockedError,
    UserNotFoundError,
)
from models.activity import Activity, GuideTour, Pubcrawl
from models.trip import Trip, TripStatus
from models.user import User

DATA_DIR: str = "data"
DATA_FILE: str = os.path.join(DATA_DIR, "malta.json")

# Sample values shared by the demos: a five-day trip and two evening and morning activities
TRIP_START: date = date(2027, 3, 12)
TRIP_END: date = date(2027, 3, 16)
MORNING: datetime = datetime(2027, 3, 14, 10, 0)
NIGHT: datetime = datetime(2027, 3, 14, 21, 0)


def demo_activities() -> None:
    """Activities: types, description, comparison by price and creation counter."""
    before: int = Activity.events_count

    historic_walk: GuideTour = GuideTour("Historic Walk", "Central Square", Decimal("10.00"), MORNING, True)
    drinkers_night: Pubcrawl = Pubcrawl("Drinkers Night", "The Dolphin Shire", Decimal("25.90"), NIGHT, 2)

    print(historic_walk.describe())
    print(drinkers_night.describe())

    print("Historic Walk is cheaper than Drinkers Night:", historic_walk < drinkers_night)
    print("Activities created in this demo:", Activity.events_count - before)

    # A saved activity with an unknown type must be rejected when loading
    try:
        Activity.activity_from_dict({"type": "Museum", "name": "Prado"})
    except InvalidTypeError as e:
        print("Rejected:", e)


def demo_prices() -> None:
    """Prices: why money is not a float, what is rejected and how old files still load."""
    # The problem with float
    print("float:   0.1 + 0.2 =", 0.1 + 0.2)  # 0.30000000000000004
    print("Decimal: 0.10 + 0.20 =", Decimal("0.10") + Decimal("0.20"))  # 0.30

    # A price is stored with exactly two decimals and saved as text
    walk: GuideTour = GuideTour("Historic Walk", "Central Square", "10", MORNING, True)
    print("Price stored as:", walk.price)  # 10.00
    print("Price saved as:", repr(walk.to_dict()["price"]))  # '10.00'

    # Invalid prices are rejected, and the activity is not created
    before: int = Activity.events_count
    for bad_price in (-5, "12.345", 9.99, "abc", True):
        try:
            GuideTour("Test", "Somewhere", bad_price, MORNING, False)
        except InvalidPriceError as e:
            print("Rejected price:", e)

    # Invalid names are rejected too
    try:
        Pubcrawl("   ", "Somewhere", "5.00", NIGHT, 1)
    except InvalidActivityNameError as e:
        print("Rejected name:", e)
    print("Activities created by mistake:", Activity.events_count - before)  # 0

    # A file saved before prices became decimals still loads
    old_data: dict = {
        "type": "GuideTour", "name": "Old Walk", "location": "Square",
        "price": 25.9, "starts_at": "2027-03-14T10:00:00", "tips_included": True,
    }
    print("Old float price loaded as:", Activity.activity_from_dict(old_data).price)  # 25.90


def demo_trip_persistence() -> None:
    """Trips: dates, price per person, alcohol-related count and a JSON round trip."""
    historic_walk: GuideTour = GuideTour("Historic Walk", "Central Square", Decimal("10.00"), MORNING, True)
    drinkers_night: Pubcrawl = Pubcrawl("Drinkers Night", "The Dolphin Shire", Decimal("25.90"), NIGHT, 2)
    malta: Trip = Trip(2334, "La Valleta", TRIP_START, TRIP_END, [historic_walk, drinkers_night])

    malta.save(DATA_FILE)
    print("Trip saved successfully.")

    loaded_trip: Trip = Trip.load(DATA_FILE)
    print("\nTrip loaded successfully.")
    print(f"Destination: {loaded_trip.destination}")
    print(f"ID: {loaded_trip.id_number}")
    print(f"Dates: {loaded_trip.start_date} to {loaded_trip.end_date}")
    print(f"Status: {loaded_trip.status.value}")
    print(f"Price per person: {loaded_trip.price_per_person()}")
    print(f"Alcoholic events: {loaded_trip.alcoholic_events()}")
    print("\nDescription of the loaded trip:", loaded_trip.describe())

    print("First activity is a GuideTour:", isinstance(loaded_trip.activities[0], GuideTour))
    print("Second activity is a Pubcrawl:", isinstance(loaded_trip.activities[1], Pubcrawl))


def demo_trip_dates() -> None:
    """Trips: dates, the start of each activity and the rule that activities fall inside the trip."""
    # 1. Dates are mandatory and must be in order
    try:
        Trip(1, "Rome", TRIP_END, TRIP_START, [])
    except InvalidTripDatesError as e:
        print("1:", e)

    # 2. An activity needs a date and a time, not only a date
    try:
        GuideTour("Walk", "Somewhere", "10.00", date(2027, 3, 14), True)  # type: ignore[arg-type]
    except InvalidStartTimeError as e:
        print("2:", e)

    # 3. Activities inside the dates are accepted, the first and last day included
    trip: Trip = Trip(1, "La Valleta", TRIP_START, TRIP_END, [])
    trip.add_activity(GuideTour("Opening Walk", "Central Square", "10.00", datetime(2027, 3, 12, 0, 0), True))
    trip.add_activity(GuideTour("Farewell Walk", "Central Square", "10.00", datetime(2027, 3, 16, 23, 59), True))
    print("3: activities in the trip:", [a.name for a in trip.activities])

    # 4. An activity outside the dates is rejected and the trip does not change
    late: Pubcrawl = Pubcrawl("Late Night", "The Dolphin Shire", "25.90", datetime(2027, 3, 17, 0, 0), 2)
    try:
        trip.add_activity(late)
    except ActivityOutsideTripDatesError as e:
        print("4:", e)
    print("   activities unchanged:", len(trip.activities))

    # 5. Removing an activity that is not in the trip
    try:
        trip.remove_activity(late)
    except ActivityNotInTripError as e:
        print("5:", e)

    # 6. The same activity can belong to two trips
    shared: GuideTour = GuideTour("Shared Walk", "Central Square", "10.00", MORNING, True)
    first: Trip = Trip(2, "La Valleta", TRIP_START, TRIP_END, [shared])
    second: Trip = Trip(3, "La Valleta", date(2027, 3, 14), date(2027, 3, 14), [shared])
    print("6: same object in both trips:", first.activities[0] is second.activities[0])

    # 7. A file saved before trips had dates cannot be loaded, and the error names the field
    old_file: str = os.path.join(DATA_DIR, "trip_without_dates.json")
    with open(old_file, "w") as f:
        json.dump({"id_number": 2334, "destination": "La Valleta", "activities": []}, f)
    try:
        Trip.load(old_file)
    except InvalidTripFileError as e:
        print("7:", e)


def demo_trip_lifecycle() -> None:
    """Trips: draft and purchased, the lock on purchased trips and the price per person."""
    walk: GuideTour = GuideTour("Historic Walk", "Central Square", "10.00", MORNING, True)
    night: Pubcrawl = Pubcrawl("Drinkers Night", "The Dolphin Shire", "25.90", NIGHT, 2)
    trip: Trip = Trip(1, "La Valleta", TRIP_START, TRIP_END, [walk, night])

    # 1. A new trip is a draft and can be edited
    print("1: status:", trip.status.value)
    trip.add_participant("ana")
    trip.add_participant("luis")

    # 2. Every price is per person, and the total depends on the participants
    print("2: price per person:", trip.price_per_person(), "| total for", len(trip.participant_ids), "people:", trip.total_price())

    # 3. Once purchased the trip is locked
    trip.mark_purchased()
    print("3: status:", trip.status.value, "| is purchased:", trip.status is TripStatus.PURCHASED)
    for label, change in (
        ("add an activity", lambda: trip.add_activity(walk)),
        ("remove an activity", lambda: trip.remove_activity(walk)),
        ("add a participant", lambda: trip.add_participant("eva")),
        ("remove a participant", lambda: trip.remove_participant("ana")),
        ("purchase again", trip.mark_purchased),
    ):
        try:
            change()
        except TripLockedError as e:
            print(f"   {label}: rejected ->", e)
    print("   nothing changed:", len(trip.activities), "activities,", trip.participant_ids, "| total:", trip.total_price())

    # 4. The status survives saving and loading
    status_file: str = os.path.join(DATA_DIR, "purchased_trip.json")
    trip.save(status_file)
    print("4: loaded status:", Trip.load(status_file).status.value)


def demo_participants() -> None:
    """Trips: how a trip manages its participants."""
    activity: GuideTour = GuideTour("Historic Walk", "Central Square", Decimal("10.00"), MORNING, True)

    # 1. A trip without participants starts empty
    trip01: Trip = Trip(1, "Rome", TRIP_START, TRIP_END, [activity])
    print("1:", trip01.participant_ids)

    # 2. Two trips: adding to one must not affect the other
    trip02: Trip = Trip(2, "Paris", TRIP_START, TRIP_END, [])
    trip01.add_participant("a")
    print("2: trip01 =", trip01.participant_ids, "| trip02 =", trip02.participant_ids)

    # 3. Several participants, in order
    trip01.add_participant("b")
    print("3:", trip01.participant_ids)

    # 4. Duplicate: must fail, and the list must not change
    try:
        trip01.add_participant("a")
    except DuplicateParticipantError as e:
        print("4:", e)
    print("   list unchanged:", trip01.participant_ids)

    # 5. Removing someone who is not there
    try:
        trip01.remove_participant("z")
    except ParticipantNotFoundError as e:
        print("5:", e)

    # 6. The returned list is a copy: appending to it must not affect the trip
    trip01.participant_ids.append("x")
    print("6:", trip01.participant_ids)

    # 7. The constructor copies the list it receives
    ids: list[str] = ["a", "b"]
    trip03: Trip = Trip(3, "Lima", TRIP_START, TRIP_END, [], ids)
    ids.append("c")
    print("7: trip03 =", trip03.participant_ids, "| original list =", ids)


def demo_participant_persistence() -> None:
    """Trips: participants survive saving and loading."""
    new_file: str = os.path.join(DATA_DIR, "test_trip.json")
    old_file: str = os.path.join(DATA_DIR, "malta_old.json")

    # Round trip
    trip: Trip = Trip(1, "Malta", TRIP_START, TRIP_END, [])
    trip.add_participant("a")
    trip.add_participant("b")
    trip.save(new_file)
    loaded: Trip = Trip.load(new_file)
    print("Loaded participants:", loaded.participant_ids)  # ['a', 'b']

    # The validation survives loading
    try:
        loaded.add_participant("a")
    except DuplicateParticipantError as e:
        print("Duplicate rejected:", e)

    # Older format: a file without the participant_ids and status fields
    with open(old_file, "w") as f:
        json.dump({
            "id_number": 2334, "destination": "La Valleta",
            "start_date": "2027-03-12", "end_date": "2027-03-16", "activities": [],
        }, f)
    old_trip: Trip = Trip.load(old_file)
    print("Old file loaded:", old_trip.destination, old_trip.participant_ids)  # La Valleta []


def demo_user_points() -> None:
    """Users: age, travel points and their validation."""
    ana: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])
    print("Birth date:", ana.birth_date, "| computed age:", ana.age)
    print("User ID:", ana.user_id)
    try:
        ana.user_id = "another-id"  # type: ignore[misc]
    except AttributeError as e:
        print("Rejected: the ID cannot be reassigned:", e)
    print("Initial points:", ana.travel_points)

    ana.earn_points(100)
    ana.redeem_points(30)
    print("After earning 100 and redeeming 30:", ana.travel_points)

    try:
        ana.redeem_points(500)
    except InsufficientPointsError as e:
        print("Rejected:", e)
    print("Balance unchanged:", ana.travel_points)

    try:
        ana.earn_points(-5)
    except InvalidPointsAmountError as e:
        print("Rejected:", e)

    try:
        ana.travel_points = 999  # type: ignore[misc]
    except AttributeError as e:
        print("Rejected: the balance cannot be assigned directly:", e)


def demo_user_persistence() -> None:
    """Users: conversion to and from dictionaries."""
    user_file: str = os.path.join(DATA_DIR, "test_user.json")

    # Round trip through a real file
    ana: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])
    ana.earn_points(100)
    with open(user_file, "w") as f:
        json.dump(ana.to_dict(), f, indent=4)

    with open(user_file, "r") as f:
        loaded: User = User.from_dict(json.load(f))
    print("Same ID:", loaded.user_id == ana.user_id)
    print("Points:", loaded.travel_points)                        # 100
    print("birth_date type:", type(loaded.birth_date).__name__)   # date

    # The lists are independent copies
    data: dict = ana.to_dict()
    data["languages"].append("en")
    print("Ana's languages:", ana.languages)                      # ['es']

    # A user with zero points can be restored
    eva: User = User("Eva", "Ruiz", date(2000, 6, 1), "Lima", "Peru", ["es"])
    print("Zero points:", User.from_dict(eva.to_dict()).travel_points)  # 0

    # A corrupted balance is rejected
    corrupted: dict = ana.to_dict()
    corrupted["travel_points"] = -50
    try:
        User.from_dict(corrupted)
    except InvalidTravelPointsBalanceError as e:
        print("Rejected:", e)


def demo_user_storage() -> None:
    """Users: one file per user, loaded by ID."""
    demo_dir: str = os.path.join(DATA_DIR, "demo_users")
    shutil.rmtree(demo_dir, ignore_errors=True)  # start from a clean state

    ana: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])
    ana.earn_points(100)
    luis: User = User("Luis", "Gil", date(1990, 1, 3), "Madrid", "Spain", ["es", "en"])

    # The folder does not exist yet: save() must create it
    print("Folder exists before saving:", os.path.isdir(demo_dir))  # False
    ana.save(demo_dir)
    luis.save(demo_dir)
    print("Folder exists after saving:", os.path.isdir(demo_dir))   # True
    print("Files saved:", sorted(os.listdir(demo_dir)))

    # Load one user by ID
    loaded: User = User.load(ana.user_id, demo_dir)
    print("Loaded:", loaded.name, "| same ID:", loaded.user_id == ana.user_id,
          "| points:", loaded.travel_points)

    # An ID with no file must fail, not return an empty user
    try:
        User.load("00000000-0000-0000-0000-000000000000", demo_dir)
    except UserNotFoundError as e:
        print("Not found:", e)

    # An ID that tries to leave the folder must be rejected
    try:
        User.load("../secret", demo_dir)
    except InvalidUserIdError as e:
        print("Invalid ID:", e)

    # The same rule applies when saving, and nothing is written
    sneaky: User = User("Eve", "Ruiz", date(2000, 6, 1), "Lima", "Peru", ["es"],
                        user_id="../escape")
    try:
        sneaky.save(demo_dir)
    except InvalidUserIdError as e:
        print("Save rejected:", e)
    print("Files saved after the rejections:", len(os.listdir(demo_dir)))  # still 2


DEMOS: dict[str, Callable[[], None]] = {
    "activities": demo_activities,
    "prices": demo_prices,
    "trips": demo_trip_persistence,
    "trip-dates": demo_trip_dates,
    "trip-lifecycle": demo_trip_lifecycle,
    "participants": demo_participants,
    "participant-persistence": demo_participant_persistence,
    "user-points": demo_user_points,
    "user-persistence": demo_user_persistence,
    "user-storage": demo_user_storage,
}


def main() -> None:
    names: list[str] = sys.argv[1:] or list(DEMOS)

    unknown: list[str] = [name for name in names if name not in DEMOS]
    if unknown:
        print("Unknown demo:", ", ".join(unknown))
        print("Available demos:", ", ".join(DEMOS))
        sys.exit(2)

    os.makedirs(DATA_DIR, exist_ok=True)

    for name in names:
        print(f"\n=== {name} ===")
        DEMOS[name]()


if __name__ == "__main__":
    main()