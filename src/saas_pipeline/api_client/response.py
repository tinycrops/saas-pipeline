"""
Response handling utilities for the OpenAI API client.

This module provides classes and functions for parsing, validating
and extracting data from API responses.
"""

from typing import Dict, Any, List, Optional, TypeVar, Generic, Union


T = TypeVar('T')


class APIResponse(Generic[T]):
    """
    Wrapper class for API responses that provides convenient access to response data.
    
    Generic type T represents the expected response data type.
    """
    
    def __init__(
        self, 
        raw_response: Dict[str, Any],
        data: T,
        model: Optional[str] = None,
        usage: Optional[Dict[str, int]] = None
    ):
        self.raw_response = raw_response
        self.data = data
        self.model = model or raw_response.get('model')
        self.usage = usage or raw_response.get('usage', {})
    
    @property
    def prompt_tokens(self) -> int:
        """Get the number of tokens used in the prompt."""
        return self.usage.get('prompt_tokens', 0)
    
    @property
    def completion_tokens(self) -> int:
        """Get the number of tokens used in the completion."""
        return self.usage.get('completion_tokens', 0)
    
    @property
    def total_tokens(self) -> int:
        """Get the total number of tokens used."""
        return self.usage.get('total_tokens', 0)


class CompletionResponse(APIResponse[str]):
    """Response wrapper for text completion API calls."""
    
    @classmethod
    def from_raw_response(cls, response: Dict[str, Any]) -> 'CompletionResponse':
        """
        Create a CompletionResponse from a raw API response.
        
        Args:
            response: Raw API response dictionary
            
        Returns:
            CompletionResponse instance
        """
        # Extract the completion text from the response
        if 'choices' not in response or not response['choices']:
            raise ValueError("Invalid completion response: missing choices")
        
        # Get the text from the first choice
        text = response['choices'][0].get('text', '')
        return cls(response, text)


class ChatCompletionResponse(APIResponse[List[Dict[str, Any]]]):
    """Response wrapper for chat completion API calls."""
    
    @classmethod
    def from_raw_response(cls, response: Dict[str, Any]) -> 'ChatCompletionResponse':
        """
        Create a ChatCompletionResponse from a raw API response.
        
        Args:
            response: Raw API response dictionary
            
        Returns:
            ChatCompletionResponse instance
        """
        # Validate the response format
        if 'choices' not in response or not response['choices']:
            raise ValueError("Invalid chat completion response: missing choices")
        
        # Extract messages from choices
        messages = []
        for choice in response['choices']:
            if 'message' in choice:
                messages.append(choice['message'])
                
        return cls(response, messages)
    
    @property
    def message(self) -> Dict[str, Any]:
        """Get the first message (most common use case)."""
        if not self.data:
            return {}
        return self.data[0]
    
    @property
    def content(self) -> str:
        """Get the content of the first message."""
        return self.message.get('content', '')


def validate_response(response: Dict[str, Any]) -> bool:
    """
    Validate that a response has the expected structure.
    
    Args:
        response: Response data to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check for minimal required fields
    if not isinstance(response, dict):
        return False
    
    if 'choices' not in response or not isinstance(response['choices'], list):
        return False
    
    # At least one choice should be present
    if not response['choices']:
        return False
    
    return True 