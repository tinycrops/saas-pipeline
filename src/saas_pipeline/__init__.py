"""
SaaS Pipeline

A modular toolkit for building, growing, and scaling a SaaS business from $0 to $100k/month with AI, niche focus, and affiliate-driven growth.
"""

__version__ = "0.1.0"
__author__ = "SaaS Pipeline Team"
__email__ = "team@saaspipeline.dev"

# Import commonly used modules for easier access
from saas_pipeline.config import load_config, get_config
from saas_pipeline.utils.logging import setup_logging

# Initialize logging when the package is imported
setup_logging() 