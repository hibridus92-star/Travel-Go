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
from datetime import date

from exceptions.errors import (
    DuplicateParticipantError,
    InsufficientPointsError,
    InvalidTypeError,
    InvalidPointsAmountError,
    InvalidTravelPointsBalanceError,
    InvalidUserIdError,
    ParticipantNotFoundError,
    UserNotFoundError,
)
from models.activity import Activity, GuideTour, Pubcrawl
from models.trip import Trip
from models.user import User

DATA_DIR: str = "data"
DATA_FILE: str = os.path.join(DATA_DIR, "malta.json")


def demo_activities() -> None:
    """Activities: types, description, comparison by price and creation counter."""
    before: int = Activity.events_count

    historic_walk: GuideTour = GuideTour("Historic Walk", "Central Square", 10.00, True)
    drinkers_night: Pubcrawl = Pubcrawl("Drinkers Night", "The Dolphin Shire", 25.90, 2)

    print(historic_walk.describe())
    print(drinkers_night.describe())

    print("Historic Walk is cheaper than Drinkers Night:", historic_walk < drinkers_night)
    print("Activities created in this demo:", Activity.events_count - before)

    # A saved activity with an unknown type must be rejected when loading
    try:
        Activity.activity_from_dict({"type": "Museum", "name": "Prado"})
    except InvalidTypeError as e:
        print("Rejected:", e)


def demo_trip_persistence() -> None:
    """Trips: total cost, alcohol-related count and a JSON round trip."""
    historic_walk: GuideTour = GuideTour("Historic Walk", "Central Square", 10.00, True)
    drinkers_night: Pubcrawl = Pubcrawl("Drinkers Night", "The Dolphin Shire", 25.90, 2)
    malta: Trip = Trip(2334, "La Valleta", [historic_walk, drinkers_night])

    malta.save(DATA_FILE)
    print("Trip saved successfully.")

    loaded_trip: Trip = Trip.load(DATA_FILE)
    print("\nTrip loaded successfully.")
    print(f"Destination: {loaded_trip.destination}")
    print(f"ID: {loaded_trip.id_number}")
    print(f"Total cost: {loaded_trip.event_total_cost()}")
    print(f"Alcoholic events: {loaded_trip.alcoholic_events()}")
    print("\nDescription of the loaded trip:", loaded_trip.describe())

    print("First activity is a GuideTour:", isinstance(loaded_trip.activities[0], GuideTour))
    print("Second activity is a Pubcrawl:", isinstance(loaded_trip.activities[1], Pubcrawl))


def demo_participants() -> None:
    """Trips: how a trip manages its participants."""
    activity: GuideTour = GuideTour("Historic Walk", "Central Square", 10.00, True)

    # 1. A trip without participants starts empty
    trip01: Trip = Trip(1, "Rome", [activity])
    print("1:", trip01.participant_ids)

    # 2. Two trips: adding to one must not affect the other
    trip02: Trip = Trip(2, "Paris", [])
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
    trip03: Trip = Trip(3, "Lima", [], ids)
    ids.append("c")
    print("7: trip03 =", trip03.participant_ids, "| original list =", ids)


def demo_participant_persistence() -> None:
    """Trips: participants survive saving and loading."""
    new_file: str = os.path.join(DATA_DIR, "test_trip.json")
    old_file: str = os.path.join(DATA_DIR, "malta_old.json")

    # Round trip
    trip: Trip = Trip(1, "Malta", [])
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

    # Old format: a file without the participant_ids field
    with open(old_file, "w") as f:
        json.dump({"id_number": 2334, "destination": "La Valleta", "activities": []}, f)
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
    "trips": demo_trip_persistence,
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