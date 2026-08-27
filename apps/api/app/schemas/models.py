"""Scientific model schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import uuid


class ScientificModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    model_type: str
    version: str
    description: Optional[str] = None
    status: str
    parameters: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ModelRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class ModelConfigurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model_type: str
    version: str
    configuration: Dict[str, Any]
