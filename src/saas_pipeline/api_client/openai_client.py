"""
OpenAI API Client

Main implementation class for interacting with the OpenAI API.
Provides methods for different API endpoints with retry logic,
error handling, and response parsing.
"""

import time
import logging
import random
from typing import Dict, Any, List, Optional, Union, Callable

import openai
from openai import OpenAI as OpenAISDK

from ..config import get_openai_api_key, get_config_value, load_config
from .exceptions import APIError, handle_api_error, TimeoutError
from .response import (
    APIResponse,
    CompletionResponse,
    ChatCompletionResponse,
    validate_response
)


logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client for interacting with the OpenAI API.
    
    This class provides methods for making various types of API calls to OpenAI,
    with built-in error handling, retry logic, and response parsing.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: Optional API key. If not provided, will be loaded from environment.
        """
        # Make sure configuration is loaded
        if get_config_value('openai') is None:
            load_config()
            
        # Set API key (from parameter or environment)
        self.api_key = api_key or get_openai_api_key()
        
        # Create the OpenAI client instance
        self.client = OpenAISDK(api_key=self.api_key)
        
        # Default configuration
        self.default_model = get_config_value('openai.model', 'gpt-4o')
        self.default_temperature = get_config_value('openai.temperature', 0.7)
        self.default_max_tokens = get_config_value('openai.max_tokens', 4000)
        self.timeout = get_config_value('openai.timeout', 60)
        
        # Retry configuration
        self.max_retries = 3
        self.initial_backoff = 1  # seconds
        
        logger.debug(f"Initialized OpenAI client with model {self.default_model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion API call.
        
        Args:
            messages: List of message dictionaries (role, content)
            model: Model to use (defaults to configuration)
            temperature: Sampling temperature (defaults to configuration)
            max_tokens: Maximum number of tokens (defaults to configuration)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            ChatCompletionResponse with the API response data
            
        Raises:
            APIError: If the API request fails after retries
        """
        params = {
            'model': model or self.default_model,
            'messages': messages,
            'temperature': temperature or self.default_temperature,
            'max_tokens': max_tokens or self.default_max_tokens,
            **kwargs
        }
        
        logger.debug(f"Making chat completion request with model {params['model']}")
        
        # Wrap the API call with retry logic
        def api_call():
            response = self.client.chat.completions.create(**params)
            # Convert the response object to a dictionary
            return response.model_dump()
        
        raw_response = self._with_retry(api_call)
        
        # Validate and parse response
        if not validate_response(raw_response):
            raise APIError("Invalid response format from OpenAI API")
        
        return ChatCompletionResponse.from_raw_response(raw_response)
    
    def completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResponse:
        """
        Make a text completion API call.
        
        Args:
            prompt: Text prompt for completion
            model: Model to use (defaults to configuration)
            temperature: Sampling temperature (defaults to configuration)
            max_tokens: Maximum number of tokens (defaults to configuration)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            CompletionResponse with the API response data
            
        Raises:
            APIError: If the API request fails after retries
        """
        params = {
            'model': model or self.default_model,
            'prompt': prompt,
            'temperature': temperature or self.default_temperature,
            'max_tokens': max_tokens or self.default_max_tokens,
            **kwargs
        }
        
        logger.debug(f"Making completion request with model {params['model']}")
        
        # Wrap the API call with retry logic
        def api_call():
            response = self.client.completions.create(**params)
            # Convert the response object to a dictionary
            return response.model_dump()
        
        raw_response = self._with_retry(api_call)
        
        # Validate and parse response
        if not validate_response(raw_response):
            raise APIError("Invalid response format from OpenAI API")
        
        return CompletionResponse.from_raw_response(raw_response)
    
    def _with_retry(self, api_call: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute an API call with exponential backoff retry logic.
        
        Args:
            api_call: Function that makes the actual API call
            
        Returns:
            API response data
            
        Raises:
            APIError: If all retries fail
        """
        last_error = None
        backoff = self.initial_backoff
        
        for attempt in range(self.max_retries):
            try:
                # Set a timeout for the API call
                start_time = time.time()
                response = api_call()
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"Request timed out after {self.timeout} seconds")
                    
                return response
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit exceeded (attempt {attempt+1}/{self.max_retries})")
                last_error = e
                # Use retry-after from response if available, otherwise use exponential backoff
                retry_after = getattr(e, 'retry_after', None)
                if retry_after:
                    sleep_time = float(retry_after)
                else:
                    sleep_time = backoff
                
            except (openai.APIError, openai.APIConnectionError) as e:
                logger.warning(f"API error: {str(e)} (attempt {attempt+1}/{self.max_retries})")
                last_error = e
                sleep_time = backoff
                
            except Exception as e:
                logger.warning(f"Unexpected error: {str(e)} (attempt {attempt+1}/{self.max_retries})")
                last_error = e
                sleep_time = backoff
            
            # If this was the last attempt, don't sleep, just raise the error
            if attempt == self.max_retries - 1:
                break
                
            # Add jitter to avoid thundering herd problem
            jitter = random.uniform(0, 0.1 * backoff)
            sleep_time += jitter
            
            logger.debug(f"Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
            
            # Exponential backoff
            backoff *= 2
        
        # If we get here, all retries have failed
        error_message = f"API request failed after {self.max_retries} attempts"
        if last_error:
            error_message += f": {str(last_error)}"
            
        logger.error(error_message)
        
        if isinstance(last_error, openai.APIError):
            # Convert OpenAI SDK error to our custom error
            raise handle_api_error(getattr(last_error, 'status_code', 500), {'error': {'message': str(last_error)}})
        else:
            raise APIError(error_message) 