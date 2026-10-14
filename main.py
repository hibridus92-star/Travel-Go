"""Demo: build a trip, save it to JSON and load it back."""
import os

from models.activity import GuideTour, Pubcrawl
from models.trip import Trip
from datetime import date
from models.User import User

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

    users = [
        User("Ana", "López", date(2000, 3, 10), "Murcia", "España", ["es"]),
        User("Luis", "García", date(2000, 12, 20), "Madrid", "España", ["es"]),
        User("Eva", "Martín", date(2000, 10, 14), "Alicante", "España", ["es"]),
    ]

    for user in users:
        print(user.name, user.age)


if __name__ == "__main__":
    main()
