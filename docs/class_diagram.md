# Class Diagram
 
Current domain model of Travel&Go. GitHub renders the diagram below automatically.
 
```mermaid
classDiagram
    class Activity {
        +events_count : int$
        #_name : str
        #_price : Decimal
        +name : str
        +location : str
        +price : Decimal
        +describe() str
        +to_dict() dict
        +activity_from_dict(data: dict)$ Activity
        +__lt__(other) bool
    }
 
    class GuideTour {
        +tips_included : bool
        +describe() str
        +to_dict() dict
        +to_activity(data: dict)$ GuideTour
    }
 
    class Pubcrawl {
        +drinks_included : int
        +describe() str
        +to_dict() dict
        +to_activity(data: dict)$ Pubcrawl
    }
 
    class money {
        <<module>>
        +CENT : Decimal$
        +parse_price(value) Decimal
        +price_from_json(value) Decimal
    }
 
    class Trip {
        +id_number : int
        +destination : str
        +activities : list~Activity~
        #_participant_ids : list~str~
        +participant_ids : list~str~
        +add_participant(user_id: str)
        +remove_participant(user_id: str)
        +event_total_cost() Decimal
        +describe() str
        +alcoholic_events() int
        +to_dict() dict
        +save(filename: str)
        +load(filename: str)$ Trip
    }
 
    class User {
        +name : str
        +surname : str
        +birth_date : date
        +city : str
        +country : str
        +languages : list~str~
        +guide_profile : object
        #_user_id : str
        #_travel_points : int
        +user_id : str
        +age : int
        +travel_points : int
        +earn_points(amount: int)
        +redeem_points(amount: int)
        +to_dict() dict
        +from_dict(data: dict)$ User
        +save(directory: str)
        +load(user_id: str, directory: str)$ User
    }
 
    class ActivityError
    class InvalidActivityNameError {
        +name : object
    }
    class InvalidPriceError {
        +price : object
        +reason : str
    }
    class InvalidTypeError {
        +type : str
    }
 
    class PointsError
    class InvalidPointsAmountError {
        +amount : int
    }
    class InsufficientPointsError {
        +amount : int
        +balance : int
    }
    class InvalidTravelPointsBalanceError {
        +balance : int
    }
 
    class ParticipantError
    class DuplicateParticipantError {
        +user_id : str
    }
    class ParticipantNotFoundError {
        +user_id : str
    }
 
    class UserStorageError
    class UserNotFoundError {
        +user_id : str
    }
    class InvalidUserIdError {
        +user_id : str
    }
 
    Activity <|-- GuideTour
    Activity <|-- Pubcrawl
    Trip o-- Activity : activities
    Activity ..> money : validates prices with
    GuideTour ..> money : reads saved prices with
    Pubcrawl ..> money : reads saved prices with
 
    ActivityError --|> Exception
    InvalidActivityNameError --|> ActivityError
    InvalidPriceError --|> ActivityError
    InvalidTypeError --|> ActivityError
    InvalidTravelPointsBalanceError --|> Exception
    PointsError --|> Exception
    InvalidPointsAmountError --|> PointsError
    InsufficientPointsError --|> PointsError
    ParticipantError --|> Exception
    DuplicateParticipantError --|> ParticipantError
    ParticipantNotFoundError --|> ParticipantError
    UserStorageError --|> Exception
    UserNotFoundError --|> UserStorageError
    InvalidUserIdError --|> UserStorageError
```
 
## Notes
 
- **Inheritance:** `GuideTour` and `Pubcrawl` extend `Activity`.
- **Aggregation:** a `Trip` holds references to `Activity` objects that exist independently of it.
- **Trips and users:** a `Trip` stores only the IDs of its participants, never `User` objects. The link is therefore not drawn as an association, which avoids circular references and keeps `trip.py` independent of `user.py`.
- **Static and class members** are marked with `$`.
- **Read-only properties:** `User.user_id`, `User.age`, `User.travel_points` and `Trip.participant_ids` cannot be assigned. Points only change through `earn_points` and `redeem_points`, and `participant_ids` returns a copy.
- **Validated properties:** `Activity.name` and `Activity.price` can be assigned, but every value is checked first, both in the constructor and in the setter, and a rejected value leaves the activity unchanged.
- **Prices:** a price is a `Decimal` with exactly two decimals. `parse_price` accepts a `Decimal`, an `int` or a text such as `"25.90"` and rejects floats, negative amounts and more than two decimals. Prices are saved as text, and `price_from_json` also reads the numbers written by older files.
- **Guide status:** `guide_profile` is `None` until the user becomes a guide.
- **Storage:** each user is saved in its own file, `data/users/<user_id>.json`. A user ID is checked before it is used as a file name.
- **Exceptions:** each family shares a base class, so related errors can be caught together (`ActivityError`, `PointsError`, `ParticipantError`, `UserStorageError`).