"""
Tests for the interview workflow generator functionality.
"""

import os
import json
import shutil
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from src.saas_pipeline.niche.workflow import (
    WorkflowManager, WorkflowStatus, ExportFormat
)


class TestWorkflowGenerator(unittest.TestCase):
    """Test cases for the interview workflow generator."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock repository and template manager
        self.repository = MagicMock()
        self.template_manager = MagicMock()
        
        # Set up directories for testing
        self.test_data_dir = "test_data"
        self.repository.data_dir = self.test_data_dir
        self.workflows_dir = os.path.join(self.test_data_dir, "workflows")
        self.sessions_dir = os.path.join(self.test_data_dir, "workflow_sessions")
        
        # Ensure test directories exist
        os.makedirs(self.workflows_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Create workflow manager instance
        self.workflow_manager = WorkflowManager(self.repository, self.template_manager)
        
        # Set up mock template data
        self.mock_template = {
            "id": "template123",
            "name": "Test Template",
            "description": "A test template",
            "niche_type": "test_niche",
            "categories": [
                {
                    "id": "cat1",
                    "name": "Demographics",
                    "description": "Basic demographic questions",
                    "order": 0,
                    "questions": [
                        {
                            "id": "q1",
                            "text": "How old are you?",
                            "type": "open_ended",
                            "order": 0
                        },
                        {
                            "id": "q2",
                            "text": "What is your occupation?",
                            "type": "open_ended",
                            "order": 1
                        }
                    ]
                },
                {
                    "id": "cat2",
                    "name": "Pain Points",
                    "description": "Questions about pain points",
                    "order": 1,
                    "questions": [
                        {
                            "id": "q3",
                            "text": "What challenges do you face?",
                            "type": "open_ended",
                            "order": 0
                        }
                    ]
                }
            ],
            "current_version": "1.0.0"
        }
        
        # Configure mock to return our template
        self.template_manager.get_template.return_value = self.mock_template
        
        # Mock question creation
        self.mock_question = MagicMock()
        self.mock_question.id = "question123"
        self.mock_question.text = "Test question"
        self.mock_question.category = "Test category"
        self.mock_question.order = 0
        self.repository.save_question.return_value = True
        self.repository.get_question.return_value = self.mock_question

    def tearDown(self):
        """Clean up after tests."""
        # Remove test directories
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
    
    def test_create_workflow(self):
        """Test creating a workflow from a template."""
        # Mock UUID generation and datetime to get predictable values
        with patch('uuid.uuid4', return_value="workflow123"), \
             patch('datetime.datetime') as mock_datetime:
            
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0)
            mock_datetime.isoformat = lambda self: self.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Create a workflow
            workflow_id = self.workflow_manager.create_workflow(
                name="Test Workflow",
                description="A test workflow",
                niche_id="niche123",
                template_id="template123"
            )
            
            # Check if workflow was created
            self.assertEqual(workflow_id, "workflow123")
            
            # Check if questions were created for each question in the template
            self.assertEqual(self.repository.save_question.call_count, 3)
    
    def test_get_workflow(self):
        """Test retrieving a workflow."""
        # Create a mock workflow
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.DRAFT.value
        }
        
        # Write the workflow to a file
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Get the workflow
        workflow = self.workflow_manager.get_workflow("workflow123")
        
        # Check if correct workflow was returned
        self.assertEqual(workflow["id"], "workflow123")
        self.assertEqual(workflow["name"], "Test Workflow")
    
    def test_add_branch(self):
        """Test adding a branch to a workflow."""
        # Create a mock workflow with a question group
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [
                {
                    "id": "group1",
                    "title": "Group 1",
                    "description": "First group",
                    "questions": ["question123"],
                    "branches": [],
                    "order": 0
                },
                {
                    "id": "group2",
                    "title": "Group 2",
                    "description": "Second group",
                    "questions": [],
                    "branches": [],
                    "order": 1
                }
            ],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.DRAFT.value
        }
        
        # Write the workflow to a file
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Mock UUID generation
        with patch('uuid.uuid4', return_value="branch123"):
            # Add a branch
            branch_id = self.workflow_manager.add_branch(
                workflow_id="workflow123",
                group_id="group1",
                question_id="question123",
                operator="equals",
                value="yes",
                target_group_id="group2"
            )
            
            # Check if branch was added
            self.assertEqual(branch_id, "branch123")
            
            # Read the updated workflow
            with open(os.path.join(self.workflows_dir, "workflow123.json"), "r") as f:
                updated_workflow = json.load(f)
            
            # Check if branch was correctly added to the workflow
            self.assertEqual(len(updated_workflow["question_groups"][0]["branches"]), 1)
            branch = updated_workflow["question_groups"][0]["branches"][0]
            self.assertEqual(branch["id"], "branch123")
            self.assertEqual(branch["condition"]["question_id"], "question123")
            self.assertEqual(branch["condition"]["operator"], "equals")
            self.assertEqual(branch["condition"]["value"], "yes")
            self.assertEqual(branch["target_group_id"], "group2")
    
    def test_start_session(self):
        """Test starting a workflow session."""
        # Create a mock workflow with a question group
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [
                {
                    "id": "group1",
                    "title": "Group 1",
                    "description": "First group",
                    "questions": ["question123"],
                    "branches": [],
                    "order": 0
                }
            ],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.ACTIVE.value
        }
        
        # Write the workflow to a file
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Mock UUID generation and datetime
        with patch('uuid.uuid4', return_value="session123"), \
             patch('datetime.datetime') as mock_datetime:
            
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0)
            mock_datetime.isoformat = lambda self: self.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Start a session
            session_id = self.workflow_manager.start_session(
                workflow_id="workflow123",
                expert_name="John Doe",
                expert_role="Manager"
            )
            
            # Check if session was created
            self.assertEqual(session_id, "session123")
            
            # Read the created session
            with open(os.path.join(self.sessions_dir, "session123.json"), "r") as f:
                session = json.load(f)
            
            # Check session properties
            self.assertEqual(session["id"], "session123")
            self.assertEqual(session["workflow_id"], "workflow123")
            self.assertEqual(session["expert_name"], "John Doe")
            self.assertEqual(session["expert_role"], "Manager")
            self.assertEqual(session["current_group_id"], "group1")
            self.assertEqual(session["completed_questions"], [])
    
    def test_record_response(self):
        """Test recording a response to a workflow question."""
        # Create a mock session
        test_session = {
            "id": "session123",
            "workflow_id": "workflow123",
            "expert_name": "John Doe",
            "expert_role": "Manager",
            "current_group_id": "group1",
            "completed_questions": [],
            "responses": {},
            "notes": "",
            "started_at": "2023-01-01T12:00:00",
            "last_updated_at": "2023-01-01T12:00:00",
            "completed_at": None
        }
        
        # Create a mock workflow
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [
                {
                    "id": "group1",
                    "title": "Group 1",
                    "description": "First group",
                    "questions": ["question123"],
                    "branches": [],
                    "order": 0
                }
            ],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.ACTIVE.value
        }
        
        # Write the session and workflow to files
        os.makedirs(self.sessions_dir, exist_ok=True)
        with open(os.path.join(self.sessions_dir, "session123.json"), "w") as f:
            json.dump(test_session, f)
        
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Mock response creation
        mock_response = MagicMock()
        mock_response.id = "response123"
        self.repository.save_response.return_value = True
        
        # Record a response
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 30)
            mock_datetime.isoformat = lambda self: self.strftime("%Y-%m-%dT%H:%M:%S")
            
            result = self.workflow_manager.record_response(
                session_id="session123",
                question_id="question123",
                answer="Test answer"
            )
            
            # Check if response was recorded
            self.assertTrue(result)
            
            # Read the updated session
            with open(os.path.join(self.sessions_dir, "session123.json"), "r") as f:
                updated_session = json.load(f)
            
            # Check if question was marked as completed
            self.assertIn("question123", updated_session["completed_questions"])
            
            # Check if response was saved
            self.repository.save_response.assert_called_once()
    
    def test_preview_workflow(self):
        """Test generating a preview of a workflow."""
        # Create a mock workflow
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [
                {
                    "id": "group1",
                    "title": "Group 1",
                    "description": "First group",
                    "questions": ["question123"],
                    "branches": [
                        {
                            "id": "branch123",
                            "condition": {
                                "question_id": "question123",
                                "operator": "equals",
                                "value": "yes"
                            },
                            "target_group_id": "group2"
                        }
                    ],
                    "order": 0
                },
                {
                    "id": "group2",
                    "title": "Group 2",
                    "description": "Second group",
                    "questions": [],
                    "branches": [],
                    "order": 1
                }
            ],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.ACTIVE.value
        }
        
        # Write the workflow to a file
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Generate a preview
        preview = self.workflow_manager.preview_workflow("workflow123")
        
        # Check preview properties
        self.assertEqual(preview["id"], "workflow123")
        self.assertEqual(preview["name"], "Test Workflow")
        self.assertEqual(len(preview["groups"]), 2)
        
        # Check group properties
        group = preview["groups"][0]
        self.assertEqual(group["id"], "group1")
        self.assertEqual(group["title"], "Group 1")
        self.assertEqual(len(group["questions"]), 1)
        self.assertEqual(len(group["branches"]), 1)
        
        # Check branch properties
        branch = group["branches"][0]
        self.assertEqual(branch["id"], "branch123")
        self.assertEqual(branch["question_text"], "Test question")
        self.assertEqual(branch["operator"], "equals")
        self.assertEqual(branch["value"], "yes")
        self.assertEqual(branch["target_group"], "Group 2")
    
    def test_export_workflow(self):
        """Test exporting a workflow to various formats."""
        # Create a mock workflow for preview
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [
                {
                    "id": "group1",
                    "title": "Group 1",
                    "description": "First group",
                    "questions": ["question123"],
                    "branches": [],
                    "order": 0
                }
            ],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.ACTIVE.value
        }
        
        # Write the workflow to a file
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Create exports directory
        exports_dir = os.path.join(self.test_data_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        # Test JSON export
        json_path = self.workflow_manager.export_workflow(
            workflow_id="workflow123",
            format="json",
            output_path=os.path.join(exports_dir, "test_workflow.json")
        )
        self.assertTrue(os.path.exists(json_path))
        
        # Test markdown export
        md_path = self.workflow_manager.export_workflow(
            workflow_id="workflow123",
            format="markdown",
            output_path=os.path.join(exports_dir, "test_workflow.md")
        )
        self.assertTrue(os.path.exists(md_path))
        
        # Test HTML export
        html_path = self.workflow_manager.export_workflow(
            workflow_id="workflow123",
            format="html",
            output_path=os.path.join(exports_dir, "test_workflow.html")
        )
        self.assertTrue(os.path.exists(html_path))
    
    def test_schedule_workflow(self):
        """Test scheduling a workflow interview."""
        # Create a mock workflow
        test_workflow = {
            "id": "workflow123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "niche_id": "niche123",
            "template_id": "template123",
            "question_groups": [],
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
            "status": WorkflowStatus.ACTIVE.value
        }
        
        # Write the workflow to a file
        os.makedirs(self.workflows_dir, exist_ok=True)
        with open(os.path.join(self.workflows_dir, "workflow123.json"), "w") as f:
            json.dump(test_workflow, f)
        
        # Create schedules directory
        schedules_dir = os.path.join(self.test_data_dir, "schedules")
        os.makedirs(schedules_dir, exist_ok=True)
        
        # Schedule a workflow
        with patch('uuid.uuid4', return_value="schedule123"), \
             patch('datetime.datetime') as mock_datetime:
            
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0)
            mock_datetime.isoformat = lambda self: self.strftime("%Y-%m-%dT%H:%M:%S")
            
            scheduled_time = datetime(2023, 1, 2, 14, 0)
            schedule_id = self.workflow_manager.schedule_workflow(
                workflow_id="workflow123",
                scheduled_time=scheduled_time,
                expert_contact="john@example.com"
            )
            
            # Check if schedule was created
            self.assertEqual(schedule_id, "schedule123")
            
            # Check if schedule file was created
            self.assertTrue(os.path.exists(os.path.join(schedules_dir, "schedule123.json")))


if __name__ == "__main__":
    unittest.main() 