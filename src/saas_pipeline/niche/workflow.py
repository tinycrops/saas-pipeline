"""
Interview Workflow Generator

This module provides functionality for creating structured interview workflows
based on templates, with support for sequential question groups, branching logic,
customization options, workflow export, and session tracking.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TypedDict, List, Dict, Optional, Any, Union, cast
from enum import Enum

from ..utils.file_io import ensure_directory, read_json, write_json
from .template import TemplateManager, QuestionType
from .models import Interview, InterviewQuestion, Response

logger = logging.getLogger(__name__)

# Default workflows directory relative to niche data directory
DEFAULT_WORKFLOWS_DIR = "workflows"
DEFAULT_SESSIONS_DIR = "workflow_sessions"


class BranchCondition(TypedDict):
    """Condition for branching logic in workflows."""
    question_id: str
    operator: str  # "equals", "contains", "greater_than", "less_than"
    value: Any


class WorkflowBranch(TypedDict):
    """Branch in a workflow, triggered by a condition."""
    id: str
    condition: BranchCondition
    target_group_id: str


class WorkflowQuestionGroup(TypedDict):
    """Group of questions in a workflow, with optional branching logic."""
    id: str
    title: str
    description: str
    questions: List[str]  # question IDs
    branches: List[WorkflowBranch]
    order: int


class WorkflowStatus(str, Enum):
    """Status of an interview workflow."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class InterviewWorkflow(TypedDict):
    """Complete definition of an interview workflow."""
    id: str
    name: str
    description: str
    niche_id: str
    template_id: str
    question_groups: List[WorkflowQuestionGroup]
    created_at: str
    updated_at: str
    status: str


class WorkflowSession(TypedDict):
    """Session tracking a specific interview workflow in progress."""
    id: str
    workflow_id: str
    expert_name: str
    expert_role: str
    current_group_id: str
    completed_questions: List[str]
    responses: Dict[str, str]  # question_id -> response
    notes: str
    started_at: str
    last_updated_at: str
    completed_at: Optional[str]


class ExportFormat(str, Enum):
    """Supported export formats for workflows."""
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    EMAIL = "email"


