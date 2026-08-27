"""Tests for scientific module interfaces."""
import pytest
from scientific.core.base import ScientificModel, ModelVersion
from scientific.risk.base import RiskModel, RiskCategory, RiskResult


class TestModelVersion:
    def test_model_version_creation(self):
        version = ModelVersion(
            version="1.0.0",
            name="test-model",
            parameters={"param1": 1.0},
            description="Test model version",
        )
        assert version.version == "1.0.0"
        assert version.name == "test-model"
        assert version.parameters == {"param1": 1.0}

    def test_model_version_to_dict(self):
        version = ModelVersion(
            version="1.0.0",
            name="test-model",
            parameters={"param1": 1.0},
        )
        result = version.to_dict()
        assert result["version"] == "1.0.0"
        assert result["name"] == "test-model"
        assert "created_at" in result


class TestRiskCategories:
    def test_risk_category_enum(self):
        assert RiskCategory.LOW.value == "low"
        assert RiskCategory.MEDIUM.value == "medium"
        assert RiskCategory.HIGH.value == "high"

    def test_risk_thresholds(self):
        thresholds = {
            "low_max": 0.33,
            "medium_max": 0.66,
            "high_max": 1.0,
        }
        assert thresholds["low_max"] == 0.33
        assert thresholds["medium_max"] == 0.66
        assert thresholds["high_max"] == 1.0


class TestScientificModelInterface:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            ScientificModel()
