# /ai_rag_story_app/app/schemas/job_status.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.job_status import JobTypeEnum, JobStateEnum

class JobStatusRead(BaseModel):
    """
    Pydantic model for returning the status of a background job.
    This is used for polling endpoints.
    """
    job_id: str
    job_type: JobTypeEnum
    state: JobStateEnum
    status_message: Optional[str] = None
    result_message: Optional[str] = None
    world_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True