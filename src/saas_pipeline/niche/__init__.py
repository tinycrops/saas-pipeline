"""
Niche Research Module

This module provides functionality for identifying pain points in chosen niches
and generating positioning statements based on interview data.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from .models import (
    Niche, Interview, InterviewQuestion, Response, PainPoint, PositioningStatement
)
from .repository import NicheRepository
from .template import TemplateManager, QuestionType, QuestionTemplate, TemplateCategory

logger = logging.getLogger(__name__)


class NicheResearchModule:
    """
    Module for niche research functionality, including interview workflows
    and positioning statement generation.
    """
    
    def __init__(self, openai_client):
        """
        Initialize the niche research module.
        
        Args:
            openai_client: OpenAI client for AI-powered analysis
        """
        self.openai_client = openai_client
        self.repository = NicheRepository()
        self.template_manager = TemplateManager(self.repository.data_dir)
        
    def analyze_niche(self, niche_name: str) -> Dict[str, Any]:
        """
        Analyze a niche and return structured data.
        
        Args:
            niche_name: Name of the niche to analyze
            
        Returns:
            Dictionary with niche analysis data
        """
        # This is a placeholder that will be fully implemented in future tasks
        # For now, it returns a simple structure
        
        # Create a new niche
        niche = Niche(
            name=niche_name,
            description=f"Analysis of {niche_name} market"
        )
        
        # Save the niche
        self.repository.save_niche(niche)
        
        # Return basic niche data
        return {
            "id": niche.id,
            "name": niche.name,
            "description": niche.description,
            "created_at": niche.created_at.isoformat(),
            "interviews": [],
            "pain_points": [],
            "positioning_statements": []
        }
    
    def create_interview_template(self, niche_id: str, categories: List[str]) -> List[InterviewQuestion]:
        """
        Create a template of interview questions for a niche.
        
        Args:
            niche_id: ID of the niche
            categories: List of question categories to include
            
        Returns:
            List of created InterviewQuestion objects
        """
        # This is a placeholder that will be fully implemented in future tasks
        # For now, it creates some example questions
        
        questions = []
        order = 0
        
        for category in categories:
            if category == "demographics":
                questions.append(InterviewQuestion(
                    text="How long have you been working in this field?",
                    category=category,
                    order=order
                ))
                order += 1
                questions.append(InterviewQuestion(
                    text="What is your primary role or responsibility?",
                    category=category,
                    order=order
                ))
                order += 1
            
            elif category == "pain_points":
                questions.append(InterviewQuestion(
                    text="What are your most time-consuming, recurring tasks?",
                    category=category,
                    order=order
                ))
                order += 1
                questions.append(InterviewQuestion(
                    text="Where do you spend the most money in your workflow?",
                    category=category,
                    order=order
                ))
                order += 1
                questions.append(InterviewQuestion(
                    text="What do you wish you could automate or simplify?",
                    category=category,
                    order=order
                ))
                order += 1
            
            elif category == "solutions":
                questions.append(InterviewQuestion(
                    text="What tools or methods do you currently use to address these challenges?",
                    category=category,
                    order=order
                ))
                order += 1
                questions.append(InterviewQuestion(
                    text="What would an ideal solution look like to you?",
                    category=category,
                    order=order
                ))
                order += 1
        
        # Save all questions
        for question in questions:
            self.repository.save_question(question)
        
        return questions
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        List all available interview templates.
        
        Returns:
            List of template metadata
        """
        return self.template_manager.list_templates()
    
    def get_template(self, template_id: str, version: Optional[str] = None) -> QuestionTemplate:
        """
        Get a specific interview template.
        
        Args:
            template_id: ID of the template
            version: Optional version of the template
            
        Returns:
            Complete template object
        """
        return self.template_manager.get_template(template_id, version)
    
    def create_template(self, 
                        name: str, 
                        description: str, 
                        niche_type: str,
                        categories: Optional[List[TemplateCategory]] = None) -> str:
        """
        Create a new interview template.
        
        Args:
            name: Name of the template
            description: Description of the template
            niche_type: Type of niche the template is for
            categories: Optional initial categories
            
        Returns:
            ID of the created template
        """
        return self.template_manager.create_template(
            name=name,
            description=description,
            niche_type=niche_type,
            categories=categories
        )
    
    def add_template_category(self,
                             template_id: str,
                             name: str,
                             description: str,
                             order: Optional[int] = None) -> str:
        """
        Add a category to a template.
        
        Args:
            template_id: ID of the template
            name: Name of the category
            description: Description of the category
            order: Optional order of the category
            
        Returns:
            ID of the created category
        """
        return self.template_manager.add_category(
            template_id=template_id,
            name=name,
            description=description,
            order=order
        )
    
    def add_template_question(self,
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
            category_id: ID of the category
            text: Question text
            question_type: Type of question
            options: Options for multiple choice questions
            required: Whether the question is required
            default_value: Optional default value
            order: Optional order of the question
            
        Returns:
            ID of the created question
        """
        return self.template_manager.add_question(
            template_id=template_id,
            category_id=category_id,
            text=text,
            question_type=question_type,
            options=options,
            required=required,
            default_value=default_value,
            order=order
        )
    
    def update_template(self,
                       template_id: str,
                       updates: Dict[str, Any],
                       create_new_version: bool = False,
                       version_notes: str = "") -> QuestionTemplate:
        """
        Update a template, optionally creating a new version.
        
        Args:
            template_id: ID of the template to update
            updates: Dictionary of updates to apply
            create_new_version: Whether to create a new version
            version_notes: Notes about the changes
            
        Returns:
            Updated template object
        """
        return self.template_manager.update_template(
            template_id=template_id,
            updates=updates,
            create_new_version=create_new_version,
            version_notes=version_notes
        )
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            True if successful, False otherwise
        """
        return self.template_manager.delete_template(template_id)
    
    def export_template(self, template_id: str, export_path: str) -> bool:
        """
        Export a template to a file.
        
        Args:
            template_id: ID of the template to export
            export_path: Path to export the template to
            
        Returns:
            True if successful, False otherwise
        """
        return self.template_manager.export_template(template_id, export_path)
    
    def import_template(self, import_path: str) -> Optional[str]:
        """
        Import a template from a file.
        
        Args:
            import_path: Path to import the template from
            
        Returns:
            ID of the imported template if successful, None otherwise
        """
        return self.template_manager.import_template(import_path)
    
    def create_interview(self, niche_id: str, expert_name: str, role: str) -> Interview:
        """
        Create a new interview for a niche expert.
        
        Args:
            niche_id: ID of the niche
            expert_name: Name of the expert being interviewed
            role: Role of the expert in the niche
            
        Returns:
            Created Interview object
        """
        interview = Interview(
            expert_name=expert_name,
            niche_id=niche_id,
            role=role
        )
        
        self.repository.save_interview(interview)
        return interview
    
    def add_interview_questions(self, interview_id: str, question_ids: List[str]) -> bool:
        """
        Add questions to an interview.
        
        Args:
            interview_id: ID of the interview
            question_ids: List of question IDs to add
            
        Returns:
            True if successful, False otherwise
        """
        interview = self.repository.get_interview(interview_id)
        if not interview:
            logger.error(f"Interview {interview_id} not found")
            return False
        
        for question_id in question_ids:
            interview.add_question(question_id)
        
        return self.repository.save_interview(interview)
    
    def add_response(self, interview_id: str, question_id: str, answer: str, notes: Optional[str] = None) -> Response:
        """
        Add a response to an interview question.
        
        Args:
            interview_id: ID of the interview
            question_id: ID of the question being answered
            answer: The response text
            notes: Optional additional notes
            
        Returns:
            Created Response object
        """
        response = Response(
            answer=answer,
            question_id=question_id,
            interview_id=interview_id,
            notes=notes
        )
        
        self.repository.save_response(response)
        return response
    
    def extract_pain_points(self, niche_id: str) -> List[PainPoint]:
        """
        Extract pain points from interview responses.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            List of identified pain points
        """
        # This is a placeholder that will be implemented with AI analysis in future tasks
        # For now, it returns an empty list
        return []
    
    def generate_positioning_statement(self, niche_id: str, pain_point_ids: List[str]) -> PositioningStatement:
        """
        Generate a positioning statement for a niche based on pain points.
        
        Args:
            niche_id: ID of the niche
            pain_point_ids: List of pain point IDs to include in the statement
            
        Returns:
            Generated PositioningStatement object
        """
        # This is a placeholder that will be fully implemented in future tasks
        
        niche = self.repository.get_niche(niche_id)
        if not niche:
            raise ValueError(f"Niche {niche_id} not found")
        
        # Simple template-based statement for now
        statement = f"I help {niche.name} do [painful thing] in 10 minutes instead of 10 hours."
        
        positioning = PositioningStatement(
            statement=statement,
            target_audience=niche.name,
            niche_id=niche_id,
            pain_point_ids=pain_point_ids
        )
        
        self.repository.save_positioning_statement(positioning)
        return positioning
    
    def generate_interview_from_template(self, niche_id: str, template_id: str, expert_name: str, role: str) -> Dict[str, Any]:
        """
        Generate an interview with questions based on a template.
        
        Args:
            niche_id: ID of the niche
            template_id: ID of the template to use
            expert_name: Name of the expert being interviewed
            role: Role of the expert in the niche
            
        Returns:
            Dictionary with interview and question data
        """
        # Get the template
        template = self.template_manager.get_template(template_id)
        
        # Create a new interview
        interview = self.create_interview(niche_id, expert_name, role)
        
        # Create questions for each template question
        question_map = {}  # Map template question IDs to created question IDs
        
        for category in template["categories"]:
            for template_question in category["questions"]:
                # Create a new question from the template
                question = InterviewQuestion(
                    text=template_question["text"],
                    category=category["name"],
                    order=template_question["order"]
                )
                
                # Save the question
                self.repository.save_question(question)
                
                # Add to interview
                interview.add_question(question.id)
                
                # Map template question ID to created question ID
                question_map[template_question["id"]] = question.id
        
        # Save the updated interview
        self.repository.save_interview(interview)
        
        # Return the result
        return {
            "interview": interview.to_dict(),
            "question_map": question_map
        } 