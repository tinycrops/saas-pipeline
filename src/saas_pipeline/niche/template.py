"""
Interview Question Template System

This module provides functionality for defining, managing, and retrieving
interview question templates for different niche types. It includes support
for template versioning, import/export, and predefined templates.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import List, Dict, Optional, Any, Union, TypedDict, cast

from ..utils.file_io import ensure_directory, read_json, write_json

logger = logging.getLogger(__name__)

# Default templates directory relative to niche data directory
DEFAULT_TEMPLATES_DIR = "templates"


class QuestionType(str, Enum):
    """Types of questions supported in interview templates."""
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    YES_NO = "yes_no"


class Question(TypedDict):
    """Definition of a question within a template category."""
    id: str
    text: str
    type: str  # QuestionType value
    options: Optional[List[str]]  # For multiple choice questions
    required: bool
    default_value: Optional[str]
    order: int


class TemplateCategory(TypedDict):
    """Definition of a category within a template."""
    id: str
    name: str
    description: str
    questions: List[Question]
    order: int


class TemplateVersion(TypedDict):
    """Version information for a template."""
    version: str
    created_at: str
    created_by: str
    changes: str


class QuestionTemplate(TypedDict):
    """Complete definition of an interview question template."""
    id: str
    name: str
    description: str
    niche_type: str
    categories: List[TemplateCategory]
    versions: List[TemplateVersion]
    current_version: str
    created_at: str
    updated_at: str
    is_default: bool


class TemplateMetadata(TypedDict):
    """Metadata for a template, stored separately from version content."""
    id: str
    name: str
    description: str
    niche_type: str
    versions: List[TemplateVersion]
    current_version: str
    created_at: str
    updated_at: str
    is_default: bool


class TemplateManager:
    """Manager for interview question templates."""
    
    def __init__(self, data_dir: str):
        """
        Initialize the template manager.
        
        Args:
            data_dir: Base directory for niche data
        """
        self.templates_dir = os.path.join(data_dir, DEFAULT_TEMPLATES_DIR)
        ensure_directory(self.templates_dir)
        self._init_predefined_templates()
    
    def _get_template_dir(self, template_id: str) -> str:
        """Get the directory path for a specific template."""
        return os.path.join(self.templates_dir, template_id)
    
    def _get_metadata_path(self, template_id: str) -> str:
        """Get the metadata file path for a template."""
        return os.path.join(self._get_template_dir(template_id), "metadata.json")
    
    def _get_version_path(self, template_id: str, version: str) -> str:
        """Get the file path for a specific template version."""
        return os.path.join(self._get_template_dir(template_id), f"{version}.json")
    
    def create_template(self, 
                        name: str, 
                        description: str, 
                        niche_type: str,
                        categories: Optional[List[TemplateCategory]] = None,
                        created_by: str = "system") -> str:
        """
        Create a new interview question template.
        
        Args:
            name: Template name
            description: Template description
            niche_type: Type of niche this template is for
            categories: Optional list of initial template categories
            created_by: Identifier of the creator
            
        Returns:
            ID of the created template
        """
        template_id = str(uuid.uuid4())
        template_dir = self._get_template_dir(template_id)
        ensure_directory(template_dir)
        
        now = datetime.now().isoformat()
        initial_version = "1.0.0"
        
        # Create metadata
        metadata: TemplateMetadata = {
            "id": template_id,
            "name": name,
            "description": description,
            "niche_type": niche_type,
            "versions": [{
                "version": initial_version,
                "created_at": now,
                "created_by": created_by,
                "changes": "Initial version"
            }],
            "current_version": initial_version,
            "created_at": now,
            "updated_at": now,
            "is_default": False
        }
        
        # Save metadata
        metadata_path = self._get_metadata_path(template_id)
        if not write_json(metadata_path, metadata):
            logger.error(f"Failed to write template metadata to {metadata_path}")
            raise IOError(f"Failed to create template: {name}")
        
        # Create version content
        version_content = {
            "categories": categories or []
        }
        
        # Save version content
        version_path = self._get_version_path(template_id, initial_version)
        if not write_json(version_path, version_content):
            logger.error(f"Failed to write template version to {version_path}")
            raise IOError(f"Failed to create template version: {initial_version}")
        
        logger.info(f"Created template {name} with ID {template_id}")
        return template_id
    
    def get_template(self, template_id: str, version: Optional[str] = None) -> QuestionTemplate:
        """
        Get a template by ID, optionally specifying a version.
        
        Args:
            template_id: ID of the template to retrieve
            version: Optional specific version to retrieve
            
        Returns:
            Complete template object
            
        Raises:
            ValueError: If template or version not found
        """
        # Read metadata
        metadata_path = self._get_metadata_path(template_id)
        metadata = read_json(metadata_path)
        if not metadata:
            raise ValueError(f"Template not found: {template_id}")
        
        # Determine which version to load
        version_to_load = version or metadata.get("current_version")
        if not version_to_load:
            raise ValueError(f"No version specified and no current version set for template: {template_id}")
        
        # Validate version exists
        if not any(v.get("version") == version_to_load for v in metadata.get("versions", [])):
            raise ValueError(f"Version {version_to_load} not found for template: {template_id}")
        
        # Read version content
        version_path = self._get_version_path(template_id, version_to_load)
        version_content = read_json(version_path)
        if not version_content:
            raise ValueError(f"Template version content not found: {version_to_load}")
        
        # Combine metadata and version content
        template = cast(QuestionTemplate, {**metadata})
        template["categories"] = version_content.get("categories", [])
        
        return template
    
    def update_template(self, 
                        template_id: str, 
                        updates: Dict[str, Any],
                        create_new_version: bool = False,
                        version_notes: str = "",
                        created_by: str = "system") -> QuestionTemplate:
        """
        Update a template, optionally creating a new version.
        
        Args:
            template_id: ID of the template to update
            updates: Dictionary of updates to apply
            create_new_version: Whether to create a new version
            version_notes: Notes about the changes (required if create_new_version is True)
            created_by: Identifier of the creator
            
        Returns:
            Updated template object
            
        Raises:
            ValueError: If template not found or invalid updates
        """
        # Read existing template
        template = self.get_template(template_id)
        
        # Handle metadata updates
        metadata_updates = {}
        version_content_updates = {}
        
        for key, value in updates.items():
            if key == "categories":
                version_content_updates["categories"] = value
            elif key in ["name", "description", "niche_type", "is_default"]:
                metadata_updates[key] = value
            else:
                logger.warning(f"Ignoring unknown update field: {key}")
        
        if create_new_version:
            if not version_notes:
                raise ValueError("Version notes are required when creating a new version")
            
            # Determine new version number
            current_version = template["current_version"]
            major, minor, patch = map(int, current_version.split("."))
            
            # For now, just increment minor version
            new_version = f"{major}.{minor + 1}.0"
            
            # Add new version to metadata
            now = datetime.now().isoformat()
            new_version_info: TemplateVersion = {
                "version": new_version,
                "created_at": now,
                "created_by": created_by,
                "changes": version_notes
            }
            
            metadata_updates["versions"] = template["versions"] + [new_version_info]
            metadata_updates["current_version"] = new_version
            metadata_updates["updated_at"] = now
            
            # Save current template content as new version
            new_categories = version_content_updates.get("categories", template["categories"])
            new_version_content = {
                "categories": new_categories
            }
            
            # Write new version file
            version_path = self._get_version_path(template_id, new_version)
            if not write_json(version_path, new_version_content):
                logger.error(f"Failed to write new template version to {version_path}")
                raise IOError(f"Failed to create template version: {new_version}")
        else:
            # Just update the current version
            metadata_updates["updated_at"] = datetime.now().isoformat()
            
            if version_content_updates:
                # Read current version content
                current_version = template["current_version"]
                version_path = self._get_version_path(template_id, current_version)
                version_content = read_json(version_path, default={})
                
                # Update and write back
                if "categories" in version_content_updates:
                    version_content["categories"] = version_content_updates["categories"]
                    
                if not write_json(version_path, version_content):
                    logger.error(f"Failed to update template version content at {version_path}")
                    raise IOError(f"Failed to update template version: {current_version}")
        
        # Update metadata file
        metadata_path = self._get_metadata_path(template_id)
        metadata = read_json(metadata_path, default={})
        for key, value in metadata_updates.items():
            metadata[key] = value
            
        if not write_json(metadata_path, metadata):
            logger.error(f"Failed to update template metadata at {metadata_path}")
            raise IOError(f"Failed to update template metadata: {template_id}")
        
        # Return the updated template
        return self.get_template(template_id)
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template and all its versions.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            True if successful, False otherwise
        """
        template_dir = self._get_template_dir(template_id)
        if not os.path.exists(template_dir):
            logger.warning(f"Template directory not found: {template_dir}")
            return False
        
        try:
            # Delete all files in the directory
            for file_path in Path(template_dir).glob("*"):
                file_path.unlink()
            
            # Remove the directory
            os.rmdir(template_dir)
            logger.info(f"Deleted template: {template_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {str(e)}")
            return False
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates (metadata only).
        
        Returns:
            List of template metadata dictionaries
        """
        templates = []
        
        try:
            # Iterate through template directories
            for item in os.listdir(self.templates_dir):
                template_dir = os.path.join(self.templates_dir, item)
                if os.path.isdir(template_dir):
                    metadata_path = os.path.join(template_dir, "metadata.json")
                    if os.path.isfile(metadata_path):
                        metadata = read_json(metadata_path)
                        if metadata:
                            templates.append(metadata)
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
        
        return templates
    
    def export_template(self, template_id: str, export_path: str) -> bool:
        """
        Export a template to a JSON file.
        
        Args:
            template_id: ID of the template to export
            export_path: Path where the template should be exported
            
        Returns:
            True if successful, False otherwise
        """
        try:
            template = self.get_template(template_id)
            return write_json(export_path, template)
        except Exception as e:
            logger.error(f"Error exporting template {template_id}: {str(e)}")
            return False
    
    def import_template(self, import_path: str, created_by: str = "system") -> Optional[str]:
        """
        Import a template from a JSON file.
        
        Args:
            import_path: Path to the template JSON file
            created_by: Identifier of the importer
            
        Returns:
            ID of the imported template if successful, None otherwise
        """
        try:
            template_data = read_json(import_path)
            if not template_data:
                logger.error(f"Failed to read template data from {import_path}")
                return None
            
            # Generate a new ID for the imported template
            new_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Extract basic metadata
            name = template_data.get("name", "Imported Template")
            description = template_data.get("description", "Imported from file")
            niche_type = template_data.get("niche_type", "general")
            categories = template_data.get("categories", [])
            
            # Create a new template with the imported data
            template_id = self.create_template(
                name=name,
                description=description,
                niche_type=niche_type,
                categories=categories,
                created_by=created_by
            )
            
            logger.info(f"Imported template {name} with new ID {template_id}")
            return template_id
        except Exception as e:
            logger.error(f"Error importing template from {import_path}: {str(e)}")
            return None
    
    def add_category(self, 
                     template_id: str, 
                     name: str, 
                     description: str,
                     order: Optional[int] = None) -> str:
        """
        Add a category to a template.
        
        Args:
            template_id: ID of the template
            name: Category name
            description: Category description
            order: Optional order position (will be placed last if not specified)
            
        Returns:
            ID of the created category
        """
        template = self.get_template(template_id)
        categories = template["categories"]
        
        # Determine order if not provided
        if order is None:
            order = max([c.get("order", 0) for c in categories], default=0) + 1
        
        # Create new category
        category_id = str(uuid.uuid4())
        new_category: TemplateCategory = {
            "id": category_id,
            "name": name,
            "description": description,
            "questions": [],
            "order": order
        }
        
        # Add to template
        categories.append(new_category)
        
        # Update template
        self.update_template(
            template_id=template_id,
            updates={"categories": categories}
        )
        
        return category_id
    
    def add_question(self,
                    template_id: str,
                    category_id: str,
                    text: str,
                    question_type: Union[QuestionType, str],
                    options: Optional[List[str]] = None,
                    required: bool = True,
                    default_value: Optional[str] = None,
                    order: Optional[int] = None) -> str:
        """
        Add a question to a template category.
        
        Args:
            template_id: ID of the template
            category_id: ID of the category to add the question to
            text: Question text
            question_type: Type of question
            options: Options for multiple choice questions
            required: Whether the question is required
            default_value: Optional default value
            order: Optional order position (will be placed last if not specified)
            
        Returns:
            ID of the created question
        """
        # Convert enum to string if needed
        if isinstance(question_type, QuestionType):
            question_type = question_type.value
        
        # Validate question type
        if question_type not in [qt.value for qt in QuestionType]:
            raise ValueError(f"Invalid question type: {question_type}")
        
        # Validate options for multiple choice
        if question_type == QuestionType.MULTIPLE_CHOICE.value and not options:
            raise ValueError("Options are required for multiple choice questions")
        
        template = self.get_template(template_id)
        categories = template["categories"]
        
        # Find the target category
        target_category = None
        for i, category in enumerate(categories):
            if category["id"] == category_id:
                target_category = category
                category_index = i
                break
        
        if not target_category:
            raise ValueError(f"Category not found: {category_id}")
        
        # Determine order if not provided
        if order is None:
            order = max([q.get("order", 0) for q in target_category["questions"]], default=0) + 1
        
        # Create new question
        question_id = str(uuid.uuid4())
        new_question: Question = {
            "id": question_id,
            "text": text,
            "type": question_type,
            "options": options,
            "required": required,
            "default_value": default_value,
            "order": order
        }
        
        # Add to category
        target_category["questions"].append(new_question)
        categories[category_index] = target_category
        
        # Update template
        self.update_template(
            template_id=template_id,
            updates={"categories": categories}
        )
        
        return question_id
    
    def _init_predefined_templates(self):
        """Initialize predefined templates if they don't already exist."""
        # Check if we already have templates
        existing_templates = self.list_templates()
        if existing_templates:
            return
        
        # Create predefined templates
        self._create_saas_template()
        self._create_ecommerce_template()
        self._create_content_creator_template()
    
    def _create_saas_template(self):
        """Create a predefined template for SaaS user interviews."""
        template_id = self.create_template(
            name="SaaS User Interview Template",
            description="Template for interviewing users of SaaS products",
            niche_type="saas",
            created_by="system"
        )
        
        # Add categories
        demographics_id = self.add_category(
            template_id=template_id,
            name="Demographics",
            description="Basic information about the interviewee",
            order=1
        )
        
        pain_points_id = self.add_category(
            template_id=template_id,
            name="Pain Points",
            description="Challenges and problems faced by the user",
            order=2
        )
        
        solutions_id = self.add_category(
            template_id=template_id,
            name="Current Solutions",
            description="How the user currently solves these problems",
            order=3
        )
        
        expectations_id = self.add_category(
            template_id=template_id,
            name="Expectations",
            description="What the user expects from an ideal solution",
            order=4
        )
        
        # Add questions to demographics
        self.add_question(
            template_id=template_id,
            category_id=demographics_id,
            text="What is your job title or role?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=demographics_id,
            text="How long have you been in this role?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        )
        
        self.add_question(
            template_id=template_id,
            category_id=demographics_id,
            text="What industry do you work in?",
            question_type=QuestionType.OPEN_ENDED,
            order=3
        )
        
        # Add questions to pain points
        self.add_question(
            template_id=template_id,
            category_id=pain_points_id,
            text="What are your biggest challenges in your current workflow?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=pain_points_id,
            text="How much time do you spend on these pain points each week?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        )
        
        self.add_question(
            template_id=template_id,
            category_id=pain_points_id,
            text="On a scale of 1-5, how severe is this pain point?",
            question_type=QuestionType.SCALE,
            order=3
        )
        
        # Add questions to solutions
        self.add_question(
            template_id=template_id,
            category_id=solutions_id,
            text="What tools or methods do you currently use to address these challenges?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=solutions_id,
            text="What do you like about your current solution?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        )
        
        self.add_question(
            template_id=template_id,
            category_id=solutions_id,
            text="What do you dislike about your current solution?",
            question_type=QuestionType.OPEN_ENDED,
            order=3
        )
        
        # Add questions to expectations
        self.add_question(
            template_id=template_id,
            category_id=expectations_id,
            text="What would an ideal solution look like to you?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=expectations_id,
            text="How much would you be willing to pay for a solution that solves this problem?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        )
        
        self.add_question(
            template_id=template_id,
            category_id=expectations_id,
            text="Would you prefer a monthly subscription or a one-time purchase?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Monthly subscription", "Annual subscription", "One-time purchase", "Not sure"],
            order=3
        )
        
        # Mark as default
        self.update_template(
            template_id=template_id,
            updates={"is_default": True}
        )
    
    def _create_ecommerce_template(self):
        """Create a predefined template for e-commerce customer interviews."""
        template_id = self.create_template(
            name="E-commerce Customer Interview Template",
            description="Template for interviewing e-commerce customers",
            niche_type="ecommerce",
            created_by="system"
        )
        
        # Add categories
        demographics_id = self.add_category(
            template_id=template_id,
            name="Shopping Habits",
            description="Information about shopping behavior",
            order=1
        )
        
        pain_points_id = self.add_category(
            template_id=template_id,
            name="Purchase Frustrations",
            description="Problems encountered during online shopping",
            order=2
        )
        
        product_id = self.add_category(
            template_id=template_id,
            name="Product Preferences",
            description="What matters most in product selection",
            order=3
        )
        
        # Add questions to demographics
        self.add_question(
            template_id=template_id,
            category_id=demographics_id,
            text="How often do you shop online?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Daily", "Weekly", "Monthly", "Rarely"],
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=demographics_id,
            text="What types of products do you typically purchase online?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        )
        
        # Add questions to pain points
        self.add_question(
            template_id=template_id,
            category_id=pain_points_id,
            text="What frustrates you most about online shopping?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=pain_points_id,
            text="Have you abandoned a purchase recently? If so, why?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        )
        
        # Add questions to product preferences
        self.add_question(
            template_id=template_id,
            category_id=product_id,
            text="How important is price in your purchase decision?",
            question_type=QuestionType.SCALE,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=product_id,
            text="How do you typically discover new products?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Social media", "Search engines", "Friends/family", "Email newsletters", "Other"],
            order=2
        )
    
    def _create_content_creator_template(self):
        """Create a predefined template for content creator audience interviews."""
        template_id = self.create_template(
            name="Content Creator Audience Template",
            description="Template for interviewing audience members of content creators",
            niche_type="content_creator",
            created_by="system"
        )
        
        # Add categories
        consumption_id = self.add_category(
            template_id=template_id,
            name="Content Consumption",
            description="How the audience consumes content",
            order=1
        )
        
        preferences_id = self.add_category(
            template_id=template_id,
            name="Content Preferences",
            description="What content the audience prefers",
            order=2
        )
        
        monetization_id = self.add_category(
            template_id=template_id,
            name="Monetization Willingness",
            description="Willingness to pay for content",
            order=3
        )
        
        # Add questions to consumption
        self.add_question(
            template_id=template_id,
            category_id=consumption_id,
            text="How did you discover this content creator?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=consumption_id,
            text="How often do you consume their content?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Daily", "Several times a week", "Weekly", "Monthly", "Rarely"],
            order=2
        )
        
        # Add questions to preferences
        self.add_question(
            template_id=template_id,
            category_id=preferences_id,
            text="What topics do you enjoy most from this creator?",
            question_type=QuestionType.OPEN_ENDED,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=preferences_id,
            text="What format do you prefer?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Video", "Audio/Podcast", "Written", "Images", "Live streams"],
            order=2
        )
        
        # Add questions to monetization
        self.add_question(
            template_id=template_id,
            category_id=monetization_id,
            text="Have you ever purchased a product from this creator?",
            question_type=QuestionType.YES_NO,
            order=1
        )
        
        self.add_question(
            template_id=template_id,
            category_id=monetization_id,
            text="What would make you consider paying for premium content?",
            question_type=QuestionType.OPEN_ENDED,
            order=2
        ) 