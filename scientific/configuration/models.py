"""Typed Pydantic configuration models for scientific YAML files."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HazardCategoryConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    min: float
    max: float | None
    hazard_min: float
    hazard_max: float
    label: str


class HazardCategoriesConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    categories: dict[str, HazardCategoryConfig]


class VulnerabilityWeightsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    weights: dict[str, float]
    scoring: dict[str, float]
    health_issues_sub: dict[str, float]
    residual_floor: float


class ExposureWeightsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    weights: dict[str, float]
    infrastructure_transit_sub: dict[str, float]
    lifestyle_sub: dict[str, float]
    scoring: dict[str, float]
    residual_floor: float


class RiskCategoryConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    min: float
    max: float
    label: str
    color: str


class RiskThresholdsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    categories: dict[str, RiskCategoryConfig]
