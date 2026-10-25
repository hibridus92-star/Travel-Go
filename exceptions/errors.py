"""Custom exceptions for Travel&Go."""


class InvalidTypeError(Exception):
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
        super().__init__(
            f"Points amount must be positive, got {amount}."
        )

class InsufficientPointsError(PointsError):
        """Raised when the requested points exceed the available balance."""
        def __init__(self, amount: int, balance: int) -> None:
            self.amount: int = amount
            self.balance: int = balance
            super().__init__(
                f"Cannot redeem {amount} points: "
                f"only {balance} points available."
            )

class InvalidTravelPointsBalanceError(Exception):
    """Raised when a saved travel points balance is negative."""

    def __init__(self, balance: int) -> None:
        self.balance: int = balance
        super().__init__(
            f"Travel points balance cannot be negative, got {balance}."
        )

class ParticipantError(Exception):
    """Base exception for trip participant errors."""


class DuplicateParticipantError(ParticipantError):
    """Raised when a user is already a participant in the trip."""

    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        super().__init__(
            f"User {user_id} is already a participant in this trip."
        )


class ParticipantNotFoundError(ParticipantError):
    """Raised when a user is not a participant in the trip."""

    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        super().__init__(
            f"User {user_id} is not a participant in this trip."
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
            f"Invalid user ID {user_id!r}: only letters, digits, '-' and '_' are allowed.")

