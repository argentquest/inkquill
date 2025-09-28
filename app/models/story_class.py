# /ai_rag_story_app/app/models/story_class.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class StoryClass(Base):
    __tablename__ = "story_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    color = Column(String(7), nullable=False)  # Hex color code like #FF5733
    world_id = Column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    world = relationship("World", back_populates="story_classes")
    acts = relationship("Act", back_populates="story_class")
    scenes = relationship("Scene", back_populates="story_class")

    def __repr__(self):
        return f"<StoryClass(id={self.id}, name='{self.name}', color='{self.color}', world_id={self.world_id})>"