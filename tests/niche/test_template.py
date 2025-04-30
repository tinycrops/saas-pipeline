"""
Tests for the niche research template system.

This module contains tests for the interview question template functionality.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.saas_pipeline.niche.template import (
    TemplateManager, QuestionType, QuestionTemplate, TemplateCategory
)


class TestTemplateManager(unittest.TestCase):
    """Test cases for the TemplateManager class."""
    
    def setUp(self):
        """Set up test environment with temporary directory for template storage."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = self.temp_dir.name
        self.templates_dir = os.path.join(self.data_dir, "templates")
        
        # Create a template manager with the temp directory
        self.template_manager = TemplateManager(self.data_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
    
    def test_create_template(self):
        """Test creation of a new template."""
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Verify template ID was returned
        self.assertIsNotNone(template_id)
        self.assertTrue(len(template_id) > 0)
        
        # Verify template directory was created
        template_dir = os.path.join(self.templates_dir, template_id)
        self.assertTrue(os.path.isdir(template_dir))
        
        # Verify metadata file exists
        metadata_path = os.path.join(template_dir, "metadata.json")
        self.assertTrue(os.path.isfile(metadata_path))
        
        # Verify version file exists
        version_path = os.path.join(template_dir, "1.0.0.json")
        self.assertTrue(os.path.isfile(version_path))
        
        # Verify metadata content
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            self.assertEqual(metadata["name"], "Test Template")
            self.assertEqual(metadata["description"], "Test description")
            self.assertEqual(metadata["niche_type"], "test_niche")
            self.assertEqual(metadata["current_version"], "1.0.0")
            self.assertEqual(len(metadata["versions"]), 1)
            self.assertEqual(metadata["versions"][0]["version"], "1.0.0")
    
    def test_get_template(self):
        """Test retrieving a template."""
        # Create a template first
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Retrieve the template
        template = self.template_manager.get_template(template_id)
        
        # Verify template content
        self.assertEqual(template["id"], template_id)
        self.assertEqual(template["name"], "Test Template")
        self.assertEqual(template["description"], "Test description")
        self.assertEqual(template["niche_type"], "test_niche")
        self.assertEqual(template["current_version"], "1.0.0")
        self.assertEqual(len(template["versions"]), 1)
        self.assertEqual(template["categories"], [])
    
    def test_update_template(self):
        """Test updating a template."""
        # Create a template first
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Update the template
        updated_template = self.template_manager.update_template(
            template_id=template_id,
            updates={"name": "Updated Name", "description": "Updated description"}
        )
        
        # Verify updates were applied
        self.assertEqual(updated_template["name"], "Updated Name")
        self.assertEqual(updated_template["description"], "Updated description")
        
        # Retrieve the template again to confirm persistence
        template = self.template_manager.get_template(template_id)
        self.assertEqual(template["name"], "Updated Name")
        self.assertEqual(template["description"], "Updated description")
    
    def test_create_new_version(self):
        """Test creating a new version of a template."""
        # Create a template first
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Add a category
        category_id = self.template_manager.add_category(
            template_id=template_id,
            name="Test Category",
            description="Test category description"
        )
        
        # Create a new version
        updated_template = self.template_manager.update_template(
            template_id=template_id,
            updates={"name": "Template v2"},
            create_new_version=True,
            version_notes="Updated template name and added category"
        )
        
        # Verify new version was created
        self.assertEqual(updated_template["current_version"], "1.1.0")
        self.assertEqual(len(updated_template["versions"]), 2)
        self.assertEqual(updated_template["versions"][1]["version"], "1.1.0")
        self.assertEqual(
            updated_template["versions"][1]["changes"], 
            "Updated template name and added category"
        )
        
        # Verify version file exists
        version_path = os.path.join(
            self.templates_dir, template_id, "1.1.0.json"
        )
        self.assertTrue(os.path.isfile(version_path))
    
    def test_get_specific_version(self):
        """Test retrieving a specific version of a template."""
        # Create a template first
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Create a new version
        self.template_manager.update_template(
            template_id=template_id,
            updates={"name": "Template v2"},
            create_new_version=True,
            version_notes="Updated template name"
        )
        
        # Get the original version
        original_template = self.template_manager.get_template(
            template_id=template_id,
            version="1.0.0"
        )
        
        # Verify it's the original version
        self.assertEqual(original_template["name"], "Test Template")
        self.assertEqual(original_template["current_version"], "1.1.0")  # This is still the current version in metadata
    
    def test_delete_template(self):
        """Test deleting a template."""
        # Create a template first
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Verify it exists
        template_dir = os.path.join(self.templates_dir, template_id)
        self.assertTrue(os.path.isdir(template_dir))
        
        # Delete the template
        result = self.template_manager.delete_template(template_id)
        
        # Verify delete was successful
        self.assertTrue(result)
        
        # Verify directory was removed
        self.assertFalse(os.path.exists(template_dir))
    
    def test_list_templates(self):
        """Test listing all templates."""
        # Create a few templates
        id1 = self.template_manager.create_template(
            name="Template 1",
            description="Description 1",
            niche_type="niche1"
        )
        
        id2 = self.template_manager.create_template(
            name="Template 2",
            description="Description 2",
            niche_type="niche2"
        )
        
        # List templates
        templates = self.template_manager.list_templates()
        
        # Verify list contains the templates
        self.assertEqual(len(templates), 2)
        template_ids = [t["id"] for t in templates]
        self.assertIn(id1, template_ids)
        self.assertIn(id2, template_ids)
    
    def test_add_category(self):
        """Test adding a category to a template."""
        # Create a template first
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        # Add a category
        category_id = self.template_manager.add_category(
            template_id=template_id,
            name="Test Category",
            description="Test category description",
            order=1
        )
        
        # Verify category ID was returned
        self.assertIsNotNone(category_id)
        
        # Retrieve the template to verify the category was added
        template = self.template_manager.get_template(template_id)
        self.assertEqual(len(template["categories"]), 1)
        self.assertEqual(template["categories"][0]["id"], category_id)
        self.assertEqual(template["categories"][0]["name"], "Test Category")
        self.assertEqual(template["categories"][0]["order"], 1)
    
    def test_add_question(self):
        """Test adding a question to a template category."""
        # Create a template with a category
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        category_id = self.template_manager.add_category(
            template_id=template_id,
            name="Test Category",
            description="Test category description"
        )
        
        # Add a question
        question_id = self.template_manager.add_question(
            template_id=template_id,
            category_id=category_id,
            text="Test question?",
            question_type=QuestionType.OPEN_ENDED,
            required=True
        )
        
        # Verify question ID was returned
        self.assertIsNotNone(question_id)
        
        # Retrieve the template to verify the question was added
        template = self.template_manager.get_template(template_id)
        self.assertEqual(len(template["categories"][0]["questions"]), 1)
        self.assertEqual(template["categories"][0]["questions"][0]["id"], question_id)
        self.assertEqual(template["categories"][0]["questions"][0]["text"], "Test question?")
        self.assertEqual(template["categories"][0]["questions"][0]["type"], "open_ended")
        self.assertEqual(template["categories"][0]["questions"][0]["required"], True)
    
    def test_add_multiple_choice_question(self):
        """Test adding a multiple choice question."""
        # Create a template with a category
        template_id = self.template_manager.create_template(
            name="Test Template",
            description="Test description",
            niche_type="test_niche"
        )
        
        category_id = self.template_manager.add_category(
            template_id=template_id,
            name="Test Category",
            description="Test category description"
        )
        
        # Add a multiple choice question
        options = ["Option 1", "Option 2", "Option 3"]
        question_id = self.template_manager.add_question(
            template_id=template_id,
            category_id=category_id,
            text="Choose an option:",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=options,
            required=True
        )
        
        # Retrieve the template to verify the question was added correctly
        template = self.template_manager.get_template(template_id)
        question = template["categories"][0]["questions"][0]
        self.assertEqual(question["type"], "multiple_choice")
        self.assertEqual(question["options"], options)
    
    def test_export_import_template(self):
        """Test exporting and importing a template."""
        # Create a template with a category and question
        template_id = self.template_manager.create_template(
            name="Export Test",
            description="Template for export testing",
            niche_type="export_test"
        )
        
        category_id = self.template_manager.add_category(
            template_id=template_id,
            name="Test Category",
            description="Test category description"
        )
        
        self.template_manager.add_question(
            template_id=template_id,
            category_id=category_id,
            text="Test question?",
            question_type=QuestionType.OPEN_ENDED
        )
        
        # Export the template
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            export_path = tmp.name
        
        export_result = self.template_manager.export_template(template_id, export_path)
        self.assertTrue(export_result)
        
        # Import the template into a new manager
        new_temp_dir = tempfile.TemporaryDirectory()
        new_manager = TemplateManager(new_temp_dir.name)
        
        imported_id = new_manager.import_template(export_path)
        self.assertIsNotNone(imported_id)
        
        # Verify imported template matches the original
        original = self.template_manager.get_template(template_id)
        imported = new_manager.get_template(imported_id)
        
        self.assertEqual(original["name"], imported["name"])
        self.assertEqual(original["description"], imported["description"])
        self.assertEqual(original["niche_type"], imported["niche_type"])
        self.assertEqual(len(original["categories"]), len(imported["categories"]))
        self.assertEqual(original["categories"][0]["name"], imported["categories"][0]["name"])
        
        # Clean up
        os.unlink(export_path)
        new_temp_dir.cleanup()
    
    def test_predefined_templates(self):
        """Test that predefined templates are created on initialization."""
        # List templates - should include predefined ones
        templates = self.template_manager.list_templates()
        
        # Verify at least 3 templates (the predefined ones)
        self.assertGreaterEqual(len(templates), 3)
        
        # Check for specific predefined templates
        template_names = [t["name"] for t in templates]
        self.assertIn("SaaS User Interview Template", template_names)
        self.assertIn("E-commerce Customer Interview Template", template_names)
        self.assertIn("Content Creator Audience Template", template_names)


if __name__ == "__main__":
    unittest.main() 