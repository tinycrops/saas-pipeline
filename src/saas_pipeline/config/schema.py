"""
Configuration Schema

Defines the structure and validation rules for configuration settings.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class OpenAISettings:
    """OpenAI API configuration settings."""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60  # Request timeout in seconds


@dataclass
class ConfigSchema:
    """Main configuration schema for the application."""
    openai: OpenAISettings = field(default_factory=OpenAISettings)
    app_name: str = "SaaS Pipeline"
    debug: bool = False
    logging_level: str = "INFO"
    
    # Additional configuration sections can be added here
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConfigSchema':
        """
        Create a ConfigSchema instance from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            Populated ConfigSchema instance
        """
        openai_config = config_dict.get('openai', {})
        openai_settings = OpenAISettings(
            model=openai_config.get('model', "gpt-4o"),
            temperature=openai_config.get('temperature', 0.7),
            max_tokens=openai_config.get('max_tokens', 4000),
            top_p=openai_config.get('top_p', 1.0),
            frequency_penalty=openai_config.get('frequency_penalty', 0.0),
            presence_penalty=openai_config.get('presence_penalty', 0.0),
            timeout=openai_config.get('timeout', 60)
        )
        
        return cls(
            openai=openai_settings,
            app_name=config_dict.get('app_name', "SaaS Pipeline"),
            debug=config_dict.get('debug', False),
            logging_level=config_dict.get('logging_level', "INFO")
        ) 