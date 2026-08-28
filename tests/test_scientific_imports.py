"""Smoke tests for scientific module imports."""


def test_import_scientific_core():
    """Test scientific core module imports."""
    from scientific.core.base import ModelVersion, ScientificModel
    assert ScientificModel is not None
    assert ModelVersion is not None


def test_import_thermal_comfort():
    """Test thermal comfort module imports."""
    from scientific.thermal_comfort.base import (
        ThermalComfortModel,
        ThermalComfortResult,
        ThermalStressCategory,
    )
    assert ThermalComfortModel is not None
    assert ThermalComfortResult is not None
    assert ThermalStressCategory is not None


def test_import_vulnerability():
    """Test vulnerability module imports."""
    from scientific.vulnerability.base import VulnerabilityModel, VulnerabilityResult
    assert VulnerabilityModel is not None
    assert VulnerabilityResult is not None


def test_import_exposure():
    """Test exposure module imports."""
    from scientific.exposure.base import ExposureModel, ExposureResult
    assert ExposureModel is not None
    assert ExposureResult is not None


def test_import_risk():
    """Test risk module imports."""
    from scientific.risk.base import RiskCategory, RiskModel, RiskResult
    assert RiskModel is not None
    assert RiskResult is not None
    assert RiskCategory is not None


def test_import_all_scientific():
    """Test importing all scientific modules together."""
    from scientific import (
        ExposureModel,
        ExposureResult,
        ModelVersion,
        RiskCategory,
        RiskModel,
        RiskResult,
        ScientificModel,
        ThermalComfortModel,
        ThermalComfortResult,
        ThermalStressCategory,
        VulnerabilityModel,
        VulnerabilityResult,
    )
    assert all([
        ScientificModel,
        ModelVersion,
        ThermalComfortModel,
        ThermalComfortResult,
        ThermalStressCategory,
        VulnerabilityModel,
        VulnerabilityResult,
        ExposureModel,
        ExposureResult,
        RiskModel,
        RiskResult,
        RiskCategory,
    ])
