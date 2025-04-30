"""
Custom exceptions for the OpenAI API client.

This module defines a hierarchy of custom exceptions for handling
various error scenarios when interacting with the OpenAI API.
"""

from typing import Optional, Dict, Any, Union


class APIError(Exception):
    """Base exception class for all API-related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)
    
    def __str__(self) -> str:
        error_msg = self.message
        if self.status_code:
            error_msg = f"[{self.status_code}] {error_msg}"
        return error_msg


class AuthenticationError(APIError):
    """Raised when there is an authentication issue with the API key."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = 429,
        response: Optional[Dict[str, Any]] = None,
        retry_after: Optional[Union[int, str]] = None
    ):
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class InvalidRequestError(APIError):
    """Raised when the request contains invalid parameters."""
    pass


class ServiceUnavailableError(APIError):
    """Raised when the OpenAI service is unavailable."""
    pass


class TimeoutError(APIError):
    """Raised when a request times out."""
    pass


def handle_api_error(status_code: int, response_data: Dict[str, Any]) -> APIError:
    """
    Factory function to create the appropriate exception based on the error response.
    
    Args:
        status_code: HTTP status code
        response_data: Error response data from the API
        
    Returns:
        An appropriate APIError subclass instance
    """
    error_message = response_data.get('error', {}).get('message', 'Unknown API error')
    
    if status_code == 401:
        return AuthenticationError(error_message, status_code, response_data)
    elif status_code == 429:
        retry_after = response_data.get('error', {}).get('retry_after')
        return RateLimitError(error_message, status_code, response_data, retry_after)
    elif status_code == 400:
        return InvalidRequestError(error_message, status_code, response_data)
    elif status_code in (500, 502, 503):
        return ServiceUnavailableError(error_message, status_code, response_data)
    else:
        return APIError(error_message, status_code, response_data) 