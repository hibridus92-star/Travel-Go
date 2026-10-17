# Class Diagram

Current domain model of Travel&Go. GitHub renders the diagram below automatically.

```mermaid
classDiagram
    class Activity {
        +events_count : int$
        +name : str
        +location : str
        +price : float
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

    class Trip {
        +id_number : int
        +destination : str
        +activities : list~Activity~
        +event_total_cost() float
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
        #_travel_points : int
        +guide_profile : object
        +trips : list~Trip~
        +age : int
        +travel_points : int
        +earn_points(amount: int)
        +redeem_points(amount: int)
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

    Activity <|-- GuideTour
    Activity <|-- Pubcrawl
    Trip o-- "many" Activity : activities
    User o-- "many" Trip : trips
    InvalidTypeError --|> Exception
    PointsError --|> Exception
    InvalidPointsAmountError --|> PointsError
    InsufficientPointsError --|> PointsError
```

## Notes

- **Inheritance:** `GuideTour` and `Pubcrawl` extend `Activity`.
- **Aggregation:** a `Trip` holds references to `Activity` objects that exist independently of it, and a `User` holds references to its `Trip` objects. Both relations are one-directional: `Trip` does not know its user, and `Activity` does not know its trip.
- **Static and class members** are marked with `$`.
- **Read-only properties:** `User.age` is computed from `birth_date`, and `User.travel_points` can only change through `earn_points` and `redeem_points`, which validate every amount.
- **Guide status:** `guide_profile` is `None` until the user becomes a guide.
- **Exceptions:** `InvalidTypeError` is raised when a saved activity has an unknown `type` field while loading from JSON. `InvalidPointsAmountError` and `InsufficientPointsError` share the base class `PointsError`, so both can be caught together.
