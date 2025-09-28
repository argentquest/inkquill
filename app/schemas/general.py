# /ai_rag_story_app/app/schemas/general.py

from pydantic import BaseModel
from typing import Optional

# --- Background: General Purpose Schemas ---
# This file contains Pydantic schemas that are general-purpose and can be
# used across different parts of the application for common response structures
# or simple data payloads.

class MessageResponse(BaseModel):
    """
    A generic Pydantic model for simple message responses from the API.
    Often used for operations that don't return complex data, like a successful
    logout or simple acknowledgements.
    """
    message: str

class DetailResponse(BaseModel):
    """
    A generic Pydantic model for responses that provide a 'detail' message.
    Commonly used by FastAPI for HTTP exceptions.
    """
    detail: str

# --- NEW: Job Submission Response Schema ---
class JobSubmissionResponse(BaseModel):
    """
    A generic response model for endpoints that start a background job.
    Returns a confirmation message and a unique job_id for tracking.
    """
    message: str
    job_id: str