"""Configuration loader — single source of truth for scientific constants.

Loads YAML files from scientific/configuration/ and returns typed Pydantic models.
Results are cached to avoid repeated file I/O and Pydantic validation.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Final

import yaml

from scientific.configuration.models import (
    ExposureWeightsConfig,
    HazardCategoriesConfig,
    RiskThresholdsConfig,
    VulnerabilityWeightsConfig,
)

_CONFIG_DIR: Final = Path(__file__).parent


def _load_yaml(filename: str) -> dict:
    path = _CONFIG_DIR / filename
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=8)
def load_hazard_categories() -> HazardCategoriesConfig:
    data = _load_yaml("hazard_categories.yaml")
    return HazardCategoriesConfig(**data["hazard_categories"])


@lru_cache(maxsize=8)
def load_vulnerability_weights() -> VulnerabilityWeightsConfig:
    data = _load_yaml("vulnerability_weights.yaml")
    return VulnerabilityWeightsConfig(**data["vulnerability_weights"])


@lru_cache(maxsize=8)
def load_exposure_weights() -> ExposureWeightsConfig:
    data = _load_yaml("exposure_weights.yaml")
    return ExposureWeightsConfig(**data["exposure_weights"])


@lru_cache(maxsize=8)
def load_risk_thresholds() -> RiskThresholdsConfig:
    data = _load_yaml("risk_thresholds.yaml")
    return RiskThresholdsConfig(**data["risk_thresholds"])
