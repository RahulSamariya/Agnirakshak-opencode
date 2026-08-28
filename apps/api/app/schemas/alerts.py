"""Alerts schemas."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ActionRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    alert_id: uuid.UUID
    category: str
    priority: str
    title: str
    description: str
    target_audience: str | None = None
    is_acknowledged: bool
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_run_id: uuid.UUID | None = None
    ward_id: uuid.UUID | None = None
    alert_level: str
    alert_type: str
    title: str
    message: str
    valid_from: datetime
    valid_until: datetime
    issued_at: datetime
    is_active: bool
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class AlertWithRecommendations(AlertResponse):
    recommendations: list[ActionRecommendationResponse] = []
