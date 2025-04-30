"""
Tests for the OpenAI API client module.

These tests verify that the OpenAI API client works correctly,
using mocked API responses to avoid actual API calls.
"""

import unittest
from unittest.mock import patch, MagicMock
import json

from src.saas_pipeline.api_client import (
    OpenAIClient,
    APIError,
    AuthenticationError,
    RateLimitError
)


class TestOpenAIClient(unittest.TestCase):
    """Test cases for the OpenAIClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the load_config and get_config_value functions
        self.config_patcher = patch('src.saas_pipeline.api_client.openai_client.get_config_value')
        self.mock_get_config = self.config_patcher.start()
        self.mock_get_config.return_value = 'gpt-4o'
        
        # Mock the get_openai_api_key function
        self.api_key_patcher = patch('src.saas_pipeline.api_client.openai_client.get_openai_api_key')
        self.mock_get_api_key = self.api_key_patcher.start()
        self.mock_get_api_key.return_value = 'test_api_key'
        
        # Mock the OpenAI SDK client
        self.openai_sdk_patcher = patch('src.saas_pipeline.api_client.openai_client.OpenAISDK')
        self.mock_openai_sdk = self.openai_sdk_patcher.start()
        
        # Create a mock client instance
        self.mock_sdk_instance = MagicMock()
        self.mock_openai_sdk.return_value = self.mock_sdk_instance
        
        # Create the client under test
        self.client = OpenAIClient()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.config_patcher.stop()
        self.api_key_patcher.stop()
        self.openai_sdk_patcher.stop()
    
    def test_init_sets_api_key(self):
        """Test that the API key is set correctly on initialization."""
        self.assertEqual(self.client.api_key, 'test_api_key')
        self.mock_openai_sdk.assert_called_once_with(api_key='test_api_key')
    
    def test_chat_completion_success(self):
        """Test successful chat completion API call."""
        # Mock response data
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            'id': 'test-id',
            'object': 'chat.completion',
            'created': 1677858242,
            'model': 'gpt-4o',
            'choices': [
                {
                    'message': {
                        'role': 'assistant',
                        'content': 'This is a test response.'
                    },
                    'finish_reason': 'stop',
                    'index': 0
                }
            ],
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            }
        }
        
        # Set up the mock chat completions API
        self.mock_sdk_instance.chat.completions.create.return_value = mock_response
        
        # Make the API call
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello, how are you?'}
        ]
        response = self.client.chat_completion(messages)
        
        # Verify the response
        self.assertEqual(response.content, 'This is a test response.')
        self.assertEqual(response.model, 'gpt-4o')
        self.assertEqual(response.total_tokens, 30)
        
        # Verify the API was called with the right parameters
        self.mock_sdk_instance.chat.completions.create.assert_called_once()
        call_args = self.mock_sdk_instance.chat.completions.create.call_args[1]
        self.assertEqual(call_args['model'], 'gpt-4o')
        self.assertEqual(call_args['messages'], messages)
    
    def test_completion_success(self):
        """Test successful text completion API call."""
        # Mock response data
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            'id': 'test-id',
            'object': 'text_completion',
            'created': 1677858242,
            'model': 'gpt-4o',
            'choices': [
                {
                    'text': 'This is a test response.',
                    'finish_reason': 'stop',
                    'index': 0
                }
            ],
            'usage': {
                'prompt_tokens': 5,
                'completion_tokens': 10,
                'total_tokens': 15
            }
        }
        
        # Set up the mock completions API
        self.mock_sdk_instance.completions.create.return_value = mock_response
        
        # Make the API call
        prompt = 'This is a test prompt.'
        response = self.client.completion(prompt)
        
        # Verify the response
        self.assertEqual(response.data, 'This is a test response.')
        self.assertEqual(response.model, 'gpt-4o')
        self.assertEqual(response.total_tokens, 15)
        
        # Verify the API was called with the right parameters
        self.mock_sdk_instance.completions.create.assert_called_once()
        call_args = self.mock_sdk_instance.completions.create.call_args[1]
        self.assertEqual(call_args['model'], 'gpt-4o')
        self.assertEqual(call_args['prompt'], prompt)
    
    @patch('src.saas_pipeline.api_client.openai_client.time')
    def test_retry_on_rate_limit(self, mock_time):
        """Test that retries happen on rate limit errors."""
        # Mock time functions
        mock_time.time.return_value = 123
        mock_time.sleep = MagicMock()
        
        # Configure the mock to raise a rate limit error on first call
        rate_limit_error = MagicMock()
        rate_limit_error.__class__ = MagicMock()
        rate_limit_error.__class__.__name__ = 'RateLimitError'
        
        # Set up the mock to raise an error on first call, then succeed
        self.mock_sdk_instance.chat.completions.create.side_effect = [
            MagicMock(side_effect=rate_limit_error),
            MagicMock(model_dump=MagicMock(return_value={
                'choices': [{'message': {'content': 'Success after retry'}}]
            }))
        ]
        
        # Make the API call
        messages = [{'role': 'user', 'content': 'Test message'}]
        response = self.client.chat_completion(messages)
        
        # Verify retry happened
        self.assertEqual(self.mock_sdk_instance.chat.completions.create.call_count, 2)
        mock_time.sleep.assert_called_once()
        
        # Verify response
        self.assertEqual(response.content, 'Success after retry')


if __name__ == '__main__':
    unittest.main() 