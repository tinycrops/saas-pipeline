"""
Tests for niche research repository.
"""

import os
import unittest
import tempfile
import shutil
from datetime import datetime

from src.saas_pipeline.niche.models import (
    Niche, Interview, InterviewQuestion, Response, PainPoint, PositioningStatement
)
from src.saas_pipeline.niche.repository import NicheRepository


class TestNicheRepository(unittest.TestCase):
    """Test cases for the NicheRepository."""
    
    def setUp(self):
        """Set up a temporary directory for test data."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = NicheRepository(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_get_niche(self):
        """Test saving and retrieving a niche."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        # Save the niche
        success = self.repo.save_niche(niche)
        self.assertTrue(success)
        
        # Check if the file was created
        niche_path = os.path.join(self.temp_dir, "niches", f"{niche.id}.json")
        self.assertTrue(os.path.exists(niche_path))
        
        # Check if the index was updated
        index_path = os.path.join(self.temp_dir, "niche_index.json")
        self.assertTrue(os.path.exists(index_path))
        
        # Retrieve the niche
        retrieved_niche = self.repo.get_niche(niche.id)
        self.assertIsNotNone(retrieved_niche)
        self.assertEqual(retrieved_niche.id, niche.id)
        self.assertEqual(retrieved_niche.name, niche.name)
        self.assertEqual(retrieved_niche.description, niche.description)
    
    def test_get_all_niches(self):
        """Test retrieving all niches."""
        # Create and save multiple niches
        niche1 = Niche(name="Niche 1", description="Description 1")
        niche2 = Niche(name="Niche 2", description="Description 2")
        niche3 = Niche(name="Niche 3", description="Description 3")
        
        self.repo.save_niche(niche1)
        self.repo.save_niche(niche2)
        self.repo.save_niche(niche3)
        
        # Get all niches
        niches = self.repo.get_all_niches()
        self.assertEqual(len(niches), 3)
        
        # Check if all niches are included
        niche_ids = [niche["id"] for niche in niches]
        self.assertIn(niche1.id, niche_ids)
        self.assertIn(niche2.id, niche_ids)
        self.assertIn(niche3.id, niche_ids)
    
    def test_save_and_get_interview(self):
        """Test saving and retrieving an interview."""
        # Create a niche first
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        # Create an interview
        interview = Interview(
            expert_name="John Doe",
            niche_id=niche.id,
            role="Marketing Consultant"
        )
        
        # Save the interview
        success = self.repo.save_interview(interview)
        self.assertTrue(success)
        
        # Check if the file was created
        interview_path = os.path.join(self.temp_dir, "interviews", f"{interview.id}.json")
        self.assertTrue(os.path.exists(interview_path))
        
        # Retrieve the interview
        retrieved_interview = self.repo.get_interview(interview.id)
        self.assertIsNotNone(retrieved_interview)
        self.assertEqual(retrieved_interview.id, interview.id)
        self.assertEqual(retrieved_interview.expert_name, interview.expert_name)
        self.assertEqual(retrieved_interview.niche_id, interview.niche_id)
        
        # Check if the interview was added to the niche
        updated_niche = self.repo.get_niche(niche.id)
        self.assertIn(interview.id, updated_niche.interviews)
    
    def test_get_interviews_by_niche(self):
        """Test retrieving interviews by niche."""
        # Create a niche
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        # Create and save interviews
        interview1 = Interview(expert_name="Expert 1", niche_id=niche.id)
        interview2 = Interview(expert_name="Expert 2", niche_id=niche.id)
        interview3 = Interview(expert_name="Expert 3", niche_id=niche.id)
        
        self.repo.save_interview(interview1)
        self.repo.save_interview(interview2)
        self.repo.save_interview(interview3)
        
        # Get interviews by niche
        interviews = self.repo.get_interviews_by_niche(niche.id)
        self.assertEqual(len(interviews), 3)
        
        # Check if all interviews are included
        interview_ids = [interview.id for interview in interviews]
        self.assertIn(interview1.id, interview_ids)
        self.assertIn(interview2.id, interview_ids)
        self.assertIn(interview3.id, interview_ids)
    
    def test_save_and_get_question(self):
        """Test saving and retrieving a question."""
        # Create a question
        question = InterviewQuestion(
            text="What are your most time-consuming tasks?",
            category="pain_points",
            order=1
        )
        
        # Save the question
        success = self.repo.save_question(question)
        self.assertTrue(success)
        
        # Check if the file was created
        question_path = os.path.join(self.temp_dir, "questions", f"{question.id}.json")
        self.assertTrue(os.path.exists(question_path))
        
        # Retrieve the question
        retrieved_question = self.repo.get_question(question.id)
        self.assertIsNotNone(retrieved_question)
        self.assertEqual(retrieved_question.id, question.id)
        self.assertEqual(retrieved_question.text, question.text)
        self.assertEqual(retrieved_question.category, question.category)
        self.assertEqual(retrieved_question.order, question.order)
    
    def test_get_questions_by_category(self):
        """Test retrieving questions by category."""
        # Create and save questions in different categories
        q1 = InterviewQuestion(text="Question 1", category="category1", order=1)
        q2 = InterviewQuestion(text="Question 2", category="category1", order=2)
        q3 = InterviewQuestion(text="Question 3", category="category2", order=1)
        q4 = InterviewQuestion(text="Question 4", category="category2", order=2)
        q5 = InterviewQuestion(text="Question 5", category="category3", order=1)
        
        self.repo.save_question(q1)
        self.repo.save_question(q2)
        self.repo.save_question(q3)
        self.repo.save_question(q4)
        self.repo.save_question(q5)
        
        # Get questions by category
        category1_questions = self.repo.get_questions_by_category("category1")
        category2_questions = self.repo.get_questions_by_category("category2")
        category3_questions = self.repo.get_questions_by_category("category3")
        
        self.assertEqual(len(category1_questions), 2)
        self.assertEqual(len(category2_questions), 2)
        self.assertEqual(len(category3_questions), 1)
        
        # Check if questions are in the correct order
        self.assertEqual(category1_questions[0].id, q1.id)
        self.assertEqual(category1_questions[1].id, q2.id)
    
    def test_save_and_get_response(self):
        """Test saving and retrieving a response."""
        # Create a niche, interview, and question first
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        interview = Interview(expert_name="John Doe", niche_id=niche.id)
        self.repo.save_interview(interview)
        
        question = InterviewQuestion(text="Test Question", category="category")
        self.repo.save_question(question)
        
        # Add the question to the interview
        interview.add_question(question.id)
        self.repo.save_interview(interview)
        
        # Create a response
        response = Response(
            answer="This is my answer",
            question_id=question.id,
            interview_id=interview.id,
            notes="Additional notes"
        )
        
        # Save the response
        success = self.repo.save_response(response)
        self.assertTrue(success)
        
        # Check if the file was created
        response_path = os.path.join(self.temp_dir, "responses", f"{response.id}.json")
        self.assertTrue(os.path.exists(response_path))
        
        # Retrieve the response
        retrieved_response = self.repo.get_response(response.id)
        self.assertIsNotNone(retrieved_response)
        self.assertEqual(retrieved_response.id, response.id)
        self.assertEqual(retrieved_response.answer, response.answer)
        self.assertEqual(retrieved_response.question_id, response.question_id)
        self.assertEqual(retrieved_response.interview_id, response.interview_id)
        self.assertEqual(retrieved_response.notes, response.notes)
        
        # Check if the response was added to the interview
        updated_interview = self.repo.get_interview(interview.id)
        self.assertIn(response.id, updated_interview.responses)
    
    def test_get_responses_by_interview(self):
        """Test retrieving responses by interview."""
        # Create a niche, interview, and questions
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        interview = Interview(expert_name="John Doe", niche_id=niche.id)
        self.repo.save_interview(interview)
        
        q1 = InterviewQuestion(text="Question 1", category="category1")
        q2 = InterviewQuestion(text="Question 2", category="category1")
        q3 = InterviewQuestion(text="Question 3", category="category2")
        
        self.repo.save_question(q1)
        self.repo.save_question(q2)
        self.repo.save_question(q3)
        
        # Add questions to the interview
        interview.add_question(q1.id)
        interview.add_question(q2.id)
        interview.add_question(q3.id)
        self.repo.save_interview(interview)
        
        # Create and save responses
        r1 = Response(answer="Answer 1", question_id=q1.id, interview_id=interview.id)
        r2 = Response(answer="Answer 2", question_id=q2.id, interview_id=interview.id)
        r3 = Response(answer="Answer 3", question_id=q3.id, interview_id=interview.id)
        
        self.repo.save_response(r1)
        self.repo.save_response(r2)
        self.repo.save_response(r3)
        
        # Get responses by interview
        responses = self.repo.get_responses_by_interview(interview.id)
        self.assertEqual(len(responses), 3)
        
        # Check if responses are correctly mapped to questions
        self.assertEqual(responses[q1.id].answer, "Answer 1")
        self.assertEqual(responses[q2.id].answer, "Answer 2")
        self.assertEqual(responses[q3.id].answer, "Answer 3")
    
    def test_save_and_get_pain_point(self):
        """Test saving and retrieving a pain point."""
        # Create a niche first
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        # Create a pain point
        pain_point = PainPoint(
            description="Time-consuming email list management",
            niche_id=niche.id,
            severity=4,
            frequency=5,
            impact=3
        )
        
        # Save the pain point
        success = self.repo.save_pain_point(pain_point)
        self.assertTrue(success)
        
        # Check if the file was created
        pain_point_path = os.path.join(self.temp_dir, "pain_points", f"{pain_point.id}.json")
        self.assertTrue(os.path.exists(pain_point_path))
        
        # Retrieve the pain point
        retrieved_pain_point = self.repo.get_pain_point(pain_point.id)
        self.assertIsNotNone(retrieved_pain_point)
        self.assertEqual(retrieved_pain_point.id, pain_point.id)
        self.assertEqual(retrieved_pain_point.description, pain_point.description)
        self.assertEqual(retrieved_pain_point.severity, pain_point.severity)
        self.assertEqual(retrieved_pain_point.frequency, pain_point.frequency)
        self.assertEqual(retrieved_pain_point.impact, pain_point.impact)
        
        # Check if the pain point was added to the niche
        updated_niche = self.repo.get_niche(niche.id)
        self.assertIn(pain_point.id, updated_niche.pain_points)
    
    def test_get_pain_points_by_niche(self):
        """Test retrieving and sorting pain points by niche."""
        # Create a niche
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        # Create and save pain points with different priorities
        p1 = PainPoint(description="Pain 1", niche_id=niche.id, severity=3, frequency=3, impact=3)  # Score: 27
        p2 = PainPoint(description="Pain 2", niche_id=niche.id, severity=5, frequency=4, impact=2)  # Score: 40
        p3 = PainPoint(description="Pain 3", niche_id=niche.id, severity=2, frequency=2, impact=2)  # Score: 8
        
        self.repo.save_pain_point(p1)
        self.repo.save_pain_point(p2)
        self.repo.save_pain_point(p3)
        
        # Get pain points by niche
        pain_points = self.repo.get_pain_points_by_niche(niche.id)
        self.assertEqual(len(pain_points), 3)
        
        # Check if pain points are sorted by priority (severity * frequency * impact)
        self.assertEqual(pain_points[0].id, p2.id)  # Highest score
        self.assertEqual(pain_points[1].id, p1.id)  # Middle score
        self.assertEqual(pain_points[2].id, p3.id)  # Lowest score
    
    def test_save_and_get_positioning_statement(self):
        """Test saving and retrieving a positioning statement."""
        # Create a niche and pain points first
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        pain_point1 = PainPoint(description="Pain 1", niche_id=niche.id)
        pain_point2 = PainPoint(description="Pain 2", niche_id=niche.id)
        
        self.repo.save_pain_point(pain_point1)
        self.repo.save_pain_point(pain_point2)
        
        # Create a positioning statement
        positioning = PositioningStatement(
            statement="I help Test Niche do painful things in 10 minutes instead of 10 hours.",
            target_audience="Test Audience",
            niche_id=niche.id,
            pain_point_ids=[pain_point1.id, pain_point2.id]
        )
        
        # Save the positioning statement
        success = self.repo.save_positioning_statement(positioning)
        self.assertTrue(success)
        
        # Check if the file was created
        positioning_path = os.path.join(self.temp_dir, "positioning", f"{positioning.id}.json")
        self.assertTrue(os.path.exists(positioning_path))
        
        # Retrieve the positioning statement
        retrieved_positioning = self.repo.get_positioning_statement(positioning.id)
        self.assertIsNotNone(retrieved_positioning)
        self.assertEqual(retrieved_positioning.id, positioning.id)
        self.assertEqual(retrieved_positioning.statement, positioning.statement)
        self.assertEqual(retrieved_positioning.target_audience, positioning.target_audience)
        self.assertEqual(retrieved_positioning.niche_id, positioning.niche_id)
        self.assertEqual(retrieved_positioning.pain_point_ids, positioning.pain_point_ids)
        
        # Check if the positioning statement was added to the niche
        updated_niche = self.repo.get_niche(niche.id)
        self.assertIn(positioning.id, updated_niche.positioning_statements)
    
    def test_get_positioning_statements_by_niche(self):
        """Test retrieving positioning statements by niche."""
        # Create a niche
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        # Create and save positioning statements
        p1 = PositioningStatement(statement="Statement 1", target_audience="Audience 1", niche_id=niche.id)
        p2 = PositioningStatement(statement="Statement 2", target_audience="Audience 2", niche_id=niche.id)
        p3 = PositioningStatement(statement="Statement 3", target_audience="Audience 3", niche_id=niche.id)
        
        self.repo.save_positioning_statement(p1)
        self.repo.save_positioning_statement(p2)
        self.repo.save_positioning_statement(p3)
        
        # Get positioning statements by niche
        statements = self.repo.get_positioning_statements_by_niche(niche.id)
        self.assertEqual(len(statements), 3)
        
        # Check if all statements are included
        statement_ids = [stmt.id for stmt in statements]
        self.assertIn(p1.id, statement_ids)
        self.assertIn(p2.id, statement_ids)
        self.assertIn(p3.id, statement_ids)
    
    def test_delete_niche_and_cascade(self):
        """Test deleting a niche and its associated data."""
        # Create a niche with interviews, pain points, and positioning statements
        niche = Niche(name="Test Niche", description="Test Description")
        self.repo.save_niche(niche)
        
        # Create interview
        interview = Interview(expert_name="John Doe", niche_id=niche.id)
        self.repo.save_interview(interview)
        
        # Create question and response
        question = InterviewQuestion(text="Test Question", category="category")
        self.repo.save_question(question)
        
        interview.add_question(question.id)
        self.repo.save_interview(interview)
        
        response = Response(answer="Test Answer", question_id=question.id, interview_id=interview.id)
        self.repo.save_response(response)
        
        # Create pain point
        pain_point = PainPoint(description="Test Pain", niche_id=niche.id)
        self.repo.save_pain_point(pain_point)
        
        # Create positioning statement
        positioning = PositioningStatement(
            statement="Test Statement",
            target_audience="Test Audience",
            niche_id=niche.id,
            pain_point_ids=[pain_point.id]
        )
        self.repo.save_positioning_statement(positioning)
        
        # Delete the niche
        success = self.repo.delete_niche(niche.id)
        self.assertTrue(success)
        
        # Check if the niche file was deleted
        niche_path = os.path.join(self.temp_dir, "niches", f"{niche.id}.json")
        self.assertFalse(os.path.exists(niche_path))
        
        # Check if the niche was removed from the index
        index_path = os.path.join(self.temp_dir, "niche_index.json")
        from src.saas_pipeline.utils.file_io import read_json
        index = read_json(index_path, default={})
        self.assertNotIn(niche.id, index)
        
        # Check if associated data was deleted
        interview_path = os.path.join(self.temp_dir, "interviews", f"{interview.id}.json")
        self.assertFalse(os.path.exists(interview_path))
        
        pain_point_path = os.path.join(self.temp_dir, "pain_points", f"{pain_point.id}.json")
        self.assertFalse(os.path.exists(pain_point_path))
        
        positioning_path = os.path.join(self.temp_dir, "positioning", f"{positioning.id}.json")
        self.assertFalse(os.path.exists(positioning_path))
        
        # Response should be deleted when interview is deleted
        response_path = os.path.join(self.temp_dir, "responses", f"{response.id}.json")
        self.assertFalse(os.path.exists(response_path))
        
        # Question is not owned by the niche, so it should still exist
        question_path = os.path.join(self.temp_dir, "questions", f"{question.id}.json")
        self.assertTrue(os.path.exists(question_path))


if __name__ == "__main__":
    unittest.main() 