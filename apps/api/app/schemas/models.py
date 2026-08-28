"""Scientific model schemas."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScientificModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    model_type: str
    version: str
    description: str | None = None
    status: str
    parameters: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class ModelRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_id: uuid.UUID
    run_start: datetime
    run_end: datetime | None = None
    status: str
    input_parameters: dict[str, Any] | None = None
    output_summary: dict[str, Any] | None = None
    error_message: str | None = None
    execution_time_ms: int | None = None
    created_at: datetime
    updated_at: datetime


class ModelConfigurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model_type: str
    version: str
    configuration: dict[str, Any]
