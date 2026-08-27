"""Alerts schemas."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import uuid


class ActionRecommendationResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    category: str
    priority: str
    title: str
    description: str
    target_audience: Optional[str] = None
    is_acknowledged: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: uuid.UUID
    risk_run_id: Optional[uuid.UUID] = None
    ward_id: Optional[uuid.UUID] = None
    alert_level: str
    alert_type: str
    title: str
    message: str
    valid_from: datetime
    valid_until: datetime
    issued_at: datetime
    is_active: bool
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertWithRecommendations(AlertResponse):
    recommendations: List[ActionRecommendationResponse] = []
