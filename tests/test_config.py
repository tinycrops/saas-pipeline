"""
Tests for the configuration module.
"""

import os
import unittest
from pathlib import Path
import json

from src.saas_pipeline.config import (
    load_config,
    get_config_value,
    get_openai_api_key
)


class TestConfig(unittest.TestCase):
    """Test cases for the configuration module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary test config file
        self.test_config_path = 'test_config.json'
        self.test_config = {
            'app_name': 'Test App',
            'openai': {
                'model': 'test-model',
                'temperature': 0.5
            }
        }
        
        with open(self.test_config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        # Save original environment
        self.original_env = os.environ.copy()
        
        # Set test environment variables
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        os.environ['OPENAI_MODEL'] = 'env-model'
        os.environ['DEBUG'] = 'true'
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test config file
        if Path(self.test_config_path).exists():
            Path(self.test_config_path).unlink()
        
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_load_config_from_file(self):
        """Test loading configuration from a file."""
        config = load_config(self.test_config_path)
        
        # File values should be loaded
        self.assertEqual(config.app_name, 'Test App')
        
        # But environment variables should override file values
        self.assertEqual(config.openai.model, 'env-model')
        self.assertEqual(config.debug, True)
    
    def test_get_config_value(self):
        """Test accessing configuration values."""
        load_config(self.test_config_path)
        
        # Test accessing values with dot notation
        self.assertEqual(get_config_value('app_name'), 'Test App')
        self.assertEqual(get_config_value('openai.model'), 'env-model')
        
        # Since we didn't set OPENAI_TEMPERATURE in the environment,
        # the default in the config file should be used
        self.assertEqual(get_config_value('openai.temperature'), 0.7)
        
        # Test default values for non-existent paths
        self.assertEqual(get_config_value('non_existent', 'default'), 'default')
    
    def test_get_openai_api_key(self):
        """Test getting the OpenAI API key."""
        api_key = get_openai_api_key()
        self.assertEqual(api_key, 'test-api-key')
    
    def test_get_openai_api_key_missing(self):
        """Test error when API key is missing."""
        # Remove API key from environment
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Getting the API key should raise an error
        with self.assertRaises(ValueError):
            get_openai_api_key()


if __name__ == '__main__':
    unittest.main() 