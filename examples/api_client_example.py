#!/usr/bin/env python3
"""
Example script demonstrating how to use the OpenAI API client.

This script shows basic usage patterns for making API calls,
handling responses, and dealing with errors.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import argparse

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.saas_pipeline.api_client import OpenAIClient, APIError
from src.saas_pipeline.config import load_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='OpenAI API Client Example')
    parser.add_argument(
        '--prompt',
        default='Write a short poem about artificial intelligence.',
        help='Prompt text for the API call'
    )
    parser.add_argument(
        '--model',
        default=None,
        help='Model to use (defaults to configuration)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    return parser.parse_args()


def chat_completion_example(client, prompt, model=None):
    """Run a chat completion example."""
    logger.info("Running chat completion example...")
    
    messages = [
        {"role": "system", "content": "You are a helpful, creative assistant."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        # Make the API call
        response = client.chat_completion(messages, model=model)
        
        # Display the response
        logger.info("=== Chat Completion Response ===")
        logger.info(f"Content: {response.content}")
        logger.info(f"Model: {response.model}")
        logger.info(f"Tokens used: {response.total_tokens}")
        
        return response.content
    
    except APIError as e:
        logger.error(f"API Error: {e}")
        return None


def completion_example(client, prompt, model=None):
    """Run a text completion example."""
    logger.info("Running text completion example...")
    
    try:
        # Make the API call
        response = client.completion(prompt, model=model)
        
        # Display the response
        logger.info("=== Text Completion Response ===")
        logger.info(f"Text: {response.data}")
        logger.info(f"Model: {response.model}")
        logger.info(f"Tokens used: {response.total_tokens}")
        
        return response.data
    
    except APIError as e:
        logger.error(f"API Error: {e}")
        return None


def main():
    """Main function for the example script."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command-line arguments
    args = setup_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config()
    logger.debug(f"Using OpenAI model: {config.openai.model}")
    
    # Create the API client
    client = OpenAIClient()
    
    # Run examples
    logger.info(f"Using prompt: {args.prompt}")
    chat_response = chat_completion_example(client, args.prompt, args.model)
    
    # Only run completion example if chat completion worked
    if chat_response:
        completion_example(client, args.prompt, args.model)


if __name__ == "__main__":
    main() 