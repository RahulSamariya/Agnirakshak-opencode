"""Tests for UTCI normalization."""
import pytest
from pydantic import ValidationError

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
    model = HazardNormalizationInput(utci_c=30.0)
    with pytest.raises(ValidationError):
        model.utci_c = 35.0


def test_utci_extra_forbid():
    with pytest.raises(ValidationError):
        HazardNormalizationInput(utci_c=30.0, extra_field=1.0)


def test_interface_implementation():
    model = UTCIHazardModel()
    assert model.model_name == "utci-hazard-v1"
    result = model.calculate_hazard(41.2)
    assert 0.0 <= result.hazard_index <= 1.0
    assert result.utci_c == 41.2
    assert isinstance(result.category, str)


# ---------------------------------------------------------------------------
# Semantic tests: H values map to correct hazard categories
# ---------------------------------------------------------------------------

class TestHazardCategoryMapping:
    """Prove that H-score values map to the correct hazard categories."""

    def test_h_zero_maps_to_no_stress(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.0)
        assert cat == "No thermal stress"

    def test_h_025_maps_to_no_stress(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.25)
        assert cat == "No thermal stress"

    def test_h_026_maps_to_moderate(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.26)
        assert cat == "Moderate heat stress"

    def test_h_050_maps_to_moderate(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.50)
        assert cat == "Moderate heat stress"

    def test_h_051_maps_to_strong(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.51)
        assert cat == "Strong heat stress"

    def test_h_075_maps_to_strong(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.75)
        assert cat == "Strong heat stress"

    def test_h_076_maps_to_very_strong(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(0.76)
        assert cat == "Very strong heat stress"

    def test_h_100_maps_to_very_strong(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(1.00)
        assert cat == "Very strong heat stress"

    def test_h_above_1_maps_to_extreme(self):
        model = UTCIHazardModel()
        cat = model.get_hazard_category(1.5)
        assert cat == "Extreme heat stress"

    def test_utci_20_is_no_stress(self):
        result = normalize_hazard(HazardNormalizationInput(utci_c=20.0))
        assert result.category == HazardCategory.NO_THERMAL_STRESS
        assert 0.0 <= result.hazard_index <= 0.25

    def test_utci_30_is_moderate(self):
        result = normalize_hazard(HazardNormalizationInput(utci_c=30.0))
        assert result.category == HazardCategory.MODERATE_HEAT_STRESS
        assert 0.25 < result.hazard_index <= 0.50

    def test_utci_35_is_strong(self):
        result = normalize_hazard(HazardNormalizationInput(utci_c=35.0))
        assert result.category == HazardCategory.STRONG_HEAT_STRESS
        assert 0.50 < result.hazard_index <= 0.75

    def test_utci_42_is_very_strong(self):
        result = normalize_hazard(HazardNormalizationInput(utci_c=42.0))
        assert result.category == HazardCategory.VERY_STRONG_HEAT_STRESS
        assert 0.75 < result.hazard_index <= 1.00

    def test_utci_55_is_extreme(self):
        result = normalize_hazard(HazardNormalizationInput(utci_c=55.0))
        assert result.category == HazardCategory.EXTREME_HEAT_STRESS
        assert result.hazard_index == 1.00
