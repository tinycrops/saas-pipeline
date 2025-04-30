"""
Niche Research Repository

This module provides functions for storing and retrieving niche research data,
including niches, interviews, questions, responses, pain points, and positioning
statements. It leverages the file_io.py utilities for persistence.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set, TypeVar, Generic, Callable

from ..utils.file_io import ensure_directory, read_json, write_json
from .models import (
    Niche, Interview, InterviewQuestion, Response, PainPoint, PositioningStatement,
    NicheDict, InterviewDict, InterviewQuestionDict, ResponseDict, PainPointDict, PositioningStatementDict
)

logger = logging.getLogger(__name__)

# Type variable for generic repository operations
T = TypeVar('T', Niche, Interview, InterviewQuestion, Response, PainPoint, PositioningStatement)

# Default data directory relative to application root
DEFAULT_DATA_DIR = os.environ.get("NICHE_DATA_DIR", "data/niche")


class NicheRepository:
    """Repository for managing niche research data."""
    
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        """
        Initialize the repository with a data directory.
        
        Args:
            data_dir: Directory where data files will be stored
        """
        self.data_dir = data_dir
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for subdir in ["niches", "interviews", "questions", "responses", "pain_points", "positioning"]:
            ensure_directory(os.path.join(self.data_dir, subdir))
    
    def _get_niche_path(self, niche_id: str) -> str:
        """Get the file path for a niche."""
        return os.path.join(self.data_dir, "niches", f"{niche_id}.json")
    
    def _get_interview_path(self, interview_id: str) -> str:
        """Get the file path for an interview."""
        return os.path.join(self.data_dir, "interviews", f"{interview_id}.json")
    
    def _get_question_path(self, question_id: str) -> str:
        """Get the file path for a question."""
        return os.path.join(self.data_dir, "questions", f"{question_id}.json")
    
    def _get_response_path(self, response_id: str) -> str:
        """Get the file path for a response."""
        return os.path.join(self.data_dir, "responses", f"{response_id}.json")
    
    def _get_pain_point_path(self, pain_point_id: str) -> str:
        """Get the file path for a pain point."""
        return os.path.join(self.data_dir, "pain_points", f"{pain_point_id}.json")
    
    def _get_positioning_path(self, positioning_id: str) -> str:
        """Get the file path for a positioning statement."""
        return os.path.join(self.data_dir, "positioning", f"{positioning_id}.json")
    
    def _get_niche_index_path(self) -> str:
        """Get the file path for the niche index."""
        return os.path.join(self.data_dir, "niche_index.json")
    
    def save_niche(self, niche: Niche) -> bool:
        """
        Save a niche to the repository.
        
        Args:
            niche: Niche object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            niche_dict = niche.to_dict()
            file_path = self._get_niche_path(niche.id)
            success = write_json(file_path, niche_dict)
            
            if success:
                # Update niche index
                self._update_niche_index(niche)
                logger.debug(f"Saved niche {niche.id} to {file_path}")
            else:
                logger.error(f"Failed to save niche {niche.id}")
                
            return success
        except Exception as e:
            logger.error(f"Error saving niche {niche.id}: {str(e)}")
            return False
    
    def _update_niche_index(self, niche: Niche):
        """Update the niche index with basic niche information."""
        index_path = self._get_niche_index_path()
        index = read_json(index_path, default={})
        
        index[niche.id] = {
            "id": niche.id,
            "name": niche.name,
            "description": niche.description,
            "updated_at": niche.updated_at.isoformat()
        }
        
        write_json(index_path, index)
    
    def get_niche(self, niche_id: str) -> Optional[Niche]:
        """
        Get a niche by ID.
        
        Args:
            niche_id: ID of the niche to retrieve
            
        Returns:
            Niche object if found, None otherwise
        """
        try:
            file_path = self._get_niche_path(niche_id)
            niche_dict = read_json(file_path)
            
            if not niche_dict:
                logger.warning(f"Niche {niche_id} not found")
                return None
                
            return Niche.from_dict(niche_dict)
        except Exception as e:
            logger.error(f"Error retrieving niche {niche_id}: {str(e)}")
            return None
    
    def get_all_niches(self) -> List[Dict[str, Any]]:
        """
        Get a list of all niches (basic info only, not full niche objects).
        
        Returns:
            List of niche summary dictionaries
        """
        try:
            index_path = self._get_niche_index_path()
            index = read_json(index_path, default={})
            return list(index.values())
        except Exception as e:
            logger.error(f"Error retrieving niche index: {str(e)}")
            return []
    
    def delete_niche(self, niche_id: str) -> bool:
        """
        Delete a niche and its associated data.
        
        Args:
            niche_id: ID of the niche to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get the niche to find associated items
            niche = self.get_niche(niche_id)
            if not niche:
                logger.warning(f"Cannot delete: Niche {niche_id} not found")
                return False
            
            # Delete associated items
            for interview_id in niche.interviews:
                self.delete_interview(interview_id)
                
            for pain_point_id in niche.pain_points:
                self.delete_pain_point(pain_point_id)
                
            for positioning_id in niche.positioning_statements:
                self.delete_positioning_statement(positioning_id)
            
            # Delete the niche file
            file_path = self._get_niche_path(niche_id)
            os.remove(file_path)
            
            # Update the index
            index_path = self._get_niche_index_path()
            index = read_json(index_path, default={})
            if niche_id in index:
                del index[niche_id]
                write_json(index_path, index)
            
            logger.debug(f"Deleted niche {niche_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting niche {niche_id}: {str(e)}")
            return False
    
    def save_interview(self, interview: Interview) -> bool:
        """
        Save an interview to the repository.
        
        Args:
            interview: Interview object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            interview_dict = interview.to_dict()
            file_path = self._get_interview_path(interview.id)
            success = write_json(file_path, interview_dict)
            
            if success:
                # Update the niche with this interview
                niche = self.get_niche(interview.niche_id)
                if niche and interview.id not in niche.interviews:
                    niche.add_interview(interview.id)
                    self.save_niche(niche)
                
                logger.debug(f"Saved interview {interview.id} to {file_path}")
            else:
                logger.error(f"Failed to save interview {interview.id}")
                
            return success
        except Exception as e:
            logger.error(f"Error saving interview {interview.id}: {str(e)}")
            return False
    
    def get_interview(self, interview_id: str) -> Optional[Interview]:
        """
        Get an interview by ID.
        
        Args:
            interview_id: ID of the interview to retrieve
            
        Returns:
            Interview object if found, None otherwise
        """
        try:
            file_path = self._get_interview_path(interview_id)
            interview_dict = read_json(file_path)
            
            if not interview_dict:
                logger.warning(f"Interview {interview_id} not found")
                return None
                
            return Interview.from_dict(interview_dict)
        except Exception as e:
            logger.error(f"Error retrieving interview {interview_id}: {str(e)}")
            return None
    
    def get_interviews_by_niche(self, niche_id: str) -> List[Interview]:
        """
        Get all interviews for a specific niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            List of Interview objects
        """
        try:
            niche = self.get_niche(niche_id)
            if not niche:
                logger.warning(f"Niche {niche_id} not found")
                return []
            
            interviews = []
            for interview_id in niche.interviews:
                interview = self.get_interview(interview_id)
                if interview:
                    interviews.append(interview)
            
            return interviews
        except Exception as e:
            logger.error(f"Error retrieving interviews for niche {niche_id}: {str(e)}")
            return []
    
    def delete_interview(self, interview_id: str) -> bool:
        """
        Delete an interview and its associated responses.
        
        Args:
            interview_id: ID of the interview to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get the interview to find associated items
            interview = self.get_interview(interview_id)
            if not interview:
                logger.warning(f"Cannot delete: Interview {interview_id} not found")
                return False
            
            # Delete associated responses
            for response_id in interview.responses:
                self.delete_response(response_id)
            
            # Remove from niche
            niche = self.get_niche(interview.niche_id)
            if niche and interview_id in niche.interviews:
                niche.interviews.remove(interview_id)
                self.save_niche(niche)
            
            # Delete the interview file
            file_path = self._get_interview_path(interview_id)
            os.remove(file_path)
            
            logger.debug(f"Deleted interview {interview_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting interview {interview_id}: {str(e)}")
            return False
    
    def save_question(self, question: InterviewQuestion) -> bool:
        """
        Save an interview question to the repository.
        
        Args:
            question: InterviewQuestion object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            question_dict = question.to_dict()
            file_path = self._get_question_path(question.id)
            success = write_json(file_path, question_dict)
            
            if success:
                logger.debug(f"Saved question {question.id} to {file_path}")
            else:
                logger.error(f"Failed to save question {question.id}")
                
            return success
        except Exception as e:
            logger.error(f"Error saving question {question.id}: {str(e)}")
            return False
    
    def get_question(self, question_id: str) -> Optional[InterviewQuestion]:
        """
        Get a question by ID.
        
        Args:
            question_id: ID of the question to retrieve
            
        Returns:
            InterviewQuestion object if found, None otherwise
        """
        try:
            file_path = self._get_question_path(question_id)
            question_dict = read_json(file_path)
            
            if not question_dict:
                logger.warning(f"Question {question_id} not found")
                return None
                
            return InterviewQuestion.from_dict(question_dict)
        except Exception as e:
            logger.error(f"Error retrieving question {question_id}: {str(e)}")
            return None
    
    def get_questions_by_category(self, category: str) -> List[InterviewQuestion]:
        """
        Get all questions for a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of InterviewQuestion objects
        """
        try:
            # List all question files
            questions_dir = os.path.join(self.data_dir, "questions")
            questions = []
            
            for file_name in os.listdir(questions_dir):
                if file_name.endswith(".json"):
                    question_id = file_name.replace(".json", "")
                    question = self.get_question(question_id)
                    if question and question.category == category:
                        questions.append(question)
            
            # Sort by order
            questions.sort(key=lambda q: q.order)
            return questions
        except Exception as e:
            logger.error(f"Error retrieving questions for category {category}: {str(e)}")
            return []
    
    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question.
        
        Args:
            question_id: ID of the question to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the question file
            file_path = self._get_question_path(question_id)
            os.remove(file_path)
            
            logger.debug(f"Deleted question {question_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting question {question_id}: {str(e)}")
            return False
    
    def save_response(self, response: Response) -> bool:
        """
        Save a response to the repository.
        
        Args:
            response: Response object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response_dict = response.to_dict()
            file_path = self._get_response_path(response.id)
            success = write_json(file_path, response_dict)
            
            if success:
                # Update the interview with this response
                interview = self.get_interview(response.interview_id)
                if interview and response.id not in interview.responses:
                    interview.add_response(response.id)
                    self.save_interview(interview)
                
                logger.debug(f"Saved response {response.id} to {file_path}")
            else:
                logger.error(f"Failed to save response {response.id}")
                
            return success
        except Exception as e:
            logger.error(f"Error saving response {response.id}: {str(e)}")
            return False
    
    def get_response(self, response_id: str) -> Optional[Response]:
        """
        Get a response by ID.
        
        Args:
            response_id: ID of the response to retrieve
            
        Returns:
            Response object if found, None otherwise
        """
        try:
            file_path = self._get_response_path(response_id)
            response_dict = read_json(file_path)
            
            if not response_dict:
                logger.warning(f"Response {response_id} not found")
                return None
                
            return Response.from_dict(response_dict)
        except Exception as e:
            logger.error(f"Error retrieving response {response_id}: {str(e)}")
            return None
    
    def get_responses_by_interview(self, interview_id: str) -> Dict[str, Response]:
        """
        Get all responses for a specific interview, keyed by question ID.
        
        Args:
            interview_id: ID of the interview
            
        Returns:
            Dictionary of Response objects keyed by question ID
        """
        try:
            interview = self.get_interview(interview_id)
            if not interview:
                logger.warning(f"Interview {interview_id} not found")
                return {}
            
            responses = {}
            for response_id in interview.responses:
                response = self.get_response(response_id)
                if response:
                    responses[response.question_id] = response
            
            return responses
        except Exception as e:
            logger.error(f"Error retrieving responses for interview {interview_id}: {str(e)}")
            return {}
    
    def delete_response(self, response_id: str) -> bool:
        """
        Delete a response.
        
        Args:
            response_id: ID of the response to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get the response to find the associated interview
            response = self.get_response(response_id)
            if not response:
                logger.warning(f"Cannot delete: Response {response_id} not found")
                return False
            
            # Remove from interview
            interview = self.get_interview(response.interview_id)
            if interview and response_id in interview.responses:
                interview.responses.remove(response_id)
                self.save_interview(interview)
            
            # Delete the response file
            file_path = self._get_response_path(response_id)
            os.remove(file_path)
            
            logger.debug(f"Deleted response {response_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting response {response_id}: {str(e)}")
            return False
    
    def save_pain_point(self, pain_point: PainPoint) -> bool:
        """
        Save a pain point to the repository.
        
        Args:
            pain_point: PainPoint object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pain_point_dict = pain_point.to_dict()
            file_path = self._get_pain_point_path(pain_point.id)
            success = write_json(file_path, pain_point_dict)
            
            if success:
                # Update the niche with this pain point
                niche = self.get_niche(pain_point.niche_id)
                if niche and pain_point.id not in niche.pain_points:
                    niche.add_pain_point(pain_point.id)
                    self.save_niche(niche)
                
                logger.debug(f"Saved pain point {pain_point.id} to {file_path}")
            else:
                logger.error(f"Failed to save pain point {pain_point.id}")
                
            return success
        except Exception as e:
            logger.error(f"Error saving pain point {pain_point.id}: {str(e)}")
            return False
    
    def get_pain_point(self, pain_point_id: str) -> Optional[PainPoint]:
        """
        Get a pain point by ID.
        
        Args:
            pain_point_id: ID of the pain point to retrieve
            
        Returns:
            PainPoint object if found, None otherwise
        """
        try:
            file_path = self._get_pain_point_path(pain_point_id)
            pain_point_dict = read_json(file_path)
            
            if not pain_point_dict:
                logger.warning(f"Pain point {pain_point_id} not found")
                return None
                
            return PainPoint.from_dict(pain_point_dict)
        except Exception as e:
            logger.error(f"Error retrieving pain point {pain_point_id}: {str(e)}")
            return None
    
    def get_pain_points_by_niche(self, niche_id: str) -> List[PainPoint]:
        """
        Get all pain points for a specific niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            List of PainPoint objects
        """
        try:
            niche = self.get_niche(niche_id)
            if not niche:
                logger.warning(f"Niche {niche_id} not found")
                return []
            
            pain_points = []
            for pain_point_id in niche.pain_points:
                pain_point = self.get_pain_point(pain_point_id)
                if pain_point:
                    pain_points.append(pain_point)
            
            # Sort by impact * frequency * severity (descending)
            pain_points.sort(key=lambda p: p.impact * p.frequency * p.severity, reverse=True)
            return pain_points
        except Exception as e:
            logger.error(f"Error retrieving pain points for niche {niche_id}: {str(e)}")
            return []
    
    def delete_pain_point(self, pain_point_id: str) -> bool:
        """
        Delete a pain point.
        
        Args:
            pain_point_id: ID of the pain point to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get the pain point to find the associated niche
            pain_point = self.get_pain_point(pain_point_id)
            if not pain_point:
                logger.warning(f"Cannot delete: Pain point {pain_point_id} not found")
                return False
            
            # Remove from niche
            niche = self.get_niche(pain_point.niche_id)
            if niche and pain_point_id in niche.pain_points:
                niche.pain_points.remove(pain_point_id)
                self.save_niche(niche)
            
            # Remove from positioning statements
            for ps_id in self._find_positioning_statements_with_pain_point(pain_point_id):
                ps = self.get_positioning_statement(ps_id)
                if ps and pain_point_id in ps.pain_point_ids:
                    ps.pain_point_ids.remove(pain_point_id)
                    self.save_positioning_statement(ps)
            
            # Delete the pain point file
            file_path = self._get_pain_point_path(pain_point_id)
            os.remove(file_path)
            
            logger.debug(f"Deleted pain point {pain_point_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting pain point {pain_point_id}: {str(e)}")
            return False
    
    def _find_positioning_statements_with_pain_point(self, pain_point_id: str) -> List[str]:
        """Find positioning statements that reference a pain point."""
        result = []
        try:
            # List all positioning statement files
            positioning_dir = os.path.join(self.data_dir, "positioning")
            
            for file_name in os.listdir(positioning_dir):
                if file_name.endswith(".json"):
                    ps_id = file_name.replace(".json", "")
                    ps = self.get_positioning_statement(ps_id)
                    if ps and pain_point_id in ps.pain_point_ids:
                        result.append(ps_id)
            
            return result
        except Exception as e:
            logger.error(f"Error finding positioning statements with pain point {pain_point_id}: {str(e)}")
            return []
    
    def save_positioning_statement(self, positioning: PositioningStatement) -> bool:
        """
        Save a positioning statement to the repository.
        
        Args:
            positioning: PositioningStatement object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            positioning_dict = positioning.to_dict()
            file_path = self._get_positioning_path(positioning.id)
            success = write_json(file_path, positioning_dict)
            
            if success:
                # Update the niche with this positioning statement
                niche = self.get_niche(positioning.niche_id)
                if niche and positioning.id not in niche.positioning_statements:
                    niche.add_positioning_statement(positioning.id)
                    self.save_niche(niche)
                
                logger.debug(f"Saved positioning statement {positioning.id} to {file_path}")
            else:
                logger.error(f"Failed to save positioning statement {positioning.id}")
                
            return success
        except Exception as e:
            logger.error(f"Error saving positioning statement {positioning.id}: {str(e)}")
            return False
    
    def get_positioning_statement(self, positioning_id: str) -> Optional[PositioningStatement]:
        """
        Get a positioning statement by ID.
        
        Args:
            positioning_id: ID of the positioning statement to retrieve
            
        Returns:
            PositioningStatement object if found, None otherwise
        """
        try:
            file_path = self._get_positioning_path(positioning_id)
            positioning_dict = read_json(file_path)
            
            if not positioning_dict:
                logger.warning(f"Positioning statement {positioning_id} not found")
                return None
                
            return PositioningStatement.from_dict(positioning_dict)
        except Exception as e:
            logger.error(f"Error retrieving positioning statement {positioning_id}: {str(e)}")
            return None
    
    def get_positioning_statements_by_niche(self, niche_id: str) -> List[PositioningStatement]:
        """
        Get all positioning statements for a specific niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            List of PositioningStatement objects
        """
        try:
            niche = self.get_niche(niche_id)
            if not niche:
                logger.warning(f"Niche {niche_id} not found")
                return []
            
            statements = []
            for ps_id in niche.positioning_statements:
                statement = self.get_positioning_statement(ps_id)
                if statement:
                    statements.append(statement)
            
            return statements
        except Exception as e:
            logger.error(f"Error retrieving positioning statements for niche {niche_id}: {str(e)}")
            return []
    
    def delete_positioning_statement(self, positioning_id: str) -> bool:
        """
        Delete a positioning statement.
        
        Args:
            positioning_id: ID of the positioning statement to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get the positioning statement to find the associated niche
            positioning = self.get_positioning_statement(positioning_id)
            if not positioning:
                logger.warning(f"Cannot delete: Positioning statement {positioning_id} not found")
                return False
            
            # Remove from niche
            niche = self.get_niche(positioning.niche_id)
            if niche and positioning_id in niche.positioning_statements:
                niche.positioning_statements.remove(positioning_id)
                self.save_niche(niche)
            
            # Delete the positioning statement file
            file_path = self._get_positioning_path(positioning_id)
            os.remove(file_path)
            
            logger.debug(f"Deleted positioning statement {positioning_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting positioning statement {positioning_id}: {str(e)}")
            return False 