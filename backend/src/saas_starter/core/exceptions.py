"""Custom application exceptions."""


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)


class TenantNotFoundError(AppError):
    """Raised when a tenant cannot be found."""

    pass


class UserNotFoundError(AppError):
    """Raised when a user cannot be found."""

    pass


class UnauthorizedError(AppError):
    """Raised when authentication or authorization fails."""

    pass


class PlanLimitExceededError(AppError):
    """Raised when a tenant exceeds their plan limits."""

    pass


class StripeError(AppError):
    """Raised when a Stripe API call fails."""

    pass
