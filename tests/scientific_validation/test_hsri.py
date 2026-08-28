"""Tests for HSRI risk calculation."""
import pytest
from pydantic import ValidationError

from scientific.risk.hsri import (
    HSRIInput,
    MultiplicativeHSRIModel,
    RiskLevel,
    calculate_hsri,
    classify_hsri,
)


def test_zero_hazard_produces_zero_hsri():
    result = calculate_hsri(
        HSRIInput(hazard_index=0.0, vulnerability_index=1.0, exposure_index=1.0)
    )
    assert result.hsri_score == 0.0
    assert result.risk_level == RiskLevel.LOW


def test_hsri_multiplication():
    result = calculate_hsri(
        HSRIInput(hazard_index=0.80, vulnerability_index=0.75, exposure_index=0.90)
    )
    assert result.hsri_score == pytest.approx(0.54, abs=1e-9)
    assert result.risk_level == RiskLevel.MEDIUM


def test_hsri_all_max():
    result = calculate_hsri(
        HSRIInput(hazard_index=1.0, vulnerability_index=1.0, exposure_index=1.0)
    )
    assert result.hsri_score == pytest.approx(1.0, abs=1e-9)
    assert result.risk_level == RiskLevel.HIGH


def test_classify_low():
    assert classify_hsri(0.0) == RiskLevel.LOW
    assert classify_hsri(0.33) == RiskLevel.LOW


def test_classify_medium():
    assert classify_hsri(0.34) == RiskLevel.MEDIUM
    assert classify_hsri(0.66) == RiskLevel.MEDIUM


def test_classify_high():
    assert classify_hsri(0.67) == RiskLevel.HIGH
    assert classify_hsri(1.0) == RiskLevel.HIGH


def test_vulnerability_floor_enforced():
    with pytest.raises(ValidationError):
        HSRIInput(hazard_index=0.5, vulnerability_index=0.30, exposure_index=0.5)


def test_exposure_floor_enforced():
    with pytest.raises(ValidationError):
        HSRIInput(hazard_index=0.5, vulnerability_index=0.5, exposure_index=0.30)


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        HSRIInput(
            hazard_index=0.5, vulnerability_index=0.5,
            exposure_index=0.5, extra=1.0,
        )


def test_interface_implementation():
    model = MultiplicativeHSRIModel()
    assert model.model_name == "hsri-multiplicative-v1"
    result = model.calculate(0.8, 0.75, 0.9)
    assert 0.0 <= result.hsri <= 1.0
    assert result.hazard == 0.8
    assert result.vulnerability == 0.75
    assert result.exposure == 0.9


def test_interface_classify_risk():
    from scientific.risk.base import RiskCategory
    model = MultiplicativeHSRIModel()
    assert model.classify_risk(0.2) == RiskCategory.LOW
    assert model.classify_risk(0.5) == RiskCategory.MEDIUM
    assert model.classify_risk(0.8) == RiskCategory.HIGH


def test_interface_thresholds():
    model = MultiplicativeHSRIModel()
    thresholds = model.get_risk_thresholds()
    assert "low" in thresholds
    assert "medium" in thresholds
    assert "high" in thresholds
