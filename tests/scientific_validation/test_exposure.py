"""Tests for Exposure scoring."""
import pytest
from pydantic import ValidationError

from scientific.exposure.scoring import (
    ExposureInput,
    InfrastructureTransitScores,
    LifestyleScores,
    calculate_exposure,
    calculate_infrastructure_transit,
    calculate_lifestyle,
)


def _all_low_exposure():
    return ExposureInput(
        infrastructure_transit=InfrastructureTransitScores(condition=0.33, facilities=0.33),
        lifestyle=LifestyleScores(alcohol=0.33, sleep=0.33, tobacco=0.33, caffeine=0.33),
        fluid_activity=0.33,
        air_quality=0.33,
        healthcare_access=0.33,
    )


def _all_high_exposure():
    return ExposureInput(
        infrastructure_transit=InfrastructureTransitScores(condition=1.00, facilities=1.00),
        lifestyle=LifestyleScores(alcohol=1.00, sleep=1.00, tobacco=1.00, caffeine=1.00),
        fluid_activity=1.00,
        air_quality=1.00,
        healthcare_access=1.00,
    )


def test_exposure_all_low():
    result = calculate_exposure(_all_low_exposure())
    assert result.exposure_index == pytest.approx(0.33, abs=1e-9)


def test_exposure_all_high():
    result = calculate_exposure(_all_high_exposure())
    assert result.exposure_index == pytest.approx(0.999, abs=1e-3)


def test_infrastructure_transit():
    scores = InfrastructureTransitScores(condition=0.66, facilities=0.33)
    result = calculate_infrastructure_transit(scores)
    expected = 0.508 * 0.66 + 0.492 * 0.33
    assert result == pytest.approx(expected, abs=1e-9)


def test_lifestyle():
    scores = LifestyleScores(alcohol=1.00, sleep=0.33, tobacco=0.33, caffeine=0.33)
    result = calculate_lifestyle(scores)
    expected = 0.341 * 1.00 + 0.232 * 0.33 + 0.218 * 0.33 + 0.208 * 0.33
    assert result == pytest.approx(expected, abs=1e-9)


def test_contributions_sum():
    result = calculate_exposure(_all_high_exposure())
    total_contrib = sum(c.contribution for c in result.contributions.values())
    assert total_contrib == pytest.approx(0.999, abs=1e-3)


def test_invalid_score_rejected():
    with pytest.raises(ValidationError):
        ExposureInput(
            infrastructure_transit=InfrastructureTransitScores(condition=0.50, facilities=0.33),
            lifestyle=LifestyleScores(alcohol=0.33, sleep=0.33, tobacco=0.33, caffeine=0.33),
            fluid_activity=0.33,
            air_quality=0.33,
            healthcare_access=0.33,
        )


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        ExposureInput(
            infrastructure_transit=InfrastructureTransitScores(condition=0.33, facilities=0.33),
            lifestyle=LifestyleScores(alcohol=0.33, sleep=0.33, tobacco=0.33, caffeine=0.33),
            fluid_activity=0.33, air_quality=0.33, healthcare_access=0.33,
            extra=1.0,
        )
