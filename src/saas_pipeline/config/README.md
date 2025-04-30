# Configuration Module

This module provides functionality for loading, validating, and accessing configuration settings for the SaaS Pipeline application, with a focus on secure API key management for OpenAI integration.

## Usage

```python
from saas_pipeline.config import load_config, get_config_value, get_openai_api_key

# Load configuration (from environment variables and optional config file)
config = load_config('path/to/config.json')  # Path is optional

# Access configuration values
model = get_config_value('openai.model')  # Returns the OpenAI model name
temperature = get_config_value('openai.temperature')  # Returns the temperature value
non_existent = get_config_value('non.existent.path', 'default')  # Returns 'default'

# Get OpenAI API key (from OPENAI_API_KEY environment variable)
api_key = get_openai_api_key()
```

## Configuration Structure

The configuration is structured as a hierarchical schema with the following sections:

- `openai`: OpenAI API settings (model, temperature, max_tokens, etc.)
- `app_name`: Application name
- `debug`: Debug mode flag
- `logging_level`: Logging level (INFO, DEBUG, etc.)

## Configuration Sources

Configuration values are loaded from multiple sources in the following priority order (higher overrides lower):

1. Environment variables (highest priority)
2. Configuration file (if provided)
3. Default values (lowest priority)

## Environment Variables

The following environment variables are recognized:

- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model name (default: "gpt-4o")
- `OPENAI_TEMPERATURE`: Temperature for API requests (default: 0.7)
- `OPENAI_MAX_TOKENS`: Maximum tokens for API responses (default: 4000)
- `DEBUG`: Debug mode flag (default: false)
- `LOGGING_LEVEL`: Logging level (default: "INFO")
- `APP_NAME`: Application name (default: "SaaS Pipeline")

## Configuration File

The configuration file should be a JSON file with the following structure:

```json
{
    "app_name": "SaaS Pipeline",
    "debug": false,
    "logging_level": "INFO",
    "openai": {
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 4000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "timeout": 60
    }
}
``` 