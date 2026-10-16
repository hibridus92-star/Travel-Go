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