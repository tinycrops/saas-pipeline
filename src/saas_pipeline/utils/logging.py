"""Logging configuration for SaaS Pipeline."""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Create console for rich output
console = Console()

def setup_logging(level: Optional[str] = None) -> None:
    """Set up logging configuration with rich formatting.
    
    Args:
        level: Optional log level to override configuration.
    """
    # Get log level from parameter or environment (defaulting to INFO)
    from saas_pipeline.config import get_config
    log_level = level or get_config()["app"]["log_level"]
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure rich handler
    rich_handler = RichHandler(
        console=console,
        show_path=False,
        omit_repeated_times=False,
        rich_tracebacks=True,
    )
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler],
    )
    
    # Create logger
    logger = logging.getLogger("saas_pipeline")
    logger.setLevel(numeric_level)
    
    # Log startup message
    logger.info("Logging initialized at level: %s", log_level)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name.
    
    Args:
        name: The name for the logger.
        
    Returns:
        A configured logger instance.
    """
    return logging.getLogger(f"saas_pipeline.{name}") 