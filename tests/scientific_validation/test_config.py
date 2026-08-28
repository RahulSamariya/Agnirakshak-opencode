"""Tests for scientific configuration loading and values."""
import pytest

from scientific.configuration.loader import (
    load_exposure_weights,
    load_hazard_categories,
    load_risk_thresholds,
    load_vulnerability_weights,
)
from scientific.configuration.models import (
    ExposureWeightsConfig,
    HazardCategoriesConfig,
    RiskThresholdsConfig,
    VulnerabilityWeightsConfig,
)


class TestHazardCategoriesConfig:
    def test_loads(self):
        cfg = load_hazard_categories()
        assert isinstance(cfg, HazardCategoriesConfig)

    def test_version(self):
        cfg = load_hazard_categories()
        assert cfg.version == "1.0.0"

    def test_five_categories(self):
        cfg = load_hazard_categories()
        assert len(cfg.categories) == 5

    def test_bounds_sum_to_correct_range(self):
        cfg = load_hazard_categories()
        first = cfg.categories["no_stress"]
        assert first.min == 9.0
        assert first.hazard_min == 0.0
        last = cfg.categories["extreme_heat"]
        assert last.hazard_min == 1.00
        assert last.hazard_max == 1.00


class TestVulnerabilityWeightsConfig:
    def test_loads(self):
        cfg = load_vulnerability_weights()
        assert isinstance(cfg, VulnerabilityWeightsConfig)

    def test_weights_sum_to_one(self):
        cfg = load_vulnerability_weights()
        total = sum(cfg.weights.values())
        assert total == pytest.approx(1.0, abs=1e-9)

    def test_expected_factors(self):
        cfg = load_vulnerability_weights()
        expected = {"age", "bmi", "economic_status", "social_isolation",
                    "education", "gender", "health_issues", "disability"}
        assert set(cfg.weights.keys()) == expected

    def test_scoring_values(self):
        cfg = load_vulnerability_weights()
        assert cfg.scoring["low"] == 0.33
        assert cfg.scoring["medium"] == 0.66
        assert cfg.scoring["high"] == 1.00

    def test_residual_floor(self):
        cfg = load_vulnerability_weights()
        assert cfg.residual_floor == 0.33

    def test_health_issues_sub_weights(self):
        cfg = load_vulnerability_weights()
        assert cfg.health_issues_sub["pre_illness"] == 0.530
        assert cfg.health_issues_sub["medication"] == 0.470
        total = sum(cfg.health_issues_sub.values())
        assert total == pytest.approx(1.0, abs=1e-9)


class TestExposureWeightsConfig:
    def test_loads(self):
        cfg = load_exposure_weights()
        assert isinstance(cfg, ExposureWeightsConfig)

    def test_expected_components(self):
        cfg = load_exposure_weights()
        expected = {"infrastructure_transit", "fluid_intake_activity",
                    "lifestyle", "air_quality", "healthcare_accessibility"}
        assert set(cfg.weights.keys()) == expected

    def test_scoring_values(self):
        cfg = load_exposure_weights()
        assert cfg.scoring["low"] == 0.33
        assert cfg.scoring["medium"] == 0.66
        assert cfg.scoring["high"] == 1.00

    def test_residual_floor(self):
        cfg = load_exposure_weights()
        assert cfg.residual_floor == 0.33

    def test_infrastructure_sub(self):
        cfg = load_exposure_weights()
        assert cfg.infrastructure_transit_sub["condition"] == 0.508
        assert cfg.infrastructure_transit_sub["facilities"] == 0.492

    def test_lifestyle_sub(self):
        cfg = load_exposure_weights()
        assert cfg.lifestyle_sub["alcohol"] == 0.341
        assert cfg.lifestyle_sub["sleep"] == 0.232
        assert cfg.lifestyle_sub["tobacco"] == 0.218
        assert cfg.lifestyle_sub["caffeine"] == 0.208


class TestRiskThresholdsConfig:
    def test_loads(self):
        cfg = load_risk_thresholds()
        assert isinstance(cfg, RiskThresholdsConfig)

    def test_three_categories(self):
        cfg = load_risk_thresholds()
        assert len(cfg.categories) == 3

    def test_thresholds(self):
        cfg = load_risk_thresholds()
        assert cfg.categories["low"].max == 0.33
        assert cfg.categories["medium"].max == 0.66
        assert cfg.categories["high"].max == 1.00

    def test_colors_defined(self):
        cfg = load_risk_thresholds()
        for cat in cfg.categories.values():
            assert cat.color.startswith("#")
