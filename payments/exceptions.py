"""
Custom exceptions for the payments application.

This module defines specific exceptions that can be raised during
payment processing operations to provide clear error handling.
"""


class PaymentError(Exception):
    """Base exception for all payment-related errors."""
    pass


class StripeConfigurationError(PaymentError):
    """Raised when Stripe is not properly configured."""
    pass


class PaymentIntentError(PaymentError):
    """Raised when there's an issue with creating or processing a PaymentIntent."""
    pass


class RefundError(PaymentError):
    """Raised when there's an issue processing a refund."""
    pass


class WebhookError(PaymentError):
    """Raised when there's an issue processing a webhook."""
    pass


class InsufficientFundsError(PaymentError):
    """Raised when a payment is declined due to insufficient funds."""
    pass


class CardDeclinedError(PaymentError):
    """Raised when a payment is declined by the card issuer."""
    pass


class AuthenticationError(PaymentError):
    """Raised when authentication with Stripe fails."""
    pass


class ConnectionTokenError(PaymentError):
    """Raised when there's an issue creating or using a connection token."""
    pass


class TerminalError(PaymentError):
    """Raised when there's an issue with Terminal operations."""
    pass


class RefundAuthorizationError(PaymentError):
    """Raised when a refund requires additional authorization."""
    pass


class DuplicatePaymentError(PaymentError):
    """Raised when attempting to process a duplicate payment."""
    pass


class PaymentAmountError(PaymentError):
    """Raised when there's an issue with payment amounts (negative, too large, etc.)."""
    pass


class CurrencyError(PaymentError):
    """Raised when there's an issue with currency handling."""
    pass
