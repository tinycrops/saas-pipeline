"""
OpenAI API Client Module

This module provides utility functions for interacting with the OpenAI API,
including making API calls, handling responses, and managing errors.
"""

from .openai_client import OpenAIClient
from .exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    ServiceUnavailableError
)
from .response import APIResponse

__all__ = [
    'OpenAIClient',
    'APIResponse',
    'APIError',
    'AuthenticationError',
    'RateLimitError',
    'InvalidRequestError',
    'ServiceUnavailableError'
] 