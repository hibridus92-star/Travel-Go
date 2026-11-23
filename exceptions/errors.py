"""Custom exceptions for Travel&Go."""

from datetime import date, datetime


class ActivityError(Exception):
    """Base exception for invalid activity data."""


class InvalidActivityNameError(ActivityError):
    """Raised when an activity name is not text, is empty or has only spaces."""

    def __init__(self, name: object) -> None:
        self.name: object = name
        super().__init__(f"Activity name must be a non-empty text, got {name!r}.")


class InvalidPriceError(ActivityError):
    """Raised when a price is not a non-negative amount with at most two decimals."""

    def __init__(self, price: object, reason: str) -> None:
        self.price: object = price
        self.reason: str = reason
        super().__init__(f"Invalid price {price!r}: {reason}.")


class InvalidStartTimeError(ActivityError):
    """Raised when an activity start is not a datetime without a time zone."""

    def __init__(self, starts_at: object, reason: str) -> None:
        self.starts_at: object = starts_at
        self.reason: str = reason
        super().__init__(f"Invalid start {starts_at}: {reason}.")


class InvalidTypeError(ActivityError):
    """Raised when a saved activity has an unknown 'type' field."""

    def __init__(self, activity_type: str, message: str = "Unknown activity type") -> None:
        self.type: str = activity_type
        super().__init__(f"{message}: {activity_type}")


class PointsError(Exception):
    """Base exception for travel points errors."""


class InvalidPointsAmountError(PointsError):
    """Raised when the points amount is zero or negative."""

    def __init__(self, amount: int) -> None:
        self.amount: int = amount
        super().__init__(f"Points amount must be positive, got {amount}.")


class InsufficientPointsError(PointsError):
    """Raised when the requested points exceed the available balance."""

    def __init__(self, amount: int, balance: int) -> None:
        self.amount: int = amount
        self.balance: int = balance
        super().__init__(f"Cannot redeem {amount} points: only {balance} points available.")


class ParticipantError(Exception):
    """Base exception for trip participant errors."""


class DuplicateParticipantError(ParticipantError):
    """Raised when a user is already a participant in the trip."""

    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        super().__init__(f"User {user_id} is already a participant in this trip.")


class ParticipantNotFoundError(ParticipantError):
    """Raised when a user is not a participant in the trip."""

    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        super().__init__(f"User {user_id} is not a participant in this trip.")


class InvalidTravelPointsBalanceError(Exception):
    """Raised when a saved travel points balance is negative."""

    def __init__(self, balance: int) -> None:
        self.balance: int = balance
        super().__init__(
            f"Travel points balance cannot be negative, got {balance}."
        )


class UserStorageError(Exception):
    """Base exception for errors when saving or loading users."""


class UserNotFoundError(UserStorageError):
    """Raised when there is no saved user with the requested ID."""

    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        super().__init__(f"No saved user with ID {user_id!r}.")


class InvalidUserIdError(UserStorageError):
    """Raised when a user ID cannot be safely used as a file name."""

    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        super().__init__(
            f"Invalid user ID {user_id!r}: only letters, digits, '-' and '_' are allowed."
        )


class TripError(Exception):
    """Base exception for invalid trip data and invalid trip operations."""


class InvalidTripDatesError(TripError):
    """Raised when the start and end dates of a trip are not usable."""

    def __init__(self, start_date: object, end_date: object, reason: str) -> None:
        self.start_date: object = start_date
        self.end_date: object = end_date
        self.reason: str = reason
        super().__init__(f"Invalid trip dates {start_date} to {end_date}: {reason}.")


class ActivityOutsideTripDatesError(TripError):
    """Raised when an activity does not take place between the start and end of the trip."""

    def __init__(self, activity_name: str, starts_at: datetime, start_date: date, end_date: date) -> None:
        self.activity_name: str = activity_name
        self.starts_at: datetime = starts_at
        self.start_date: date = start_date
        self.end_date: date = end_date
        super().__init__(
            f"Activity '{activity_name}' starts on {starts_at:%Y-%m-%d %H:%M}, "
            f"outside the trip dates ({start_date} to {end_date})."
        )


class ActivityNotInTripError(TripError):
    """Raised when removing an activity that is not part of the trip."""

    def __init__(self, activity_name: str) -> None:
        self.activity_name: str = activity_name
        super().__init__(f"Activity '{activity_name}' is not part of this trip.")


class TripLockedError(TripError):
    """Raised when a purchased trip is changed."""

    def __init__(self, trip_id: int, action: str) -> None:
        self.trip_id: int = trip_id
        self.action: str = action
        super().__init__(f"Trip {trip_id} is already purchased and cannot be changed ({action}).")


class InvalidTripFileError(TripError):
    """Raised when a saved trip has a missing or unreadable field."""

    def __init__(self, field: str, reason: str) -> None:
        self.field: str = field
        self.reason: str = reason
        super().__init__(f"Invalid trip file, field '{field}': {reason}.")