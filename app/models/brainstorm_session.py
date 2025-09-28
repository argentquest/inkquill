from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


class BrainstormSession(Base):
    __tablename__ = "brainstorm_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_response_id = Column(Integer, ForeignKey("user_interview_responses.id"), nullable=False)
    session_name = Column(String(200), nullable=True)  # Optional user-defined name
    generated_concepts = Column(Text, nullable=False)  # JSON array of story concepts
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="brainstorm_sessions")
    interview_response = relationship("UserInterviewResponse")
    favorites = relationship("BrainstormFavorite", back_populates="session", cascade="all, delete-orphan")
    
    def get_concepts(self) -> List[Dict[str, Any]]:
        """Parse and return the generated story concepts"""
        return json.loads(self.generated_concepts)
    
    def set_concepts(self, concepts: List[Dict[str, Any]]) -> None:
        """Set the generated story concepts"""
        self.generated_concepts = json.dumps(concepts, ensure_ascii=False, indent=2)
        self.updated_at = datetime.utcnow()
    
    def add_concept(self, concept: Dict[str, Any]) -> None:
        """Add a single concept to the session"""
        concepts = self.get_concepts()
        concepts.append(concept)
        self.set_concepts(concepts)
    
    def get_concept_by_id(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific concept by its ID"""
        concepts = self.get_concepts()
        for concept in concepts:
            if concept.get('id') == concept_id:
                return concept
        return None
    
    def __repr__(self):
        return f"<BrainstormSession(id={self.id}, user_id={self.user_id}, concepts_count={len(self.get_concepts())})>"


class BrainstormFavorite(Base):
    __tablename__ = "brainstorm_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("brainstorm_sessions.id"), nullable=False)
    concept_id = Column(String(50), nullable=False)  # ID of the concept within the session
    concept_data = Column(Text, nullable=False)  # JSON copy of the concept for quick access
    is_selected = Column(Boolean, default=False)  # If user selected this for story creation
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="brainstorm_favorites")
    session = relationship("BrainstormSession", back_populates="favorites")
    
    def get_concept_data(self) -> Dict[str, Any]:
        """Parse and return the concept data"""
        return json.loads(self.concept_data)
    
    def set_concept_data(self, concept: Dict[str, Any]) -> None:
        """Set the concept data"""
        self.concept_data = json.dumps(concept, ensure_ascii=False, indent=2)
    
    def __repr__(self):
        return f"<BrainstormFavorite(id={self.id}, user_id={self.user_id}, concept_id='{self.concept_id}')>"


class BrainstormStory(Base):
    __tablename__ = "brainstorm_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    favorite_id = Column(Integer, ForeignKey("brainstorm_favorites.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True)  # Link to created story
    title = Column(String(200), nullable=False)
    three_act_structure = Column(Text, nullable=False)  # JSON with act1, act2, act3
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="brainstorm_stories")
    favorite = relationship("BrainstormFavorite")
    story = relationship("Story")
    
    def get_three_acts(self) -> Dict[str, str]:
        """Parse and return the three-act structure"""
        return json.loads(self.three_act_structure)
    
    def set_three_acts(self, acts: Dict[str, str]) -> None:
        """Set the three-act structure"""
        self.three_act_structure = json.dumps(acts, ensure_ascii=False, indent=2)
    
    def __repr__(self):
        return f"<BrainstormStory(id={self.id}, user_id={self.user_id}, title='{self.title}')>"