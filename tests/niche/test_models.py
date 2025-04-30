"""
Tests for niche research data models.
"""

import unittest
from datetime import datetime
from src.saas_pipeline.niche.models import (
    Niche, Interview, InterviewQuestion, Response, PainPoint, PositioningStatement
)


class TestNicheModel(unittest.TestCase):
    """Test cases for the Niche data model."""
    
    def test_niche_creation(self):
        """Test creating a Niche object."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        self.assertEqual(niche.name, "Email Marketing for Freelancers")
        self.assertEqual(niche.description, "Tools and strategies for freelancers to manage email marketing.")
        self.assertIsNotNone(niche.id)
        self.assertIsInstance(niche.created_at, datetime)
        self.assertIsInstance(niche.updated_at, datetime)
        self.assertEqual(niche.interviews, [])
        self.assertEqual(niche.pain_points, [])
        self.assertEqual(niche.positioning_statements, [])
    
    def test_niche_validation(self):
        """Test Niche validation for required fields."""
        with self.assertRaises(ValueError):
            Niche(name="", description="Description")
        
        with self.assertRaises(ValueError):
            Niche(name="Name", description="")
    
    def test_niche_to_dict(self):
        """Test converting a Niche to a dictionary."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        niche_dict = niche.to_dict()
        self.assertEqual(niche_dict["name"], "Email Marketing for Freelancers")
        self.assertEqual(niche_dict["description"], "Tools and strategies for freelancers to manage email marketing.")
        self.assertEqual(niche_dict["interviews"], [])
        self.assertEqual(niche_dict["pain_points"], [])
        self.assertEqual(niche_dict["positioning_statements"], [])
        self.assertIsInstance(niche_dict["created_at"], str)
        self.assertIsInstance(niche_dict["updated_at"], str)
    
    def test_niche_from_dict(self):
        """Test creating a Niche from a dictionary."""
        niche_dict = {
            "id": "test-id",
            "name": "Email Marketing for Freelancers",
            "description": "Tools and strategies for freelancers to manage email marketing.",
            "target_audience": "Freelancers",
            "market_size": "Medium",
            "competition": "High",
            "interviews": ["interview-1", "interview-2"],
            "pain_points": ["pain-1", "pain-2"],
            "positioning_statements": ["pos-1"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        niche = Niche.from_dict(niche_dict)
        self.assertEqual(niche.id, "test-id")
        self.assertEqual(niche.name, "Email Marketing for Freelancers")
        self.assertEqual(niche.description, "Tools and strategies for freelancers to manage email marketing.")
        self.assertEqual(niche.target_audience, "Freelancers")
        self.assertEqual(niche.market_size, "Medium")
        self.assertEqual(niche.competition, "High")
        self.assertEqual(niche.interviews, ["interview-1", "interview-2"])
        self.assertEqual(niche.pain_points, ["pain-1", "pain-2"])
        self.assertEqual(niche.positioning_statements, ["pos-1"])
    
    def test_add_interview(self):
        """Test adding an interview to a niche."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        niche.add_interview("interview-1")
        self.assertEqual(niche.interviews, ["interview-1"])
        
        # Adding the same interview again shouldn't duplicate it
        niche.add_interview("interview-1")
        self.assertEqual(niche.interviews, ["interview-1"])
        
        niche.add_interview("interview-2")
        self.assertEqual(niche.interviews, ["interview-1", "interview-2"])
    
    def test_add_pain_point(self):
        """Test adding a pain point to a niche."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        niche.add_pain_point("pain-1")
        self.assertEqual(niche.pain_points, ["pain-1"])
        
        # Adding the same pain point again shouldn't duplicate it
        niche.add_pain_point("pain-1")
        self.assertEqual(niche.pain_points, ["pain-1"])
        
        niche.add_pain_point("pain-2")
        self.assertEqual(niche.pain_points, ["pain-1", "pain-2"])
    
    def test_add_positioning_statement(self):
        """Test adding a positioning statement to a niche."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        niche.add_positioning_statement("pos-1")
        self.assertEqual(niche.positioning_statements, ["pos-1"])
        
        # Adding the same positioning statement again shouldn't duplicate it
        niche.add_positioning_statement("pos-1")
        self.assertEqual(niche.positioning_statements, ["pos-1"])
        
        niche.add_positioning_statement("pos-2")
        self.assertEqual(niche.positioning_statements, ["pos-1", "pos-2"])
    
    def test_update(self):
        """Test updating niche attributes."""
        niche = Niche(
            name="Email Marketing for Freelancers",
            description="Tools and strategies for freelancers to manage email marketing."
        )
        
        original_updated_at = niche.updated_at
        
        # Wait a moment to ensure timestamps differ
        import time
        time.sleep(0.001)
        
        niche.update(
            name="Updated Name",
            target_audience="Updated Audience",
            invalid_field="Should be ignored"
        )
        
        self.assertEqual(niche.name, "Updated Name")
        self.assertEqual(niche.description, "Tools and strategies for freelancers to manage email marketing.")
        self.assertEqual(niche.target_audience, "Updated Audience")
        self.assertFalse(hasattr(niche, "invalid_field"))
        self.assertNotEqual(niche.updated_at, original_updated_at)


class TestInterviewModel(unittest.TestCase):
    """Test cases for the Interview data model."""
    
    def test_interview_creation(self):
        """Test creating an Interview object."""
        interview = Interview(
            expert_name="John Doe",
            niche_id="niche-1",
            role="Marketing Consultant"
        )
        
        self.assertEqual(interview.expert_name, "John Doe")
        self.assertEqual(interview.niche_id, "niche-1")
        self.assertEqual(interview.role, "Marketing Consultant")
        self.assertIsNone(interview.contact_info)
        self.assertIsNone(interview.notes)
        self.assertIsNotNone(interview.id)
        self.assertIsInstance(interview.date, datetime)
        self.assertIsInstance(interview.created_at, datetime)
        self.assertIsInstance(interview.updated_at, datetime)
        self.assertEqual(interview.questions, [])
        self.assertEqual(interview.responses, [])
    
    def test_interview_validation(self):
        """Test Interview validation for required fields."""
        with self.assertRaises(ValueError):
            Interview(expert_name="", niche_id="niche-1")
        
        with self.assertRaises(ValueError):
            Interview(expert_name="John Doe", niche_id="")
    
    def test_add_question(self):
        """Test adding a question to an interview."""
        interview = Interview(
            expert_name="John Doe",
            niche_id="niche-1"
        )
        
        interview.add_question("q-1")
        self.assertEqual(interview.questions, ["q-1"])
        
        # Adding the same question again shouldn't duplicate it
        interview.add_question("q-1")
        self.assertEqual(interview.questions, ["q-1"])
        
        interview.add_question("q-2")
        self.assertEqual(interview.questions, ["q-1", "q-2"])
    
    def test_add_response(self):
        """Test adding a response to an interview."""
        interview = Interview(
            expert_name="John Doe",
            niche_id="niche-1"
        )
        
        interview.add_response("r-1")
        self.assertEqual(interview.responses, ["r-1"])
        
        # Adding the same response again shouldn't duplicate it
        interview.add_response("r-1")
        self.assertEqual(interview.responses, ["r-1"])
        
        interview.add_response("r-2")
        self.assertEqual(interview.responses, ["r-1", "r-2"])


class TestPainPointModel(unittest.TestCase):
    """Test cases for the PainPoint data model."""
    
    def test_pain_point_creation(self):
        """Test creating a PainPoint object."""
        pain_point = PainPoint(
            description="Time-consuming email list management",
            niche_id="niche-1",
            severity=4,
            frequency=5,
            impact=3
        )
        
        self.assertEqual(pain_point.description, "Time-consuming email list management")
        self.assertEqual(pain_point.niche_id, "niche-1")
        self.assertEqual(pain_point.severity, 4)
        self.assertEqual(pain_point.frequency, 5)
        self.assertEqual(pain_point.impact, 3)
        self.assertIsNotNone(pain_point.id)
        self.assertIsInstance(pain_point.created_at, datetime)
        self.assertIsInstance(pain_point.updated_at, datetime)
    
    def test_pain_point_validation(self):
        """Test PainPoint validation for required fields and value ranges."""
        with self.assertRaises(ValueError):
            PainPoint(description="", niche_id="niche-1")
        
        with self.assertRaises(ValueError):
            PainPoint(description="Description", niche_id="niche-1", severity=0)
        
        with self.assertRaises(ValueError):
            PainPoint(description="Description", niche_id="niche-1", severity=6)
        
        with self.assertRaises(ValueError):
            PainPoint(description="Description", niche_id="niche-1", frequency=0)
        
        with self.assertRaises(ValueError):
            PainPoint(description="Description", niche_id="niche-1", frequency=6)
        
        with self.assertRaises(ValueError):
            PainPoint(description="Description", niche_id="niche-1", impact=0)
        
        with self.assertRaises(ValueError):
            PainPoint(description="Description", niche_id="niche-1", impact=6)


class TestPositioningStatementModel(unittest.TestCase):
    """Test cases for the PositioningStatement data model."""
    
    def test_positioning_statement_creation(self):
        """Test creating a PositioningStatement object."""
        positioning = PositioningStatement(
            statement="I help freelancers manage email lists in 10 minutes instead of 10 hours.",
            target_audience="Freelancers",
            niche_id="niche-1",
            pain_point_ids=["pain-1", "pain-2"]
        )
        
        self.assertEqual(positioning.statement, "I help freelancers manage email lists in 10 minutes instead of 10 hours.")
        self.assertEqual(positioning.target_audience, "Freelancers")
        self.assertEqual(positioning.niche_id, "niche-1")
        self.assertEqual(positioning.pain_point_ids, ["pain-1", "pain-2"])
        self.assertIsNotNone(positioning.id)
        self.assertIsInstance(positioning.created_at, datetime)
        self.assertIsInstance(positioning.updated_at, datetime)
    
    def test_positioning_statement_validation(self):
        """Test PositioningStatement validation for required fields."""
        with self.assertRaises(ValueError):
            PositioningStatement(statement="", target_audience="Audience", niche_id="niche-1")
        
        with self.assertRaises(ValueError):
            PositioningStatement(statement="Statement", target_audience="", niche_id="niche-1")
        
        with self.assertRaises(ValueError):
            PositioningStatement(statement="Statement", target_audience="Audience", niche_id="")
    
    def test_add_pain_point(self):
        """Test adding a pain point to a positioning statement."""
        positioning = PositioningStatement(
            statement="I help freelancers manage email lists in 10 minutes instead of 10 hours.",
            target_audience="Freelancers",
            niche_id="niche-1"
        )
        
        positioning.add_pain_point("pain-1")
        self.assertEqual(positioning.pain_point_ids, ["pain-1"])
        
        # Adding the same pain point again shouldn't duplicate it
        positioning.add_pain_point("pain-1")
        self.assertEqual(positioning.pain_point_ids, ["pain-1"])
        
        positioning.add_pain_point("pain-2")
        self.assertEqual(positioning.pain_point_ids, ["pain-1", "pain-2"])


if __name__ == "__main__":
    unittest.main() 