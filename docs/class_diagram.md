# Class Diagram

Current domain model of Travel&Go. GitHub renders the diagram below automatically.

```mermaid
classDiagram
    class Activity {
        -events_count : int$
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

    class InvalidTypeError {
        +type : str
    }

    Activity <|-- GuideTour
    Activity <|-- Pubcrawl
    Trip o-- "many" Activity : activities
    InvalidTypeError --|> Exception
```

## Notes

- **Inheritance:** `GuideTour` and `Pubcrawl` extend `Activity`.
- **Aggregation:** a `Trip` holds references to `Activity` objects that exist independently of it.
- **Static and class members** are marked with `$`.
- `InvalidTypeError` is raised when a saved activity has an unknown `type` field while loading from JSON.
