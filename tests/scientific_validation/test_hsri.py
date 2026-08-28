"""Tests for HSRI risk calculation."""
import pytest
from pydantic import ValidationError

from scientific.risk.hsri import (
    HSRIInput,
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
