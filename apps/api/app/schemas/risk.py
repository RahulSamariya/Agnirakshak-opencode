"""Risk schemas."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class RiskAssessmentComponentResponse(BaseModel):
    id: uuid.UUID
    risk_assessment_id: uuid.UUID
    component_type: str
    factor_name: str
    factor_value: float
    weight: float
    weighted_value: float
    rank: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    id: uuid.UUID
    risk_run_id: uuid.UUID
    grid_cell_id: uuid.UUID
    hazard_assessment_id: uuid.UUID
    vulnerability_profile_id: uuid.UUID
    exposure_profile_id: uuid.UUID
    valid_time: datetime
    hazard: float = Field(ge=0.0, le=1.0)
    vulnerability: float = Field(ge=0.0, le=1.0)
    exposure: float = Field(ge=0.0, le=1.0)
    hsri: float = Field(ge=0.0, le=1.0)
    risk_category: str
    calculation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentWithComponents(RiskAssessmentResponse):
    components: List[RiskAssessmentComponentResponse] = []


class RiskExplanationResponse(BaseModel):
    risk_assessment: RiskAssessmentResponse
    hazard_breakdown: Dict[str, Any]
    vulnerability_top_factors: List[Dict[str, Any]]
    exposure_top_factors: List[Dict[str, Any]]
    thresholds_applied: Dict[str, Any]
    model_version: str


class WardRiskSummaryResponse(BaseModel):
    id: uuid.UUID
    risk_run_id: uuid.UUID
    ward_id: uuid.UUID
    valid_time: datetime
    mean_hazard: float = Field(ge=0.0, le=1.0)
    mean_vulnerability: float = Field(ge=0.0, le=1.0)
    mean_exposure: float = Field(ge=0.0, le=1.0)
    mean_hsri: float = Field(ge=0.0, le=1.0)
    max_hsri: float = Field(ge=0.0, le=1.0)
    min_hsri: float = Field(ge=0.0, le=1.0)
    risk_category: str
    cell_count: int
    high_risk_cell_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskRunResponse(BaseModel):
    id: uuid.UUID
    hazard_model_run_id: uuid.UUID
    run_start: datetime
    run_end: Optional[datetime] = None
    status: str
    total_assessments: Optional[int] = None
    completed_assessments: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
