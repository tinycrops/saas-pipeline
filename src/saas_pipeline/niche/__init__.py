"""
Niche Research Module

This module provides functionality for niche research, including data models,
repository, interview workflows, pain point analysis, and positioning statement generation.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .models import (
    Niche, Interview, InterviewQuestion, Response, PainPoint, PositioningStatement
)
from .repository import NicheRepository
from .template import TemplateManager, QuestionType, QuestionTemplate, TemplateCategory, create_default_templates
from .workflow import WorkflowManager, InterviewWorkflow, WorkflowSession, ExportFormat
from .pain_points import (
    PainPointAnalyzer, 
    PainPointVisualizer,
    extract_pain_points_from_response,
    analyze_niche_pain_points
)
from .positioning import (
    PositioningGenerator,
    generate_positioning_statement,
    create_ab_test_for_niche
)

logger = logging.getLogger(__name__)


class NicheResearchModule:
    """Main class for niche research functionality."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the niche research module.
        
        Args:
            data_dir: Directory for data storage (if None, uses default)
        """
        self.repository = NicheRepository(data_dir)
        self.template_manager = TemplateManager(self.repository)
        self.workflow_manager = WorkflowManager(self.repository, self.template_manager)
        self.pain_point_analyzer = PainPointAnalyzer(self.repository)
        self.pain_point_visualizer = PainPointVisualizer(self.repository)
        self.positioning_generator = PositioningGenerator(self.repository)
    
    # Niche operations
    def create_niche(self, name: str, description: str, target_audience: str = None,
                  market_size: str = None, competition: str = None) -> str:
        """
        Create a new niche.
        
        Args:
            name: Name of the niche
            description: Description of the niche
            target_audience: Target audience (optional)
            market_size: Market size information (optional)
            competition: Competition information (optional)
            
        Returns:
            ID of the created niche
        """
        niche = Niche(
            name=name,
            description=description,
            target_audience=target_audience,
            market_size=market_size,
            competition=competition
        )
        
        success = self.repository.save_niche(niche)
        if not success:
            raise RuntimeError(f"Failed to save niche: {name}")
        
        return niche.id
    
    def get_niche(self, niche_id: str) -> Niche:
        """
        Get a niche by ID.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            Niche object
        """
        niche = self.repository.get_niche(niche_id)
        if not niche:
            raise ValueError(f"Niche not found: {niche_id}")
        
        return niche
    
    def get_all_niches(self) -> list:
        """
        Get all niches.
        
        Returns:
            List of niche summary dictionaries
        """
        return self.repository.get_all_niches()
    
    def delete_niche(self, niche_id: str) -> bool:
        """
        Delete a niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            True if successful, False otherwise
        """
        return self.repository.delete_niche(niche_id)
    
    # Interview operations
    def create_interview(self, niche_id: str, expert_name: str, role: str = "",
                      contact_info: str = None) -> str:
        """
        Create a new interview.
        
        Args:
            niche_id: ID of the niche
            expert_name: Name of the expert
            role: Role of the expert (optional)
            contact_info: Contact information (optional)
            
        Returns:
            ID of the created interview
        """
        interview = Interview(
            expert_name=expert_name,
            niche_id=niche_id,
            role=role,
            contact_info=contact_info
        )
        
        success = self.repository.save_interview(interview)
        if not success:
            raise RuntimeError(f"Failed to save interview for: {expert_name}")
        
        return interview.id
    
    def get_interview(self, interview_id: str) -> Interview:
        """
        Get an interview by ID.
        
        Args:
            interview_id: ID of the interview
            
        Returns:
            Interview object
        """
        interview = self.repository.get_interview(interview_id)
        if not interview:
            raise ValueError(f"Interview not found: {interview_id}")
        
        return interview
    
    def get_interviews_by_niche(self, niche_id: str) -> list:
        """
        Get interviews for a niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            List of interview objects
        """
        return self.repository.get_interviews_by_niche(niche_id)
    
    def add_response(self, interview_id: str, question_id: str, answer: str, notes: str = None) -> str:
        """
        Add a response to an interview.
        
        Args:
            interview_id: ID of the interview
            question_id: ID of the question
            answer: Answer text
            notes: Additional notes (optional)
            
        Returns:
            ID of the created response
        """
        response = Response(
            answer=answer,
            question_id=question_id,
            interview_id=interview_id,
            notes=notes
        )
        
        success = self.repository.save_response(response)
        if not success:
            raise RuntimeError(f"Failed to save response")
        
        interview = self.repository.get_interview(interview_id)
        if interview:
            interview.add_response(response.id)
            self.repository.save_interview(interview)
        
        return response.id
    
    # Template operations
    def create_template(self, name: str, description: str, niche_type: str) -> str:
        """
        Create a new template.
        
        Args:
            name: Name of the template
            description: Description of the template
            niche_type: Type of niche the template is for
            
        Returns:
            ID of the created template
        """
        return self.template_manager.create_template(name, description, niche_type)
    
    def get_template(self, template_id: str) -> dict:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Template dictionary
        """
        return self.template_manager.get_template(template_id)
    
    def get_all_templates(self) -> list:
        """
        Get all templates.
        
        Returns:
            List of template summary dictionaries
        """
        return self.template_manager.get_all_templates()
    
    def init_default_templates(self) -> list:
        """
        Initialize default templates.
        
        Returns:
            List of created template IDs
        """
        return create_default_templates(self.template_manager)
    
    # Workflow operations
    def create_workflow(self, name: str, description: str, niche_id: str, template_id: str) -> str:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            niche_id: ID of the niche
            template_id: ID of the template
            
        Returns:
            ID of the created workflow
        """
        return self.workflow_manager.create_workflow(name, description, niche_id, template_id)
    
    def get_workflow(self, workflow_id: str) -> dict:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow dictionary
        """
        return self.workflow_manager.get_workflow(workflow_id)
    
    def start_session(self, workflow_id: str, expert_name: str, expert_role: str) -> str:
        """
        Start a new workflow session.
        
        Args:
            workflow_id: ID of the workflow
            expert_name: Name of the expert
            expert_role: Role of the expert
            
        Returns:
            ID of the created session
        """
        return self.workflow_manager.start_session(workflow_id, expert_name, expert_role)
    
    # Pain point operations
    def extract_pain_points(self, interview_id: str) -> list:
        """
        Extract pain points from an interview.
        
        Args:
            interview_id: ID of the interview
            
        Returns:
            List of potential pain points
        """
        return self.pain_point_analyzer.extract_pain_points_from_interview(interview_id)
    
    def create_pain_points(self, niche_id: str, threshold: float = 0.0) -> list:
        """
        Create pain points for a niche based on interviews.
        
        Args:
            niche_id: ID of the niche
            threshold: Minimum score threshold (0.0-5.0)
            
        Returns:
            List of created pain point IDs
        """
        return self.pain_point_analyzer.create_pain_points_for_niche(niche_id, threshold)
    
    def analyze_pain_points(self, niche_id: str) -> dict:
        """
        Analyze pain points for a niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            Dictionary of analysis results
        """
        return self.pain_point_analyzer.analyze_pain_points(niche_id)
    
    def generate_pain_point_report(self, niche_id: str) -> dict:
        """
        Generate a comprehensive pain point report.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            Dictionary with report data
        """
        return self.pain_point_visualizer.export_pain_point_report(niche_id)
    
    # Positioning operations
    def generate_positioning(self, niche_id: str, product_name: str, 
                           tone: str = "professional",
                           competitor: str = None,
                           num_variations: int = 3) -> list:
        """
        Generate positioning statements for a niche.
        
        Args:
            niche_id: ID of the niche
            product_name: Name of the product
            tone: Tone for the statement
            competitor: Main competitor name (optional)
            num_variations: Number of variations to generate
            
        Returns:
            List of positioning statement dictionaries
        """
        return self.positioning_generator.generate_positioning_for_niche(
            niche_id, product_name, tone, competitor, num_variations
        )
    
    def create_ab_test(self, niche_id: str, product_name: str, num_variations: int = 2) -> dict:
        """
        Create an A/B test with multiple positioning statement variations.
        
        Args:
            niche_id: ID of the niche
            product_name: Name of the product
            num_variations: Number of variations to test
            
        Returns:
            Dictionary with A/B test data
        """
        return self.positioning_generator.create_ab_test(niche_id, product_name, num_variations)
    
    def refine_positioning(self, positioning_id: str, feedback: str) -> dict:
        """
        Refine a positioning statement based on feedback.
        
        Args:
            positioning_id: ID of the positioning statement
            feedback: Feedback text
            
        Returns:
            Dictionary with refined positioning data
        """
        result = self.positioning_generator.refine_positioning(positioning_id, feedback)
        if not result:
            raise ValueError(f"Failed to refine positioning statement: {positioning_id}")
        return result

# Create default instance
niche_research = NicheResearchModule() 