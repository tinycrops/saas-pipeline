"""Tests for the configuration module."""

import os
from unittest.mock import patch

import pytest
import yaml

from saas_pipeline.config import load_config, get_config

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "test-model",
        "OPENAI_TEMPERATURE": "0.5",
        "OPENAI_MAX_TOKENS": "1000",
        "LOG_LEVEL": "DEBUG",
        "CACHE_ENABLED": "false",
        "CACHE_TTL": "1800",
        "DEBUG": "true",
        "TESTING": "true",
        "RATE_LIMIT_ENABLED": "false",
        "RATE_LIMIT_REQUESTS": "30",
        "RATE_LIMIT_PERIOD": "30",
    }):
        yield

def test_load_config_from_env(mock_env_vars):
    """Test loading configuration from environment variables."""
    config = load_config()
    
    assert config["openai"]["api_key"] == "test-key"
    assert config["openai"]["model"] == "test-model"
    assert config["openai"]["temperature"] == 0.5
    assert config["openai"]["max_tokens"] == 1000
    
    assert config["app"]["log_level"] == "DEBUG"
    assert config["app"]["cache_enabled"] is False
    assert config["app"]["cache_ttl"] == 1800
    assert config["app"]["debug"] is True
    assert config["app"]["testing"] is True
    
    assert config["rate_limit"]["enabled"] is False
    assert config["rate_limit"]["requests"] == 30
    assert config["rate_limit"]["period"] == 30

def test_load_config_from_yaml(mock_env_vars, tmp_path):
    """Test loading configuration from YAML file."""
    # Create test YAML file
    yaml_config = {
        "openai": {
            "model": "yaml-model",
            "temperature": 0.3,
        },
        "app": {
            "log_level": "WARNING",
        }
    }
    
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(yaml_config, f)
    
    # Load config with YAML file
    config = load_config(str(config_file))
    
    # YAML values should override env vars
    assert config["openai"]["model"] == "yaml-model"
    assert config["openai"]["temperature"] == 0.3
    assert config["app"]["log_level"] == "WARNING"
    
    # Other values should remain from env vars
    assert config["openai"]["api_key"] == "test-key"
    assert config["openai"]["max_tokens"] == 1000

def test_get_config_loads_if_empty():
    """Test that get_config loads configuration if not already loaded."""
    with patch("saas_pipeline.config.load_config") as mock_load:
        mock_load.return_value = {"test": "config"}
        config = get_config()
        assert config == {"test": "config"}
        mock_load.assert_called_once()

def test_missing_api_key():
    """Test that missing API key raises error."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            load_config() 