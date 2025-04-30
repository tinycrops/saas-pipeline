"""Configuration management for SaaS Pipeline."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global configuration dictionary
_config: Dict[str, Any] = {}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from environment variables and YAML file.
    
    Args:
        config_path: Optional path to a YAML configuration file.
        
    Returns:
        Dict containing merged configuration from all sources.
    """
    global _config
    
    # Start with environment variables
    config = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
        },
        "app": {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "cache_enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
            "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "testing": os.getenv("TESTING", "false").lower() == "true",
        },
        "rate_limit": {
            "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            "requests": int(os.getenv("RATE_LIMIT_REQUESTS", "60")),
            "period": int(os.getenv("RATE_LIMIT_PERIOD", "60")),
        },
    }
    
    # Load YAML configuration if provided
    if config_path:
        yaml_path = Path(config_path)
        if yaml_path.exists():
            with open(yaml_path) as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    _deep_update(config, yaml_config)
    
    # Validate required configuration
    _validate_config(config)
    
    # Update global configuration
    _config = config
    
    return config

def get_config() -> Dict[str, Any]:
    """Get the current configuration.
    
    Returns:
        Dict containing the current configuration.
    """
    if not _config:
        return load_config()
    return _config

def _deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """Recursively update a dictionary with another dictionary.
    
    Args:
        base_dict: The dictionary to update.
        update_dict: The dictionary containing updates.
    """
    for key, value in update_dict.items():
        if (
            key in base_dict 
            and isinstance(base_dict[key], dict) 
            and isinstance(value, dict)
        ):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value

def _validate_config(config: Dict[str, Any]) -> None:
    """Validate the configuration.
    
    Args:
        config: The configuration dictionary to validate.
        
    Raises:
        ValueError: If required configuration is missing.
    """
    if not config["openai"]["api_key"]:
        raise ValueError(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
        ) 