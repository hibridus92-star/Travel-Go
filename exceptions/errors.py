"""Custom exceptions for Travel&Go."""


class InvalidTypeError(Exception):
    """Raised when a saved activity has an unknown 'type' field."""

    def __init__(self, activity_type: str, message: str = "Unknown activity type") -> None:
        self.type: str = activity_type
        super().__init__(f"{message}: {activity_type}")
