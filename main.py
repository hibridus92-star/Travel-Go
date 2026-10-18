"""Demo: build a trip, save it to JSON and load it back."""
import os

from exceptions.errors import (
    DuplicateParticipantError,
    ParticipantNotFoundError,
)

from models.activity import GuideTour, Pubcrawl
from models.trip import Trip
from datetime import date
from models.user import User


DATA_FILE: str = os.path.join("data", "malta.json")


def main() -> None:
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


    # 1. A trip without participants starts empty
    trip01: Trip = Trip(1, "Rome", [historic_walk])
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

if __name__ == "__main__":
    main()
