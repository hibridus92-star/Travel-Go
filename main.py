"""Demo: exercise the Travel&Go domain model and its JSON persistence."""
import json
import os
import shutil
from datetime import date

from exceptions.errors import (
    DuplicateParticipantError,
    ParticipantNotFoundError,
    InvalidTravelPointsBalanceError,
    InvalidUserIdError,
    UserNotFoundError,
)
from models.activity import GuideTour, Pubcrawl
from models.trip import Trip
from models.user import User

DATA_FILE: str = os.path.join("data", "malta.json")


def demo_trip_persistence() -> None:
    """Demonstrate that a trip and its activities survive saving and loading."""
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

    print(isinstance(loaded_trip.activities[0], GuideTour))
    print(isinstance(loaded_trip.activities[1], Pubcrawl))


def demo_participants(activity: GuideTour) -> None:
    """Demonstrate how a Trip manages its participants."""
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
    """Demonstrate that participants survive saving and loading."""
    new_file: str = os.path.join("data", "test_trip.json")
    old_file: str = os.path.join("data", "malta_old.json")

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
    print(old_trip.destination, old_trip.participant_ids)  # La Valleta []


def demo_user_persistence() -> None:
    """Demonstrate that a user survives saving and loading."""
    user_file: str = os.path.join("data", "test_user.json")

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
    """Demonstrate saving and loading users by ID, one file per user."""
    demo_dir: str = os.path.join("data", "demo_users")
    shutil.rmtree(demo_dir, ignore_errors=True)  # start from a clean state

    ana: User = User("Ana", "Lopez", date(2000, 3, 10), "Murcia", "Spain", ["es"])
    ana.earn_points(100)
    luis: User = User("Luis", "Gil", date(1990, 1, 3), "Madrid", "Spain", ["es", "en"])

    # The folder does not exist yet: save() must create it
    print("Folder exists before saving:", os.path.isdir(demo_dir))  # False
    ana.save(demo_dir)
    luis.save(demo_dir)
    print("Folder exists after saving:", os.path.isdir(demo_dir))   # True
    print("Files saved:", len(os.listdir(demo_dir)))                # 2

    # Load one user by ID
    loaded: User = User.load(ana.user_id, demo_dir)
    print("Loaded:", loaded.name, "| same ID:", loaded.user_id == ana.user_id,
          "| points:", loaded.travel_points)                        # Ana | True | 100

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


def main() -> None:
    historic_walk: GuideTour = GuideTour("Historic Walk", "Central Square", 10.00, True)

    # Active demo
    print("--- User storage ---")
    demo_user_storage()

    # Previous demos: uncomment the ones you want to run again
    # print("\n--- User persistence ---")
    # demo_user_persistence()
    # print("\n--- Trip persistence ---")
    # demo_trip_persistence()
    # print("\n--- Participants ---")
    # demo_participants(historic_walk)
    # print("\n--- Participant persistence ---")
    # demo_participant_persistence()


if __name__ == "__main__":
    main()