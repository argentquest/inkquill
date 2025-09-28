from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


class UserInterviewResponse(Base):
    __tablename__ = "user_interview_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_id = Column(String(100), nullable=False, index=True)
    json_response = Column(Text, nullable=False)
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="interview_responses")
    
    def get_response_data(self) -> Dict[str, Any]:
        """Parse and return the JSON response data"""
        return json.loads(self.json_response)
    
    def set_response_data(self, data: Dict[str, Any]) -> None:
        """Set the JSON response data"""
        self.json_response = json.dumps(data, ensure_ascii=False, indent=2)
        self.updated_at = datetime.utcnow()
    
    def get_selected_genres(self) -> List[str]:
        """Extract selected genres from response"""
        data = self.get_response_data()
        genre_response = data.get("responses", {}).get("genre_preferences", {})
        return genre_response.get("selected_values", [])
    
    def get_writing_experience(self) -> List[str]:
        """Extract writing experience from response"""
        data = self.get_response_data()
        exp_response = data.get("responses", {}).get("writing_experience", {})
        return exp_response.get("selected_values", [])
    
    def get_help_needed(self) -> List[str]:
        """Extract help areas from response"""
        data = self.get_response_data()
        help_response = data.get("responses", {}).get("help_needed", {})
        return help_response.get("selected_values", [])
    
    def get_writing_stage(self) -> List[str]:
        """Extract writing stage from response"""
        data = self.get_response_data()
        stage_response = data.get("responses", {}).get("writing_stage", {})
        return stage_response.get("selected_values", [])
    
    def get_navigation_choice(self) -> Optional[str]:
        """Get the navigation choice from Question 5"""
        data = self.get_response_data()
        next_step_response = data.get("responses", {}).get("next_step", {})
        selected = next_step_response.get("selected_values", [])
        return selected[0] if selected else None
    
    def get_navigation_destination(self) -> Optional[str]:
        """Get the final navigation destination"""
        data = self.get_response_data()
        return data.get("navigation", {}).get("final_destination")
    
    def wants_brainstorming(self) -> bool:
        """Check if user wants brainstorming"""
        data = self.get_response_data()
        brainstorm_response = data.get("responses", {}).get("brainstorming_popup", {})
        selected = brainstorm_response.get("selected_values", [])
        return "yes_brainstorm" in selected
    
    def get_story_summary(self) -> Optional[str]:
        """Get the story summary text from Question 7"""
        data = self.get_response_data()
        story_response = data.get("responses", {}).get("story_summary", {})
        return story_response.get("text_value")
    
    def was_question_skipped(self, question_id: str) -> bool:
        """Check if a specific question was skipped"""
        data = self.get_response_data()
        question_response = data.get("responses", {}).get(question_id, {})
        return question_response.get("skipped", False)
    
    def get_completion_metadata(self) -> Dict[str, Any]:
        """Get completion metadata like time taken, questions skipped, etc."""
        data = self.get_response_data()
        return data.get("metadata", {})
    
    # Story Brainstorm specific methods
    def get_story_brainstorm_genres(self) -> List[str]:
        """Extract selected genres from story brainstorm response"""
        if self.interview_id != "story_brainstorm":
            return []
        data = self.get_response_data()
        genre_response = data.get("responses", {}).get("genre_selection", {})
        return genre_response.get("selected_values", [])
    
    def get_story_brainstorm_tone(self) -> List[str]:
        """Extract selected story tones from story brainstorm response"""
        if self.interview_id != "story_brainstorm":
            return []
        data = self.get_response_data()
        tone_response = data.get("responses", {}).get("story_tone", {})
        return tone_response.get("selected_values", [])
    
    def get_story_brainstorm_characters(self) -> Dict[str, Any]:
        """Extract character information from story brainstorm response"""
        if self.interview_id != "story_brainstorm":
            return {}
        data = self.get_response_data()
        responses = data.get("responses", {})
        
        return {
            "character1": {
                "role": responses.get("character1_role", {}).get("selected_values", []),
                "name": responses.get("character1_name", {}).get("text_value", ""),
                "background": responses.get("character1_background", {}).get("text_value", "")
            },
            "character2": {
                "role": responses.get("character2_role", {}).get("selected_values", []),
                "name": responses.get("character2_name", {}).get("text_value", ""),
                "background": responses.get("character2_background", {}).get("text_value", "")
            }
        }
    
    def get_story_brainstorm_elements(self) -> List[str]:
        """Extract selected story elements from story brainstorm response"""
        if self.interview_id != "story_brainstorm":
            return []
        data = self.get_response_data()
        elements_response = data.get("responses", {}).get("story_elements", {})
        return elements_response.get("selected_values", [])
    
    def __repr__(self):
        return f"<UserInterviewResponse(id={self.id}, user_id={self.user_id}, interview_id='{self.interview_id}')>"