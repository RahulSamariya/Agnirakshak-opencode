"""Tests for UTCI normalization."""
from scientific.hazard.utci.normalization import (
    HazardCategory,
    HazardNormalizationInput,
    UTCIHazardModel,
    normalize_hazard,
)


def test_utci_9_boundary():
    result = normalize_hazard(HazardNormalizationInput(utci_c=9.0))
    assert result.hazard_index == 0.0
    assert result.category == HazardCategory.NO_THERMAL_STRESS


def test_utci_26_boundary():
    result = normalize_hazard(HazardNormalizationInput(utci_c=26.0))
    assert result.hazard_index == 0.25
    assert result.category == HazardCategory.MODERATE_HEAT_STRESS


def test_utci_32_boundary():
    result = normalize_hazard(HazardNormalizationInput(utci_c=32.0))
    assert result.hazard_index == 0.50
    assert result.category == HazardCategory.STRONG_HEAT_STRESS


def test_utci_38_boundary():
    result = normalize_hazard(HazardNormalizationInput(utci_c=38.0))
    assert result.hazard_index == 0.75
    assert result.category == HazardCategory.VERY_STRONG_HEAT_STRESS


def test_utci_46_boundary():
    result = normalize_hazard(HazardNormalizationInput(utci_c=46.0))
    assert result.hazard_index == 1.00
    assert result.category == HazardCategory.EXTREME_HEAT_STRESS


def test_utci_above_46_is_capped():
    result = normalize_hazard(HazardNormalizationInput(utci_c=50.0))
    assert result.hazard_index == 1.00
    assert result.category == HazardCategory.EXTREME_HEAT_STRESS


def test_utci_below_9_is_clamped():
    result = normalize_hazard(HazardNormalizationInput(utci_c=0.0))
    assert result.hazard_index == 0.0


def test_utci_mid_range():
    result = normalize_hazard(HazardNormalizationInput(utci_c=29.0))
    assert result.category == HazardCategory.MODERATE_HEAT_STRESS
    assert 0.25 < result.hazard_index < 0.50


def test_utci_frozen_model():
    import pytest
    from pydantic import ValidationError

    model = HazardNormalizationInput(utci_c=30.0)
    with pytest.raises(ValidationError):
        model.utci_c = 35.0


def test_utci_extra_forbid():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        HazardNormalizationInput(utci_c=30.0, extra_field=1.0)


def test_interface_implementation():
    model = UTCIHazardModel()
    assert model.model_name == "utci-hazard-v1"
    result = model.calculate_hazard(41.2)
    assert 0.0 <= result.hazard_index <= 1.0
    assert result.utci_value == 41.2
    assert isinstance(result.hazard_category, str)


def test_interface_get_hazard_category():
    model = UTCIHazardModel()
    cat = model.get_hazard_category(0.5)
    assert isinstance(cat, str)
