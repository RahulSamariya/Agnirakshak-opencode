"""Scientific model schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid


class ScientificModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    model_type: str
    version: str
    description: Optional[str] = None
    status: str
    parameters: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelRunResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    run_start: datetime
    run_end: Optional[datetime] = None
    status: str
    input_parameters: Optional[Dict[str, Any]] = None
    output_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelConfigurationResponse(BaseModel):
    model_type: str
    version: str
    configuration: Dict[str, Any]
