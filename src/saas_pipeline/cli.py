"""
Command-Line Interface (CLI) Entry Point

This module provides the main CLI entry point for the SaaS Pipeline application,
integrating the various modules into a unified command-line interface.
"""

import os
import sys
import argparse
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import application modules
from .config import load_config, get_config_value
from .api_client import OpenAIClient
from .utils import read_json, write_json, ensure_directory

# Import modules for functionality
from .niche import NicheResearchModule
from .prototype import PrototypeBuilderModule
from .affiliate import AffiliateEngineModule
from .feedback import FeedbackModule

def setup_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="SaaS Pipeline - AI-powered SaaS development tools",
        epilog="For more information, visit https://github.com/yourusername/saas-pipeline"
    )
    
    # Global options
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--config', 
        type=str,
        help='Path to configuration file'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Niche Research command
    niche_parser = subparsers.add_parser(
        'niche-research', 
        help='Research a niche and generate market insights'
    )
    niche_parser.add_argument(
        'niche', 
        type=str,
        help='The niche to research (e.g., "email marketing for freelancers")'
    )
    niche_parser.add_argument(
        '--output',
        type=str,
        help='Output file for research results (default: niche_research.json)'
    )
    
    # Prototype Builder command
    prototype_parser = subparsers.add_parser(
        'prototype', 
        help='Design a prototype for your SaaS idea'
    )
    prototype_parser.add_argument(
        'idea', 
        type=str,
        help='Brief description of your SaaS idea'
    )
    prototype_parser.add_argument(
        '--niche-file',
        type=str,
        help='Niche research file to use as input'
    )
    prototype_parser.add_argument(
        '--output',
        type=str,
        help='Output file for prototype design (default: prototype.json)'
    )
    
    # Affiliate Engine command
    affiliate_parser = subparsers.add_parser(
        'affiliate', 
        help='Generate affiliate marketing materials'
    )
    affiliate_parser.add_argument(
        'product', 
        type=str,
        help='Name or path to product definition file'
    )
    affiliate_parser.add_argument(
        '--creators',
        type=str,
        help='Path to list of creators to target'
    )
    affiliate_parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory for generated affiliate materials'
    )
    
    # Feedback Analysis command
    feedback_parser = subparsers.add_parser(
        'feedback', 
        help='Analyze and summarize product feedback'
    )
    feedback_parser.add_argument(
        'feedback_file', 
        type=str,
        help='Path to file containing feedback to analyze'
    )
    feedback_parser.add_argument(
        '--output',
        type=str,
        help='Output file for feedback summary (default: feedback_summary.json)'
    )
    
    return parser

def process_global_args(args: argparse.Namespace) -> None:
    """
    Process global command-line arguments.
    
    Args:
        args: Parsed command-line arguments
    """
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Load configuration file if specified
    if args.config:
        load_config(args.config)
        logger.debug(f"Loaded configuration from {args.config}")
    else:
        load_config()  # Load from default locations

def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI application.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = setup_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Process global arguments
        process_global_args(args)
        
        # Handle command
        if args.command == 'niche-research':
            return handle_niche_research(args)
        elif args.command == 'prototype':
            return handle_prototype(args)
        elif args.command == 'affiliate':
            return handle_affiliate(args)
        elif args.command == 'feedback':
            return handle_feedback(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        if args.debug:
            logger.exception("Exception details:")
        return 1

def handle_niche_research(args: argparse.Namespace) -> int:
    """
    Handle the niche-research command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    logger.info(f"Starting niche research for: {args.niche}")
    
    # Initialize the OpenAI client
    openai_client = OpenAIClient()
    
    # Create niche research module
    niche_module = NicheResearchModule(openai_client)
    
    # Execute niche research
    try:
        results = niche_module.analyze_niche(args.niche)
        
        # Save results to file
        output_file = args.output or "niche_research.json"
        write_json(output_file, results)
        logger.info(f"Niche research saved to {output_file}")
        
        return 0
    except Exception as e:
        logger.error(f"Error in niche research: {str(e)}")
        return 1

def handle_prototype(args: argparse.Namespace) -> int:
    """
    Handle the prototype command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    logger.info(f"Starting prototype design for: {args.idea}")
    
    # Initialize the OpenAI client
    openai_client = OpenAIClient()
    
    # Create prototype module
    prototype_module = PrototypeBuilderModule(openai_client)
    
    # Load niche research if provided
    niche_data = None
    if args.niche_file:
        niche_data = read_json(args.niche_file)
        if not niche_data:
            logger.error(f"Failed to load niche research from {args.niche_file}")
            return 1
    
    # Generate prototype
    try:
        results = prototype_module.design_prototype(args.idea, niche_data=niche_data)
        
        # Save results to file
        output_file = args.output or "prototype.json"
        write_json(output_file, results)
        logger.info(f"Prototype design saved to {output_file}")
        
        return 0
    except Exception as e:
        logger.error(f"Error in prototype design: {str(e)}")
        return 1

def handle_affiliate(args: argparse.Namespace) -> int:
    """
    Handle the affiliate command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    logger.info(f"Starting affiliate material generation for: {args.product}")
    
    # Initialize the OpenAI client
    openai_client = OpenAIClient()
    
    # Create affiliate module
    affiliate_module = AffiliateEngineModule(openai_client)
    
    # Load product data
    product_data = None
    if os.path.isfile(args.product):
        product_data = read_json(args.product)
        if not product_data:
            logger.error(f"Failed to load product data from {args.product}")
            return 1
    
    # Load creator list if provided
    creators = None
    if args.creators:
        creators = read_json(args.creators)
        if not creators:
            logger.error(f"Failed to load creators from {args.creators}")
            return 1
    
    # Generate affiliate materials
    try:
        output_dir = args.output_dir or "affiliate_materials"
        ensure_directory(output_dir)
        
        results = affiliate_module.generate_materials(
            product_name=args.product if not product_data else None,
            product_data=product_data,
            creators=creators
        )
        
        # Save results
        for creator, materials in results.items():
            creator_file = os.path.join(output_dir, f"{creator.lower().replace(' ', '_')}.json")
            write_json(creator_file, materials)
        
        summary_file = os.path.join(output_dir, "summary.json")
        write_json(summary_file, {"creators": list(results.keys())})
        
        logger.info(f"Affiliate materials saved to {output_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error generating affiliate materials: {str(e)}")
        return 1

def handle_feedback(args: argparse.Namespace) -> int:
    """
    Handle the feedback command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    logger.info(f"Starting feedback analysis for: {args.feedback_file}")
    
    # Initialize the OpenAI client
    openai_client = OpenAIClient()
    
    # Create feedback module
    feedback_module = FeedbackModule(openai_client)
    
    # Load feedback data
    feedback_data = read_json(args.feedback_file)
    if not feedback_data:
        logger.error(f"Failed to load feedback from {args.feedback_file}")
        return 1
    
    # Analyze feedback
    try:
        results = feedback_module.analyze_feedback(feedback_data)
        
        # Save results to file
        output_file = args.output or "feedback_summary.json"
        write_json(output_file, results)
        logger.info(f"Feedback analysis saved to {output_file}")
        
        return 0
    except Exception as e:
        logger.error(f"Error analyzing feedback: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 