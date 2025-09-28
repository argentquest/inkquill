# /ai_rag_story_app/app/schemas/ai_review.py
from pydantic import BaseModel, Field
from typing import List, Optional

class AISuggestion(BaseModel):
    """
    Pydantic model for a single AI-generated suggestion.
    Includes context snippets to help locate the suggestion in the text.
    """
    id: str = Field(..., description="A unique identifier for the suggestion.")
    category: str = Field(..., description="The category of the feedback (e.g., Pacing, Character Motivation).")
    suggestion_text: str = Field(..., description="The specific, actionable feedback text.")
    proposed_solution: Optional[str] = Field(None, description="A concrete, specific solution or rewrite suggestion for Apply functionality.")
    context_start_snippet: Optional[str] = Field(None, description="First ~5 words of the relevant text segment, if applicable.")
    context_end_snippet: Optional[str] = Field(None, description="Last ~5 words of the relevant text segment, if applicable.")
    explanation: Optional[str] = Field(None, description="Brief reasoning for the suggestion.")
    severity: Optional[str] = Field(None, description="Perceived impact of addressing this suggestion (e.g., High, Medium, Low).")

    class Config:
        from_attributes = True


class MetricDetail(BaseModel):
    """
    Pydantic model for the detail of a single metric, including its rating and justification.
    """
    rating: int = Field(..., ge=1, le=5, description="Rating on a scale of 1 to 5 (5 being excellent).")
    justification: str = Field(..., description="Brief justification for the assigned rating.")

    class Config:
        from_attributes = True


class OptionalMetricDetail(BaseModel):
    """
    Pydantic model for optional metrics that may not apply to all content.
    Rating can be null when the metric doesn't apply (e.g., no dialogue to rate).
    """
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating on a scale of 1 to 5 (5 being excellent), or null if not applicable.")
    justification: str = Field(..., description="Brief justification for the assigned rating or explanation of why not applicable.")

    class Config:
        from_attributes = True


class AIReviewMetrics(BaseModel):
    """
    Pydantic model for the collection of AI-generated metrics for writing quality.
    """
    originality_of_concept: MetricDetail
    engagement_readability: MetricDetail
    character_depth_in_act: MetricDetail
    plot_coherence_pacing_in_act: MetricDetail
    descriptive_language: MetricDetail
    emotional_resonance_of_act: MetricDetail
    dialogue_quality: Optional[OptionalMetricDetail] = None
    grammar_technical_accuracy: Optional[OptionalMetricDetail] = None
    reading_level_appropriateness: Optional[OptionalMetricDetail] = None
    world_building_consistency: Optional[OptionalMetricDetail] = None
    tension_conflict_development: Optional[OptionalMetricDetail] = None
    overall_storytelling_effectiveness_of_act: MetricDetail

    class Config:
        from_attributes = True


class ActAIReviewResponse(BaseModel):
    """
    Pydantic model for the overall JSON response structure from the AI Act Review endpoint.
    """
    suggestions: List[AISuggestion]
    metrics: AIReviewMetrics
    message: Optional[str] = Field(None, description="An optional message providing overall feedback or status of the review process.")
    # rendered_prompt_debug: Optional[str] = Field(None, description="DEBUG: The fully rendered prompt sent to the AI. For debug purposes only.") # Example if you decide to send it back

    class Config:
        from_attributes = True