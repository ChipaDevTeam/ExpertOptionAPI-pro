"""Custom exceptions for the ExpertOption API."""

class ExpertOptionError(Exception):
    """Base exception for ExpertOption API errors."""
    pass

class ConnectionError(ExpertOptionError):
    """Raised when WebSocket connection fails."""
    pass

class AuthenticationError(ExpertOptionError):
    """Raised when authentication with the server fails."""
    pass

class InvalidAssetError(ExpertOptionError):
    """Raised when an invalid or inactive asset is used."""
    pass

class InvalidExpirationTimeError(ExpertOptionError):
    """Raised when an invalid expiration time is provided."""
    pass

class OrderPlacementError(ExpertOptionError):
    """Raised when order placement fails."""
    pass

class DataFetchError(ExpertOptionError):
    """Raised when fetching data (e.g., candles, profile) fails."""
    pass