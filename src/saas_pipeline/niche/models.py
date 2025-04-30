"""
Niche Research Data Models

This module defines the data models for niche research, including niches,
interviews, questions, responses, pain points, and positioning statements.
It provides a structured representation of the data and relationships between
different entities used in the niche research module.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union, TypedDict


# TypedDict definitions for JSON serialization
class PainPointDict(TypedDict):
    id: str
    description: str
    severity: int
    frequency: int
    impact: int
    niche_id: str
    created_at: str
    updated_at: str


class ResponseDict(TypedDict):
    id: str
    answer: str
    notes: Optional[str]
    question_id: str
    interview_id: str
    created_at: str


class InterviewQuestionDict(TypedDict):
    id: str
    text: str
    category: str
    order: int
    created_at: str
    updated_at: str


class InterviewDict(TypedDict):
    id: str
    expert_name: str
    role: str
    contact_info: Optional[str]
    date: str
    notes: Optional[str]
    niche_id: str
    questions: List[str]
    responses: List[str]
    created_at: str
    updated_at: str


class PositioningStatementDict(TypedDict):
    id: str
    statement: str
    target_audience: str
    pain_point_ids: List[str]
    niche_id: str
    created_at: str
    updated_at: str


class NicheDict(TypedDict):
    id: str
    name: str
    description: str
    target_audience: Optional[str]
    market_size: Optional[str]
    competition: Optional[str]
    interviews: List[str]
    pain_points: List[str]
    positioning_statements: List[str]
    created_at: str
    updated_at: str


@dataclass
class PainPoint:
    """A pain point identified during niche research interviews."""
    description: str
    niche_id: str
    severity: int = 1  # 1-5 scale, 5 being most severe
    frequency: int = 1  # 1-5 scale, 5 being most frequent
    impact: int = 1  # 1-5 scale, 5 being highest impact
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the pain point data."""
        self._validate()

    def _validate(self):
        """Validate pain point attributes."""
        if not self.description:
            raise ValueError("Pain point description cannot be empty")
        
        for metric in ['severity', 'frequency', 'impact']:
            value = getattr(self, metric)
            if not isinstance(value, int) or value < 1 or value > 5:
                raise ValueError(f"{metric} must be an integer between 1 and 5")

    def update(self, **kwargs):
        """Update pain point attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self._validate()

    def to_dict(self) -> PainPointDict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "severity": self.severity,
            "frequency": self.frequency,
            "impact": self.impact,
            "niche_id": self.niche_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PainPoint':
        """Create a PainPoint instance from a dictionary."""
        # Convert string dates back to datetime objects
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            
        return cls(**data)


@dataclass
class InterviewQuestion:
    """A question used in niche research interviews."""
    text: str
    category: str  # e.g., "pain points", "current solutions", "demographics"
    order: int = 0  # The order in which the question should be asked
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the question data."""
        self._validate()

    def _validate(self):
        """Validate question attributes."""
        if not self.text:
            raise ValueError("Question text cannot be empty")
        if not self.category:
            raise ValueError("Question category cannot be empty")
        if not isinstance(self.order, int) or self.order < 0:
            raise ValueError("Question order must be a non-negative integer")

    def update(self, **kwargs):
        """Update question attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self._validate()

    def to_dict(self) -> InterviewQuestionDict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "order": self.order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterviewQuestion':
        """Create an InterviewQuestion instance from a dictionary."""
        # Convert string dates back to datetime objects
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            
        return cls(**data)


@dataclass
class Response:
    """A response to an interview question."""
    answer: str
    question_id: str
    interview_id: str
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the response data."""
        self._validate()

    def _validate(self):
        """Validate response attributes."""
        if not self.answer:
            raise ValueError("Response answer cannot be empty")
        if not self.question_id:
            raise ValueError("Response must be linked to a question")
        if not self.interview_id:
            raise ValueError("Response must be linked to an interview")

    def to_dict(self) -> ResponseDict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "answer": self.answer,
            "notes": self.notes,
            "question_id": self.question_id,
            "interview_id": self.interview_id,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create a Response instance from a dictionary."""
        # Convert string dates back to datetime objects
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            
        return cls(**data)


@dataclass
class Interview:
    """An interview with a niche expert."""
    expert_name: str
    niche_id: str
    role: str = ""  # Role of the expert in the niche
    contact_info: Optional[str] = None
    date: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None
    questions: List[str] = field(default_factory=list)  # List of question IDs
    responses: List[str] = field(default_factory=list)  # List of response IDs
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the interview data."""
        self._validate()

    def _validate(self):
        """Validate interview attributes."""
        if not self.expert_name:
            raise ValueError("Expert name cannot be empty")
        if not self.niche_id:
            raise ValueError("Interview must be linked to a niche")

    def add_question(self, question_id: str):
        """Add a question ID to the interview."""
        if question_id not in self.questions:
            self.questions.append(question_id)
            self.updated_at = datetime.now()

    def add_response(self, response_id: str):
        """Add a response ID to the interview."""
        if response_id not in self.responses:
            self.responses.append(response_id)
            self.updated_at = datetime.now()

    def update(self, **kwargs):
        """Update interview attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self._validate()

    def to_dict(self) -> InterviewDict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "expert_name": self.expert_name,
            "role": self.role,
            "contact_info": self.contact_info,
            "date": self.date.isoformat(),
            "notes": self.notes,
            "niche_id": self.niche_id,
            "questions": self.questions,
            "responses": self.responses,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interview':
        """Create an Interview instance from a dictionary."""
        # Convert string dates back to datetime objects
        for date_field in ["date", "created_at", "updated_at"]:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
            
        return cls(**data)


@dataclass
class PositioningStatement:
    """A positioning statement for a niche based on pain points."""
    statement: str
    target_audience: str
    niche_id: str
    pain_point_ids: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the positioning statement data."""
        self._validate()

    def _validate(self):
        """Validate positioning statement attributes."""
        if not self.statement:
            raise ValueError("Positioning statement cannot be empty")
        if not self.target_audience:
            raise ValueError("Target audience cannot be empty")
        if not self.niche_id:
            raise ValueError("Positioning statement must be linked to a niche")

    def add_pain_point(self, pain_point_id: str):
        """Add a pain point ID to the positioning statement."""
        if pain_point_id not in self.pain_point_ids:
            self.pain_point_ids.append(pain_point_id)
            self.updated_at = datetime.now()

    def update(self, **kwargs):
        """Update positioning statement attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self._validate()

    def to_dict(self) -> PositioningStatementDict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "statement": self.statement,
            "target_audience": self.target_audience,
            "pain_point_ids": self.pain_point_ids,
            "niche_id": self.niche_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PositioningStatement':
        """Create a PositioningStatement instance from a dictionary."""
        # Convert string dates back to datetime objects
        for date_field in ["created_at", "updated_at"]:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
            
        return cls(**data)


@dataclass
class Niche:
    """A niche market being researched."""
    name: str
    description: str
    target_audience: Optional[str] = None
    market_size: Optional[str] = None
    competition: Optional[str] = None
    interviews: List[str] = field(default_factory=list)  # List of interview IDs
    pain_points: List[str] = field(default_factory=list)  # List of pain point IDs
    positioning_statements: List[str] = field(default_factory=list)  # List of positioning statement IDs
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the niche data."""
        self._validate()

    def _validate(self):
        """Validate niche attributes."""
        if not self.name:
            raise ValueError("Niche name cannot be empty")
        if not self.description:
            raise ValueError("Niche description cannot be empty")

    def add_interview(self, interview_id: str):
        """Add an interview ID to the niche."""
        if interview_id not in self.interviews:
            self.interviews.append(interview_id)
            self.updated_at = datetime.now()

    def add_pain_point(self, pain_point_id: str):
        """Add a pain point ID to the niche."""
        if pain_point_id not in self.pain_points:
            self.pain_points.append(pain_point_id)
            self.updated_at = datetime.now()

    def add_positioning_statement(self, positioning_statement_id: str):
        """Add a positioning statement ID to the niche."""
        if positioning_statement_id not in self.positioning_statements:
            self.positioning_statements.append(positioning_statement_id)
            self.updated_at = datetime.now()

    def update(self, **kwargs):
        """Update niche attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self._validate()

    def to_dict(self) -> NicheDict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_audience": self.target_audience,
            "market_size": self.market_size,
            "competition": self.competition,
            "interviews": self.interviews,
            "pain_points": self.pain_points,
            "positioning_statements": self.positioning_statements,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Niche':
        """Create a Niche instance from a dictionary."""
        # Convert string dates back to datetime objects
        for date_field in ["created_at", "updated_at"]:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
            
        return cls(**data) 