class WorkflowManager:
    """Manager for interview workflows."""
    
    def __init__(self, repository, template_manager):
        """
        Initialize the workflow manager.
        
        Args:
            repository: Repository for storage
            template_manager: Template manager instance
        """
        self.repository = repository
        self.template_manager = template_manager
        self.workflows_dir = os.path.join(self.repository.data_dir, DEFAULT_WORKFLOWS_DIR)
        self.sessions_dir = os.path.join(self.repository.data_dir, DEFAULT_SESSIONS_DIR)
        ensure_directory(self.workflows_dir)
        ensure_directory(self.sessions_dir)
        
    def _get_workflow_path(self, workflow_id: str) -> str:
        """Get the file path for a workflow."""
        return os.path.join(self.workflows_dir, f"{workflow_id}.json")
    
    def _get_session_path(self, session_id: str) -> str:
        """Get the file path for a workflow session."""
        return os.path.join(self.sessions_dir, f"{session_id}.json")
    
    def _get_workflows_index_path(self) -> str:
        """Get the file path for the workflows index."""
        return os.path.join(self.workflows_dir, "index.json")
    
    def _update_workflows_index(self, workflow: InterviewWorkflow) -> None:
        """Update the workflows index with basic workflow information."""
        index_path = self._get_workflows_index_path()
        index = read_json(index_path, default={})
        
        index[workflow["id"]] = {
            "id": workflow["id"],
            "name": workflow["name"],
            "description": workflow["description"],
            "niche_id": workflow["niche_id"],
            "template_id": workflow["template_id"],
            "status": workflow["status"],
            "updated_at": workflow["updated_at"]
        }
        
        write_json(index_path, index)
    
    def create_workflow(self, 
                        name: str, 
                        description: str, 
                        niche_id: str, 
                        template_id: str,
                        customizations: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new interview workflow based on a template.
        
        Args:
            name: Workflow name
            description: Workflow description
            niche_id: ID of the niche this workflow is for
            template_id: ID of the template to base the workflow on
            customizations: Optional customizations to apply
            
        Returns:
            ID of the created workflow
            
        Raises:
            ValueError: If template not found or invalid
        """
        # Get the template
        template = self.template_manager.get_template(template_id)
        
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create question groups based on template categories
        question_groups = []
        for i, category in enumerate(template["categories"]):
            question_ids = []
            
            # For each question in the category, create an interview question
            for question in category["questions"]:
                question_text = question["text"]
                question_type = question["type"]
                
                # Create a new interview question
                interview_question = InterviewQuestion(
                    text=question_text,
                    category=category["name"],
                    order=question["order"] if "order" in question else i
                )
                
                # Save the question
                self.repository.save_question(interview_question)
                question_ids.append(interview_question.id)
            
            # Create a question group for this category
            group: WorkflowQuestionGroup = {
                "id": str(uuid.uuid4()),
                "title": category["name"],
                "description": category["description"],
                "questions": question_ids,
                "branches": [],
                "order": category["order"] if "order" in category else i
            }
            
            question_groups.append(group)
        
        # Create the workflow
        workflow: InterviewWorkflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "niche_id": niche_id,
            "template_id": template_id,
            "question_groups": question_groups,
            "created_at": now,
            "updated_at": now,
            "status": WorkflowStatus.DRAFT.value
        }
        
        # Apply customizations if provided
        if customizations:
            self._apply_customizations(workflow, customizations)
        
        # Save the workflow
        workflow_path = self._get_workflow_path(workflow_id)
        success = write_json(workflow_path, workflow)
        
        if not success:
            raise IOError(f"Failed to save workflow: {name}")
        
        # Update the index
        self._update_workflows_index(workflow)
        
        logger.info(f"Created workflow '{name}' with ID {workflow_id}")
        return workflow_id
    
    def _apply_customizations(self, workflow: InterviewWorkflow, customizations: Dict[str, Any]) -> None:
        """
        Apply customizations to a workflow.
        
        Args:
            workflow: Workflow to customize
            customizations: Customization options
        """
        if "groups" in customizations:
            # Customizations for specific groups
            for group_customization in customizations["groups"]:
                group_id = group_customization.get("id")
                group_index = None
                
                # Find the group by ID if provided
                if group_id:
                    for i, group in enumerate(workflow["question_groups"]):
                        if group["id"] == group_id:
                            group_index = i
                            break
                
                # Otherwise use the index
                elif "index" in group_customization:
                    group_index = group_customization["index"]
                
                if group_index is not None and group_index < len(workflow["question_groups"]):
                    group = workflow["question_groups"][group_index]
                    
                    # Update group properties
                    if "title" in group_customization:
                        group["title"] = group_customization["title"]
                    
                    if "description" in group_customization:
                        group["description"] = group_customization["description"]
                    
                    if "order" in group_customization:
                        group["order"] = group_customization["order"]
                    
                    # Add/remove questions
                    if "add_questions" in group_customization:
                        for question in group_customization["add_questions"]:
                            # Create and save a new question
                            interview_question = InterviewQuestion(
                                text=question["text"],
                                category=group["title"],
                                order=question.get("order", len(group["questions"]))
                            )
                            self.repository.save_question(interview_question)
                            group["questions"].append(interview_question.id)
                    
                    if "remove_questions" in group_customization:
                        for question_id in group_customization["remove_questions"]:
                            if question_id in group["questions"]:
                                group["questions"].remove(question_id)
                    
                    # Add branches
                    if "branches" in group_customization:
                        for branch in group_customization["branches"]:
                            new_branch: WorkflowBranch = {
                                "id": str(uuid.uuid4()),
                                "condition": {
                                    "question_id": branch["question_id"],
                                    "operator": branch["operator"],
                                    "value": branch["value"]
                                },
                                "target_group_id": branch["target_group_id"]
                            }
                            group["branches"].append(new_branch)
        
        # Global workflow customizations
        if "name" in customizations:
            workflow["name"] = customizations["name"]
        
        if "description" in customizations:
            workflow["description"] = customizations["description"]
        
        if "status" in customizations:
            workflow["status"] = customizations["status"]
        
        # Update timestamp
        workflow["updated_at"] = datetime.now().isoformat()
    
    def get_workflow(self, workflow_id: str) -> Optional[InterviewWorkflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow to retrieve
            
        Returns:
            Workflow object if found, None otherwise
        """
        try:
            workflow_path = self._get_workflow_path(workflow_id)
            workflow = read_json(workflow_path)
            
            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found")
                return None
                
            return cast(InterviewWorkflow, workflow)
        except Exception as e:
            logger.error(f"Error retrieving workflow {workflow_id}: {str(e)}")
            return None
    
    def list_workflows(self, niche_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all workflows, optionally filtered by niche.
        
        Args:
            niche_id: Optional niche ID to filter by
            
        Returns:
            List of workflow summary dictionaries
        """
        try:
            index_path = self._get_workflows_index_path()
            index = read_json(index_path, default={})
            
            if niche_id:
                return [w for w in index.values() if w["niche_id"] == niche_id]
            else:
                return list(index.values())
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}")
            return []
    
    def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a workflow with new properties.
        
        Args:
            workflow_id: ID of the workflow to update
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.warning(f"Cannot update: Workflow {workflow_id} not found")
            return False
        
        try:
            # Apply updates
            self._apply_customizations(workflow, updates)
            
            # Save the updated workflow
            workflow_path = self._get_workflow_path(workflow_id)
            success = write_json(workflow_path, workflow)
            
            if success:
                # Update the index
                self._update_workflows_index(workflow)
                logger.debug(f"Updated workflow {workflow_id}")
            else:
                logger.error(f"Failed to save updated workflow {workflow_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error updating workflow {workflow_id}: {str(e)}")
            return False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow and its associated sessions.
        
        Args:
            workflow_id: ID of the workflow to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if workflow exists
            workflow_path = self._get_workflow_path(workflow_id)
            if not os.path.exists(workflow_path):
                logger.warning(f"Cannot delete: Workflow {workflow_id} not found")
                return False
            
            # Delete the workflow file
            os.remove(workflow_path)
            
            # Update the index
            index_path = self._get_workflows_index_path()
            index = read_json(index_path, default={})
            if workflow_id in index:
                del index[workflow_id]
                write_json(index_path, index)
            
            # Delete associated sessions
            sessions = self.list_sessions(workflow_id)
            for session in sessions:
                self.delete_session(session["id"])
            
            logger.debug(f"Deleted workflow {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {str(e)}")
            return False
    
    def add_branch(self, 
                  workflow_id: str,
                  group_id: str,
                  question_id: str,
                  operator: str,
                  value: Any,
                  target_group_id: str) -> Optional[str]:
        """
        Add conditional branching to a workflow.
        
        Args:
            workflow_id: ID of the workflow
            group_id: ID of the question group to add the branch to
            question_id: ID of the question that triggers the branch
            operator: Comparison operator for the condition
            value: Value to compare against
            target_group_id: ID of the target question group
            
        Returns:
            ID of the created branch if successful, None otherwise
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.warning(f"Cannot add branch: Workflow {workflow_id} not found")
            return None
        
        # Find the group
        group = None
        for g in workflow["question_groups"]:
            if g["id"] == group_id:
                group = g
                break
        
        if not group:
            logger.warning(f"Cannot add branch: Group {group_id} not found in workflow {workflow_id}")
            return None
        
        # Verify that question exists in the group
        if question_id not in group["questions"]:
            logger.warning(f"Cannot add branch: Question {question_id} not found in group {group_id}")
            return None
        
        # Verify that target group exists
        target_group_exists = False
        for g in workflow["question_groups"]:
            if g["id"] == target_group_id:
                target_group_exists = True
                break
        
        if not target_group_exists:
            logger.warning(f"Cannot add branch: Target group {target_group_id} not found in workflow {workflow_id}")
            return None
        
        # Create the branch
        branch_id = str(uuid.uuid4())
        branch: WorkflowBranch = {
            "id": branch_id,
            "condition": {
                "question_id": question_id,
                "operator": operator,
                "value": value
            },
            "target_group_id": target_group_id
        }
        
        # Add the branch to the group
        group["branches"].append(branch)
        
        # Update the workflow
        workflow["updated_at"] = datetime.now().isoformat()
        workflow_path = self._get_workflow_path(workflow_id)
        success = write_json(workflow_path, workflow)
        
        if success:
            # Update the index
            self._update_workflows_index(workflow)
            logger.debug(f"Added branch {branch_id} to workflow {workflow_id}")
            return branch_id
        else:
            logger.error(f"Failed to save workflow {workflow_id} after adding branch")
            return None
    
    def remove_branch(self, workflow_id: str, group_id: str, branch_id: str) -> bool:
        """
        Remove a branch from a workflow.
        
        Args:
            workflow_id: ID of the workflow
            group_id: ID of the group containing the branch
            branch_id: ID of the branch to remove
            
        Returns:
            True if successful, False otherwise
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.warning(f"Cannot remove branch: Workflow {workflow_id} not found")
            return False
        
        # Find the group
        group = None
        for g in workflow["question_groups"]:
            if g["id"] == group_id:
                group = g
                break
        
        if not group:
            logger.warning(f"Cannot remove branch: Group {group_id} not found in workflow {workflow_id}")
            return False
        
        # Find and remove the branch
        for i, branch in enumerate(group["branches"]):
            if branch["id"] == branch_id:
                group["branches"].pop(i)
                
                # Update the workflow
                workflow["updated_at"] = datetime.now().isoformat()
                workflow_path = self._get_workflow_path(workflow_id)
                success = write_json(workflow_path, workflow)
                
                if success:
                    # Update the index
                    self._update_workflows_index(workflow)
                    logger.debug(f"Removed branch {branch_id} from workflow {workflow_id}")
                    return True
                else:
                    logger.error(f"Failed to save workflow {workflow_id} after removing branch")
                    return False
        
        logger.warning(f"Cannot remove branch: Branch {branch_id} not found in group {group_id}")
        return False
    
    def start_session(self, 
                     workflow_id: str,
                     expert_name: str,
                     expert_role: str,
                     notes: str = "") -> Optional[str]:
        """
        Start a new interview session with this workflow.
        
        Args:
            workflow_id: ID of the workflow
            expert_name: Name of the person being interviewed
            expert_role: Role of the person being interviewed
            notes: Optional initial notes for the session
            
        Returns:
            ID of the created session if successful, None otherwise
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.warning(f"Cannot start session: Workflow {workflow_id} not found")
            return None
        
        # Find the first question group
        if not workflow["question_groups"]:
            logger.warning(f"Cannot start session: Workflow {workflow_id} has no question groups")
            return None
        
        # Sort question groups by order
        question_groups = sorted(workflow["question_groups"], key=lambda g: g["order"])
        first_group = question_groups[0]
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create the session
        session: WorkflowSession = {
            "id": session_id,
            "workflow_id": workflow_id,
            "expert_name": expert_name,
            "expert_role": expert_role,
            "current_group_id": first_group["id"],
            "completed_questions": [],
            "responses": {},
            "notes": notes,
            "started_at": now,
            "last_updated_at": now,
            "completed_at": None
        }
        
        # Save the session
        session_path = self._get_session_path(session_id)
        success = write_json(session_path, session)
        
        if success:
            logger.debug(f"Started session {session_id} for workflow {workflow_id}")
            return session_id
        else:
            logger.error(f"Failed to save session {session_id}")
            return None
    
    def get_session(self, session_id: str) -> Optional[WorkflowSession]:
        """
        Get a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session object if found, None otherwise
        """
        try:
            session_path = self._get_session_path(session_id)
            session = read_json(session_path)
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
                
            return cast(WorkflowSession, session)
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
    
    def list_sessions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sessions, optionally filtered by workflow.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            List of session dictionaries
        """
        try:
            sessions_dir = Path(self.sessions_dir)
            sessions = []
            
            for file_path in sessions_dir.glob("*.json"):
                session = read_json(str(file_path))
                if session and (not workflow_id or session.get("workflow_id") == workflow_id):
                    sessions.append(session)
            
            return sessions
        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            return []
    
    def record_response(self,
                       session_id: str,
                       question_id: str,
                       answer: str,
                       notes: Optional[str] = None) -> bool:
        """
        Record a response to a workflow question.
        
        Args:
            session_id: ID of the session
            question_id: ID of the question being answered
            answer: Response to the question
            notes: Optional notes about the response
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Cannot record response: Session {session_id} not found")
            return False
        
        workflow = self.get_workflow(session["workflow_id"])
        if not workflow:
            logger.warning(f"Cannot record response: Workflow {session['workflow_id']} not found")
            return False
        
        # Find the current group
        current_group = None
        for group in workflow["question_groups"]:
            if group["id"] == session["current_group_id"]:
                current_group = group
                break
        
        if not current_group:
            logger.warning(f"Cannot record response: Current group {session['current_group_id']} not found")
            return False
        
        # Verify that question exists in the current group
        if question_id not in current_group["questions"]:
            logger.warning(f"Cannot record response: Question {question_id} not found in current group")
            return False
        
        # Create a response object
        response = Response(
            answer=answer,
            question_id=question_id,
            interview_id=session_id,
            notes=notes
        )
        
        # Save the response
        response_saved = self.repository.save_response(response)
        if not response_saved:
            logger.error(f"Failed to save response for question {question_id}")
            return False
        
        # Update the session
        session["responses"][question_id] = response.id
        session["completed_questions"].append(question_id)
        session["last_updated_at"] = datetime.now().isoformat()
        
        # Check if we should change groups based on branching logic
        next_group_id = self._check_branching_logic(current_group, question_id, answer)
        if next_group_id:
            session["current_group_id"] = next_group_id
        
        # Check if all questions in the current group are completed
        elif set(current_group["questions"]).issubset(set(session["completed_questions"])):
            # Find the next group in order
            next_group = self._get_next_group(workflow, current_group["order"])
            if next_group:
                session["current_group_id"] = next_group["id"]
            else:
                # If no next group, the workflow is completed
                session["completed_at"] = datetime.now().isoformat()
        
        # Save the updated session
        session_path = self._get_session_path(session_id)
        session_saved = write_json(session_path, session)
        
        if not session_saved:
            logger.error(f"Failed to save session {session_id} after recording response")
            return False
        
        logger.debug(f"Recorded response for question {question_id} in session {session_id}")
        return True
    
    def _check_branching_logic(self, group: WorkflowQuestionGroup, question_id: str, answer: str) -> Optional[str]:
        """
        Check if any branch conditions are met and return the target group ID if so.
        
        Args:
            group: Current question group
            question_id: ID of the answered question
            answer: Response to the question
            
        Returns:
            Target group ID if a branch condition is met, None otherwise
        """
        for branch in group["branches"]:
            condition = branch["condition"]
            if condition["question_id"] != question_id:
                continue
            
            # Check the condition
            if condition["operator"] == "equals" and str(answer) == str(condition["value"]):
                return branch["target_group_id"]
            elif condition["operator"] == "contains" and str(condition["value"]) in str(answer):
                return branch["target_group_id"]
            elif condition["operator"] == "greater_than" and float(answer) > float(condition["value"]):
                return branch["target_group_id"]
            elif condition["operator"] == "less_than" and float(answer) < float(condition["value"]):
                return branch["target_group_id"]
        
        return None
    
    def _get_next_group(self, workflow: InterviewWorkflow, current_order: int) -> Optional[WorkflowQuestionGroup]:
        """
        Get the next group in sequence after the current one.
        
        Args:
            workflow: Current workflow
            current_order: Order of the current group
            
        Returns:
            Next group if found, None otherwise
        """
        # Sort groups by order
        groups = sorted(workflow["question_groups"], key=lambda g: g["order"])
        
        # Find the next group
        for group in groups:
            if group["order"] > current_order:
                return group
        
        return None
    
    def get_next_question(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next question in the workflow based on session state.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Question details if available, None if workflow completed
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Cannot get next question: Session {session_id} not found")
            return None
        
        # If session is completed, return None
        if session["completed_at"]:
            return {
                "completed": True,
                "message": "Interview workflow completed"
            }
        
        workflow = self.get_workflow(session["workflow_id"])
        if not workflow:
            logger.warning(f"Cannot get next question: Workflow {session['workflow_id']} not found")
            return None
        
        # Find the current group
        current_group = None
        for group in workflow["question_groups"]:
            if group["id"] == session["current_group_id"]:
                current_group = group
                break
        
        if not current_group:
            logger.warning(f"Cannot get next question: Current group {session['current_group_id']} not found")
            return None
        
        # Find the first unanswered question in the current group
        for question_id in current_group["questions"]:
            if question_id not in session["completed_questions"]:
                # Get the question details
                question = self.repository.get_question(question_id)
                if question:
                    return {
                        "question_id": question_id,
                        "text": question.text,
                        "category": question.category,
                        "order": question.order,
                        "group_id": current_group["id"],
                        "group_title": current_group["title"],
                        "group_description": current_group["description"],
                        "total_questions": len(current_group["questions"]),
                        "answered_questions": sum(1 for q in current_group["questions"] if q in session["completed_questions"])
                    }
        
        # If all questions in the current group are answered, check if there's a next group
        next_group = self._get_next_group(workflow, current_group["order"])
        if next_group:
            # Update session to move to next group
            session["current_group_id"] = next_group["id"]
            session["last_updated_at"] = datetime.now().isoformat()
            session_path = self._get_session_path(session_id)
            write_json(session_path, session)
            
            # Recurse to get the next question
            return self.get_next_question(session_id)
        else:
            # If no next group, the workflow is completed
            session["completed_at"] = datetime.now().isoformat()
            session_path = self._get_session_path(session_id)
            write_json(session_path, session)
            
            return {
                "completed": True,
                "message": "Interview workflow completed"
            }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Status information including completion percentage
        """
        session = self.get_session(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        workflow = self.get_workflow(session["workflow_id"])
        if not workflow:
            return {"error": f"Workflow {session['workflow_id']} not found"}
        
        # Get all questions in the workflow
        all_questions = []
        for group in workflow["question_groups"]:
            all_questions.extend(group["questions"])
        
        # Calculate completion percentage
        total_questions = len(all_questions)
        answered_questions = len(session["completed_questions"])
        completion_percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        
        # Get current group info
        current_group = None
        for group in workflow["question_groups"]:
            if group["id"] == session["current_group_id"]:
                current_group = group
                break
        
        current_group_info = {
            "id": current_group["id"],
            "title": current_group["title"],
            "description": current_group["description"],
            "total_questions": len(current_group["questions"]) if current_group else 0,
            "answered_questions": sum(1 for q in current_group["questions"] if q in session["completed_questions"]) if current_group else 0
        } if current_group else None
        
        return {
            "session_id": session_id,
            "workflow_id": session["workflow_id"],
            "workflow_name": workflow["name"],
            "expert_name": session["expert_name"],
            "expert_role": session["expert_role"],
            "started_at": session["started_at"],
            "last_updated_at": session["last_updated_at"],
            "completed_at": session["completed_at"],
            "is_completed": session["completed_at"] is not None,
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "completion_percentage": completion_percentage,
            "current_group": current_group_info
        }
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a workflow session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session_path = self._get_session_path(session_id)
            if not os.path.exists(session_path):
                logger.warning(f"Cannot delete: Session {session_id} not found")
                return False
            
            # Delete the session file
            os.remove(session_path)
            logger.debug(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    def preview_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Generate a preview of the workflow.
        
        Args:
            workflow_id: ID of the workflow to preview
            
        Returns:
            Preview data including question groups and branching logic
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        # Gather question details
        questions_map = {}
        for group in workflow["question_groups"]:
            for question_id in group["questions"]:
                question = self.repository.get_question(question_id)
                if question:
                    questions_map[question_id] = {
                        "id": question_id,
                        "text": question.text,
                        "category": question.category,
                        "order": question.order
                    }
        
        # Build group preview data
        groups_preview = []
        for group in sorted(workflow["question_groups"], key=lambda g: g["order"]):
            group_questions = []
            for question_id in group["questions"]:
                if question_id in questions_map:
                    group_questions.append(questions_map[question_id])
            
            # Build branch preview data
            branches_preview = []
            for branch in group["branches"]:
                if branch["condition"]["question_id"] in questions_map:
                    question = questions_map[branch["condition"]["question_id"]]
                    
                    # Find target group
                    target_group_title = "Unknown"
                    for g in workflow["question_groups"]:
                        if g["id"] == branch["target_group_id"]:
                            target_group_title = g["title"]
                            break
                    
                    branches_preview.append({
                        "id": branch["id"],
                        "question_text": question["text"],
                        "operator": branch["condition"]["operator"],
                        "value": branch["condition"]["value"],
                        "target_group": target_group_title
                    })
            
            groups_preview.append({
                "id": group["id"],
                "title": group["title"],
                "description": group["description"],
                "order": group["order"],
                "questions": group_questions,
                "branches": branches_preview
            })
        
        return {
            "id": workflow["id"],
            "name": workflow["name"],
            "description": workflow["description"],
            "status": workflow["status"],
            "groups": groups_preview,
            "created_at": workflow["created_at"],
            "updated_at": workflow["updated_at"]
        }
    
    def export_workflow(self, 
                       workflow_id: str, 
                       format: str = "pdf",
                       output_path: Optional[str] = None) -> str:
        """
        Export a workflow to the specified format.
        
        Args:
            workflow_id: ID of the workflow to export
            format: Export format (pdf, html, markdown, json, email)
            output_path: Optional path for the exported file
            
        Returns:
            Path to the exported file
        """
        # Get workflow preview data
        preview_data = self.preview_workflow(workflow_id)
        if "error" in preview_data:
            raise ValueError(preview_data["error"])
        
        # Determine export format
        export_format = ExportFormat(format.lower()) if format.lower() in [f.value for f in ExportFormat] else ExportFormat.PDF
        
        # Generate default output path if not provided
        if not output_path:
            sanitized_name = preview_data["name"].replace(" ", "_").lower()
            output_dir = os.path.join(self.repository.data_dir, "exports")
            ensure_directory(output_dir)
            output_path = os.path.join(output_dir, f"{sanitized_name}_{workflow_id}.{export_format.value}")
        
        # Export based on format
        if export_format == ExportFormat.JSON:
            # JSON format - simplest case
            return self._export_json(preview_data, output_path)
        elif export_format == ExportFormat.MARKDOWN:
            return self._export_markdown(preview_data, output_path)
        elif export_format == ExportFormat.HTML:
            return self._export_html(preview_data, output_path)
        elif export_format == ExportFormat.EMAIL:
            return self._export_email(preview_data, output_path)
        else:  # Default to PDF
            return self._export_pdf(preview_data, output_path)
    
    def _export_json(self, data: Dict[str, Any], output_path: str) -> str:
        """Export workflow to JSON format."""
        success = write_json(output_path, data)
        if not success:
            raise IOError(f"Failed to export workflow to {output_path}")
        return output_path
    
    def _export_markdown(self, data: Dict[str, Any], output_path: str) -> str:
        """Export workflow to Markdown format."""
        try:
            with open(output_path, 'w') as f:
                # Write header
                f.write(f"# {data['name']}\n\n")
                f.write(f"{data['description']}\n\n")
                f.write(f"Status: {data['status']}\n")
                f.write(f"Created: {data['created_at']}\n")
                f.write(f"Last Updated: {data['updated_at']}\n\n")
                
                # Write question groups
                for group in data['groups']:
                    f.write(f"## {group['title']}\n\n")
                    f.write(f"{group['description']}\n\n")
                    
                    # Write questions
                    f.write("### Questions\n\n")
                    for i, question in enumerate(group['questions']):
                        f.write(f"{i+1}. {question['text']}\n")
                    
                    # Write branches if any
                    if group['branches']:
                        f.write("\n### Branching Logic\n\n")
                        for branch in group['branches']:
                            f.write(f"- If '{branch['question_text']}' {branch['operator']} '{branch['value']}' → Go to '{branch['target_group']}'\n")
                    
                    f.write("\n")
            
            return output_path
        except Exception as e:
            logger.error(f"Error exporting to markdown: {str(e)}")
            raise IOError(f"Failed to export workflow to {output_path}")
    
    def _export_html(self, data: Dict[str, Any], output_path: str) -> str:
        """Export workflow to HTML format."""
        try:
            with open(output_path, 'w') as f:
                # Basic HTML structure
                f.write("<!DOCTYPE html>\n")
                f.write("<html>\n<head>\n")
                f.write(f"<title>{data['name']} - Interview Workflow</title>\n")
                f.write("<style>\n")
                f.write("body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }\n")
                f.write("h1 { color: #333; }\n")
                f.write("h2 { color: #444; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 10px; }\n")
                f.write("h3 { color: #555; }\n")
                f.write(".meta { color: #777; font-size: 0.9em; margin-bottom: 30px; }\n")
                f.write(".question { margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #ccc; }\n")
                f.write(".branch { margin: 5px 0; padding: 8px; background: #f0f8ff; border-left: 4px solid #4682b4; }\n")
                f.write("</style>\n")
                f.write("</head>\n<body>\n")
                
                # Header
                f.write(f"<h1>{data['name']}</h1>\n")
                f.write(f"<p>{data['description']}</p>\n")
                f.write("<div class='meta'>\n")
                f.write(f"<div>Status: {data['status']}</div>\n")
                f.write(f"<div>Created: {data['created_at']}</div>\n")
                f.write(f"<div>Last Updated: {data['updated_at']}</div>\n")
                f.write("</div>\n")
                
                # Groups
                for group in data['groups']:
                    f.write(f"<h2>{group['title']}</h2>\n")
                    f.write(f"<p>{group['description']}</p>\n")
                    
                    # Questions
                    f.write("<h3>Questions</h3>\n")
                    for i, question in enumerate(group['questions']):
                        f.write(f"<div class='question'>{i+1}. {question['text']}</div>\n")
                    
                    # Branches
                    if group['branches']:
                        f.write("<h3>Branching Logic</h3>\n")
                        for branch in group['branches']:
                            f.write("<div class='branch'>")
                            f.write(f"If '{branch['question_text']}' {branch['operator']} '{branch['value']}' → Go to '{branch['target_group']}'")
                            f.write("</div>\n")
                
                f.write("</body>\n</html>")
            
            return output_path
        except Exception as e:
            logger.error(f"Error exporting to HTML: {str(e)}")
            raise IOError(f"Failed to export workflow to {output_path}")
    
    def _export_email(self, data: Dict[str, Any], output_path: str) -> str:
        """Export workflow to email-friendly format (simplified HTML)."""
        try:
            with open(output_path, 'w') as f:
                # Email-friendly HTML
                f.write(f"<h1>{data['name']}</h1>\n")
                f.write(f"<p>{data['description']}</p>\n")
                f.write(f"<p><em>Status: {data['status']}</em></p>\n")
                
                # Groups
                for group in data['groups']:
                    f.write(f"<h2>{group['title']}</h2>\n")
                    f.write(f"<p>{group['description']}</p>\n")
                    
                    # Questions
                    f.write("<ul>\n")
                    for question in group['questions']:
                        f.write(f"<li>{question['text']}</li>\n")
                    f.write("</ul>\n")
            
            return output_path
        except Exception as e:
            logger.error(f"Error exporting to email format: {str(e)}")
            raise IOError(f"Failed to export workflow to {output_path}")
    
    def _export_pdf(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Export workflow to PDF format.
        
        Note: This is a placeholder implementation that actually creates a markdown file
        with instructions to convert to PDF. In a production environment, you'd use a
        library like reportlab, weasyprint, or wkhtmltopdf to generate actual PDFs.
        """
        # Create markdown first
        md_path = output_path.replace('.pdf', '.md')
        self._export_markdown(data, md_path)
        
        # Add PDF conversion instructions
        with open(md_path, 'a') as f:
            f.write("\n\n---\n\n")
            f.write("# PDF Conversion Instructions\n\n")
            f.write("To convert this markdown file to PDF, you can use one of these methods:\n\n")
            f.write("1. Use pandoc: `pandoc -s -o output.pdf this_file.md`\n")
            f.write("2. Use a markdown editor with PDF export capability\n")
            f.write("3. Use an online markdown to PDF converter\n")
        
        logger.warning("PDF export is not fully implemented. Created markdown file with conversion instructions instead.")
        return md_path
    
    def schedule_workflow(self, 
                         workflow_id: str,
                         scheduled_time: datetime,
                         expert_contact: str) -> str:
        """
        Schedule a workflow for a future time.
        
        Args:
            workflow_id: ID of the workflow to schedule
            scheduled_time: When to schedule the interview
            expert_contact: Contact information for the interviewee
            
        Returns:
            ID of the scheduling entry
        """
        # This is a placeholder implementation that creates a scheduling entry
        # In a production environment, you'd integrate with a calendar/scheduling system
        
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        schedule_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        schedule_dir = os.path.join(self.repository.data_dir, "schedules")
        ensure_directory(schedule_dir)
        
        schedule_data = {
            "id": schedule_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "scheduled_time": scheduled_time.isoformat(),
            "expert_contact": expert_contact,
            "created_at": now,
            "status": "scheduled"
        }
        
        schedule_path = os.path.join(schedule_dir, f"{schedule_id}.json")
        success = write_json(schedule_path, schedule_data)
        
        if not success:
            raise IOError(f"Failed to save scheduling entry")
        
        logger.info(f"Scheduled workflow {workflow_id} for {scheduled_time.isoformat()} with expert {expert_contact}")
        return schedule_id 