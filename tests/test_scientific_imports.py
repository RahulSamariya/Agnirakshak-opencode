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
        ThermalStressCategory,
    )
    from scientific.thermal_comfort.utci import PlaceholderUTCIModel, UTCIInput, UTCIOutput
    assert ThermalComfortModel is not None
    assert ThermalStressCategory is not None
    assert UTCIInput is not None
    assert UTCIOutput is not None
    assert PlaceholderUTCIModel is not None


def test_import_vulnerability():
    """Test vulnerability module imports."""
    from scientific.vulnerability.base import VulnerabilityModel
    from scientific.vulnerability.scoring import VulnerabilityOutput
    assert VulnerabilityModel is not None
    assert VulnerabilityOutput is not None


def test_import_exposure():
    """Test exposure module imports."""
    from scientific.exposure.base import ExposureModel
    from scientific.exposure.scoring import ExposureOutput
    assert ExposureModel is not None
    assert ExposureOutput is not None


def test_import_risk():
    """Test risk module imports."""
    from scientific.risk.base import RiskCategory, RiskModel
    from scientific.risk.hsri import HSRIOutput
    assert RiskModel is not None
    assert HSRIOutput is not None
    assert RiskCategory is not None


def test_import_all_scientific():
    """Test importing all scientific modules together."""
    from scientific import (
        ExposureModel,
        ModelVersion,
        RiskCategory,
        RiskModel,
        ScientificModel,
        ThermalComfortModel,
        ThermalStressCategory,
        VulnerabilityModel,
    )
    from scientific.exposure.scoring import ExposureOutput
    from scientific.hazard.utci.normalization import HazardNormalizationOutput
    from scientific.risk.hsri import HSRIOutput
    from scientific.thermal_comfort.utci import UTCIInput, UTCIOutput
    from scientific.vulnerability.scoring import VulnerabilityOutput
    assert all([
        ScientificModel,
        ModelVersion,
        ThermalComfortModel,
        ThermalStressCategory,
        VulnerabilityModel,
        VulnerabilityOutput,
        ExposureModel,
        ExposureOutput,
        RiskModel,
        HSRIOutput,
        RiskCategory,
        HazardNormalizationOutput,
        UTCIInput,
        UTCIOutput,
    ])
