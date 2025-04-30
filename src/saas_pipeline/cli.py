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
from .niche.template import QuestionType
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
    
    # Template Management commands
    template_parser = subparsers.add_parser(
        'template', 
        help='Manage interview question templates'
    )
    template_subparsers = template_parser.add_subparsers(
        dest='template_command',
        help='Template management command'
    )
    
    # List templates
    list_parser = template_subparsers.add_parser(
        'list',
        help='List available templates'
    )
    list_parser.add_argument(
        '--output',
        type=str,
        help='Output file for template list (default: print to console)'
    )
    
    # Create template
    create_parser = template_subparsers.add_parser(
        'create',
        help='Create a new template'
    )
    create_parser.add_argument(
        'name',
        type=str,
        help='Name for the new template'
    )
    create_parser.add_argument(
        'niche_type',
        type=str,
        help='Type of niche this template is for'
    )
    create_parser.add_argument(
        '--description',
        type=str,
        default='',
        help='Description for the template'
    )
    
    # Show template
    show_parser = template_subparsers.add_parser(
        'show',
        help='Show details of a template'
    )
    show_parser.add_argument(
        'template_id',
        type=str,
        help='ID of the template to show'
    )
    show_parser.add_argument(
        '--version',
        type=str,
        help='Specific version to show'
    )
    show_parser.add_argument(
        '--output',
        type=str,
        help='Output file for template details (default: print to console)'
    )
    
    # Export template
    export_parser = template_subparsers.add_parser(
        'export',
        help='Export a template to a file'
    )
    export_parser.add_argument(
        'template_id',
        type=str,
        help='ID of the template to export'
    )
    export_parser.add_argument(
        'output',
        type=str,
        help='Output file path for the exported template'
    )
    
    # Import template
    import_parser = template_subparsers.add_parser(
        'import',
        help='Import a template from a file'
    )
    import_parser.add_argument(
        'input',
        type=str,
        help='Input file path for the template to import'
    )
    
    # Delete template
    delete_parser = template_subparsers.add_parser(
        'delete',
        help='Delete a template'
    )
    delete_parser.add_argument(
        'template_id',
        type=str,
        help='ID of the template to delete'
    )
    delete_parser.add_argument(
        '--force',
        action='store_true',
        help='Force deletion without confirmation'
    )
    
    # Add category to template
    add_category_parser = template_subparsers.add_parser(
        'add-category',
        help='Add a category to a template'
    )
    add_category_parser.add_argument(
        'template_id',
        type=str,
        help='ID of the template to modify'
    )
    add_category_parser.add_argument(
        'name',
        type=str,
        help='Name for the new category'
    )
    add_category_parser.add_argument(
        '--description',
        type=str,
        default='',
        help='Description for the category'
    )
    add_category_parser.add_argument(
        '--order',
        type=int,
        help='Order position for the category'
    )
    
    # Add question to template
    add_question_parser = template_subparsers.add_parser(
        'add-question',
        help='Add a question to a template category'
    )
    add_question_parser.add_argument(
        'template_id',
        type=str,
        help='ID of the template to modify'
    )
    add_question_parser.add_argument(
        'category_id',
        type=str,
        help='ID of the category to add the question to'
    )
    add_question_parser.add_argument(
        'text',
        type=str,
        help='Text of the question'
    )
    add_question_parser.add_argument(
        '--type',
        type=str,
        choices=[qt.value for qt in QuestionType],
        default=QuestionType.OPEN_ENDED.value,
        help='Type of question'
    )
    add_question_parser.add_argument(
        '--options',
        type=str,
        help='Options for multiple choice questions (comma-separated)'
    )
    add_question_parser.add_argument(
        '--required',
        action='store_true',
        default=True,
        help='Whether the question is required'
    )
    add_question_parser.add_argument(
        '--order',
        type=int,
        help='Order position for the question'
    )
    
    # Create new template version
    new_version_parser = template_subparsers.add_parser(
        'new-version',
        help='Create a new version of a template'
    )
    new_version_parser.add_argument(
        'template_id',
        type=str,
        help='ID of the template to create a new version for'
    )
    new_version_parser.add_argument(
        'notes',
        type=str,
        help='Notes about the changes in this version'
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
        elif args.command == 'template':
            return handle_template(args)
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

def handle_template(args: argparse.Namespace) -> int:
    """
    Handle the template command.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if not hasattr(args, 'template_command') or not args.template_command:
        logger.error("No template subcommand specified")
        return 1
    
    # Initialize OpenAI client
    openai_client = OpenAIClient()
    
    # Initialize niche research module
    niche_module = NicheResearchModule(openai_client)
    
    # Handle template subcommands
    if args.template_command == 'list':
        return handle_template_list(args, niche_module)
    elif args.template_command == 'create':
        return handle_template_create(args, niche_module)
    elif args.template_command == 'show':
        return handle_template_show(args, niche_module)
    elif args.template_command == 'export':
        return handle_template_export(args, niche_module)
    elif args.template_command == 'import':
        return handle_template_import(args, niche_module)
    elif args.template_command == 'delete':
        return handle_template_delete(args, niche_module)
    elif args.template_command == 'add-category':
        return handle_template_add_category(args, niche_module)
    elif args.template_command == 'add-question':
        return handle_template_add_question(args, niche_module)
    elif args.template_command == 'new-version':
        return handle_template_new_version(args, niche_module)
    else:
        logger.error(f"Unknown template subcommand: {args.template_command}")
        return 1

def handle_template_list(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle listing templates."""
    templates = niche_module.get_templates()
    
    if args.output:
        write_json(args.output, {"templates": templates})
        logger.info(f"Template list written to {args.output}")
    else:
        # Print to console
        if not templates:
            print("No templates found.")
        else:
            print(f"Found {len(templates)} templates:")
            for t in templates:
                print(f"  - {t['name']} (ID: {t['id']})")
                print(f"    Type: {t['niche_type']}")
                print(f"    Description: {t['description']}")
                print(f"    Current version: {t['current_version']}")
                print()
    
    return 0

def handle_template_create(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle creating a new template."""
    template_id = niche_module.create_template(
        name=args.name,
        description=args.description,
        niche_type=args.niche_type
    )
    
    logger.info(f"Created template {args.name} with ID: {template_id}")
    return 0

def handle_template_show(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle showing template details."""
    try:
        template = niche_module.get_template(args.template_id, args.version)
        
        if args.output:
            write_json(args.output, template)
            logger.info(f"Template details written to {args.output}")
        else:
            # Print to console
            print(f"Template: {template['name']} (ID: {template['id']})")
            print(f"Description: {template['description']}")
            print(f"Niche type: {template['niche_type']}")
            print(f"Current version: {template['current_version']}")
            print(f"Created: {template['created_at']}")
            print(f"Updated: {template['updated_at']}")
            print(f"Is default: {template['is_default']}")
            print()
            
            print(f"Versions:")
            for v in template['versions']:
                print(f"  - {v['version']} (Created: {v['created_at']})")
                print(f"    Changes: {v['changes']}")
                print(f"    Created by: {v['created_by']}")
                print()
            
            print(f"Categories ({len(template['categories'])}):")
            for category in sorted(template['categories'], key=lambda c: c['order']):
                print(f"  - {category['name']} (ID: {category['id']})")
                print(f"    Description: {category['description']}")
                print(f"    Order: {category['order']}")
                print()
                
                print(f"    Questions ({len(category['questions'])}):")
                for question in sorted(category['questions'], key=lambda q: q['order']):
                    print(f"      - {question['text']} (ID: {question['id']})")
                    print(f"        Type: {question['type']}")
                    print(f"        Required: {question['required']}")
                    if question['type'] == QuestionType.MULTIPLE_CHOICE.value and question.get('options'):
                        print(f"        Options: {', '.join(question['options'])}")
                    print()
        
        return 0
    except ValueError as e:
        logger.error(str(e))
        return 1

def handle_template_export(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle exporting a template."""
    try:
        success = niche_module.export_template(args.template_id, args.output)
        if success:
            logger.info(f"Exported template {args.template_id} to {args.output}")
            return 0
        else:
            logger.error(f"Failed to export template {args.template_id}")
            return 1
    except ValueError as e:
        logger.error(str(e))
        return 1

def handle_template_import(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle importing a template."""
    try:
        template_id = niche_module.import_template(args.input)
        if template_id:
            logger.info(f"Imported template from {args.input} with ID: {template_id}")
            return 0
        else:
            logger.error(f"Failed to import template from {args.input}")
            return 1
    except Exception as e:
        logger.error(f"Error importing template: {str(e)}")
        return 1

def handle_template_delete(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle deleting a template."""
    try:
        # Confirm deletion unless force flag is set
        if not args.force:
            try:
                template = niche_module.get_template(args.template_id)
                confirm = input(f"Are you sure you want to delete template '{template['name']}' (ID: {args.template_id})? [y/N] ")
                if confirm.lower() not in ['y', 'yes']:
                    logger.info("Deletion cancelled by user")
                    return 0
            except ValueError:
                logger.warning(f"Template {args.template_id} not found, proceeding with deletion")
        
        success = niche_module.delete_template(args.template_id)
        if success:
            logger.info(f"Deleted template {args.template_id}")
            return 0
        else:
            logger.error(f"Failed to delete template {args.template_id}")
            return 1
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return 1

def handle_template_add_category(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle adding a category to a template."""
    try:
        category_id = niche_module.add_template_category(
            template_id=args.template_id,
            name=args.name,
            description=args.description,
            order=args.order
        )
        
        logger.info(f"Added category '{args.name}' to template {args.template_id} with ID: {category_id}")
        return 0
    except ValueError as e:
        logger.error(str(e))
        return 1

def handle_template_add_question(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle adding a question to a template category."""
    try:
        # Process options for multiple choice
        options = None
        if args.type == QuestionType.MULTIPLE_CHOICE.value:
            if not args.options:
                logger.error("Options are required for multiple choice questions")
                return 1
            options = [opt.strip() for opt in args.options.split(',')]
        
        question_id = niche_module.add_template_question(
            template_id=args.template_id,
            category_id=args.category_id,
            text=args.text,
            question_type=args.type,
            options=options,
            required=args.required,
            order=args.order
        )
        
        logger.info(f"Added question to template {args.template_id} with ID: {question_id}")
        return 0
    except ValueError as e:
        logger.error(str(e))
        return 1

def handle_template_new_version(args: argparse.Namespace, niche_module: NicheResearchModule) -> int:
    """Handle creating a new version of a template."""
    try:
        template = niche_module.update_template(
            template_id=args.template_id,
            updates={},  # No content changes, just version bump
            create_new_version=True,
            version_notes=args.notes
        )
        
        logger.info(f"Created new version {template['current_version']} for template {args.template_id}")
        return 0
    except ValueError as e:
        logger.error(str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main()) 