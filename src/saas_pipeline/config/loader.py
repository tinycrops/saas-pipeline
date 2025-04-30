"""
Configuration Loader

Functions for loading, validating, and accessing configuration settings
from environment variables and configuration files.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .schema import ConfigSchema

logger = logging.getLogger(__name__)

# Global configuration instance
_config: Optional[ConfigSchema] = None


def load_config(config_path: Optional[str] = None) -> ConfigSchema:
    """
    Load configuration from environment variables and optional config file.
    
    Args:
        config_path: Optional path to a JSON configuration file
        
    Returns:
        ConfigSchema instance with loaded configuration
    """
    global _config
    
    # Start with default empty config
    config_dict: Dict[str, Any] = {}
    
    # Load from config file if provided
    if config_path:
        config_file = Path(config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_dict = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
            except (json.JSONDecodeError, PermissionError) as e:
                logger.error(f"Error loading config file: {e}")
    
    # Override with environment variables
    env_config = _load_from_env()
    _deep_update(config_dict, env_config)
    
    # Create and store config instance
    _config = ConfigSchema.from_dict(config_dict)
    return _config


def get_openai_api_key() -> str:
    """
    Get the OpenAI API key from environment variable.
    
    Returns:
        OpenAI API key as string
        
    Raises:
        ValueError: If API key is not set
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
    return api_key


def get_config_value(path: str, default: Any = None) -> Any:
    """
    Access a configuration value using dot notation.
    
    Args:
        path: Dot-separated path to the configuration value (e.g., 'openai.model')
        default: Default value to return if the path doesn't exist
        
    Returns:
        Configuration value or default
        
    Raises:
        ValueError: If configuration hasn't been loaded yet
    """
    if _config is None:
        raise ValueError("Configuration not loaded. Call load_config() first.")
    
    current = _config
    for part in path.split('.'):
        if hasattr(current, part):
            current = getattr(current, part)
        else:
            return default
    
    return current


def _load_from_env() -> Dict[str, Any]:
    """
    Load configuration values from environment variables.
    
    Returns:
        Dictionary with configuration from environment variables
    """
    config: Dict[str, Any] = {
        'openai': {
            'model': os.environ.get('OPENAI_MODEL', 'gpt-4o'),
            'temperature': float(os.environ.get('OPENAI_TEMPERATURE', '0.7')),
            'max_tokens': int(os.environ.get('OPENAI_MAX_TOKENS', '4000')),
        }
    }
    
    # Add other environment-based configuration here
    if 'DEBUG' in os.environ:
        config['debug'] = os.environ.get('DEBUG', '').lower() in ('true', '1', 'yes')
    
    if 'LOGGING_LEVEL' in os.environ:
        config['logging_level'] = os.environ.get('LOGGING_LEVEL', 'INFO')
    
    if 'APP_NAME' in os.environ:
        config['app_name'] = os.environ.get('APP_NAME', 'SaaS Pipeline')
    
    return config


def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep update a nested dictionary with values from another dictionary.
    
    Args:
        target: Target dictionary to update
        source: Source dictionary with values to apply
        
    Returns:
        Updated target dictionary
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
    
    return target 