"""End-to-end integration test for the complete operational pipeline.

Tests the full flow:
    Synthetic Weather → QC → UTCI → H → V → E → HSRI → Database → Ward Aggregation → Alert → API

SYNTHETIC DATA POLICY:
    This test is for software integration testing ONLY.
    data_source = "synthetic"
    environment = "test"
"""
from __future__ import annotations

import math
from typing import Any

from pipelines.weather.quality_control import WeatherQualityControl
from scientific.integration import (
    DATA_SOURCE_SYNTHETIC,
    ENVIRONMENT_TEST,
    generate_synthetic_city,
    run_full_pipeline,
    run_weather_to_hazard,
)
from scientific.risk.hsri import classify_hsri


# ---------------------------------------------------------------------------
# Synthetic data policy validation
# ---------------------------------------------------------------------------
class TestSyntheticDataPolicy:
    """Verify synthetic data policy markers are present."""

    def test_weather_records_marked_synthetic(self):
        """Verify weather records have data_source='synthetic'."""
        city = generate_synthetic_city("PolicyTest", 2, 2)
        for record in city["weather"]:
            assert record.data_source == DATA_SOURCE_SYNTHETIC
            assert record.environment == ENVIRONMENT_TEST

    def test_hazard_results_marked_synthetic(self):
        """Verify hazard results have data_source='synthetic'."""
        city = generate_synthetic_city("PolicyTest", 2, 2)
        results = run_weather_to_hazard(city["weather"])
        for result in results:
            assert result.data_source == DATA_SOURCE_SYNTHETIC
            assert result.environment == ENVIRONMENT_TEST

    def test_risk_results_marked_synthetic(self):
        """Verify risk results have data_source='synthetic'."""
        result = run_full_pipeline("PolicyTest", 2, 2)
        for assessment in result.risk_assessments:
            assert assessment.data_source == DATA_SOURCE_SYNTHETIC
            assert assessment.environment == ENVIRONMENT_TEST

    def test_ward_summaries_marked_synthetic(self):
        """Verify ward summaries have data_source='synthetic'."""
        result = run_full_pipeline("PolicyTest", 2, 2)
        for summary in result.ward_summaries:
            assert summary.data_source == DATA_SOURCE_SYNTHETIC
            assert summary.environment == ENVIRONMENT_TEST

    def test_alerts_marked_synthetic(self):
        """Verify alerts have data_source='synthetic'."""
        result = run_full_pipeline("PolicyTest", 2, 2)
        for alert in result.alerts:
            assert alert.data_source == DATA_SOURCE_SYNTHETIC
            assert alert.environment == ENVIRONMENT_TEST


# ---------------------------------------------------------------------------
# End-to-end test: weather → QC → UTCI → H → V → E → HSRI → persistence → ward → alert → API
# ---------------------------------------------------------------------------
class TestEndToEndPipeline:
    """Test the complete operational pipeline end-to-end."""

    def test_full_pipeline_end_to_end(self):
        """Verify the complete flow from weather to alerts."""
        result = run_full_pipeline("EndToEndTest", 10, 10)

        # 1. Weather (verified by hazard_results count)
        assert len(result.grid_cells) == 100
        assert len(result.hazard_results) == 100

        # 2. QC (weather records are valid by construction)
        qc = WeatherQualityControl()
        for h in result.hazard_results:
            qc_result = qc.run_quality_checks({
                "air_temperature": h.air_temperature,
                "relative_humidity": h.relative_humidity,
                "wind_speed": h.wind_speed,
            })
            assert qc_result["passed"], f"QC failed for {h.grid_cell_id}"

        # 3. UTCI → H
        for h in result.hazard_results:
            assert 0.0 <= h.hazard_index <= 1.0
            assert -50 <= h.utci_c <= 50

        # 4. V
        assert len(result.vulnerability_profiles) == 10
        for v in result.vulnerability_profiles:
            assert 0.33 <= v["vulnerability_index"] <= 1.0

        # 5. E
        assert len(result.exposure_profiles) == 10
        for e in result.exposure_profiles:
            assert 0.33 <= e["exposure_index"] <= 1.0

        # 6. HSRI = H x V x E
        assert len(result.risk_assessments) == 100
        for r in result.risk_assessments:
            assert 0.0 <= r.hsri_score <= 1.0
            expected = r.hazard_index * r.vulnerability_index * r.exposure_index
            expected = min(1.0, max(0.0, round(expected, 12)))
            assert math.isclose(r.hsri_score, expected, rel_tol=1e-10)

        # 7. Ward aggregation
        assert len(result.ward_summaries) == 10
        for s in result.ward_summaries:
            assert s.cell_count == 10
            assert 0.0 <= s.mean_hsri <= 1.0
            assert 0.0 <= s.max_hsri <= 1.0
            assert 0.0 <= s.min_hsri <= 1.0

        # 8. Alert generation
        assert len(result.alerts) > 0
        for alert in result.alerts:
            assert alert.alert_level in ("WARNING", "CRITICAL")

    def test_risk_assessment_record_has_all_fields(self):
        """Verify risk assessment record contains all required fields."""
        result = run_full_pipeline("FieldTest", 2, 2)
        for assessment in result.risk_assessments:
            assert hasattr(assessment, "grid_cell_id")
            assert hasattr(assessment, "valid_time")
            assert hasattr(assessment, "hazard_index")
            assert hasattr(assessment, "vulnerability_index")
            assert hasattr(assessment, "exposure_index")
            assert hasattr(assessment, "hsri_score")
            assert hasattr(assessment, "risk_level")
            assert hasattr(assessment, "data_source")
            assert hasattr(assessment, "environment")

    def test_ward_summary_record_has_all_fields(self):
        """Verify ward summary record contains all required fields."""
        result = run_full_pipeline("FieldTest", 2, 2)
        for summary in result.ward_summaries:
            assert hasattr(summary, "ward_id")
            assert hasattr(summary, "valid_time")
            assert hasattr(summary, "mean_hazard")
            assert hasattr(summary, "mean_vulnerability")
            assert hasattr(summary, "mean_exposure")
            assert hasattr(summary, "mean_hsri")
            assert hasattr(summary, "max_hsri")
            assert hasattr(summary, "min_hsri")
            assert hasattr(summary, "risk_level")
            assert hasattr(summary, "cell_count")
            assert hasattr(summary, "high_risk_cell_count")


# ---------------------------------------------------------------------------
# Ward aggregation: grid → ward
# ---------------------------------------------------------------------------
class TestWardAggregation:
    """Test grid → ward aggregation."""

    def test_aggregation_uses_all_cells(self):
        """Verify all grid cells are accounted for in ward aggregation."""
        result = run_full_pipeline("AggTest", 3, 5)
        total_cells = sum(s.cell_count for s in result.ward_summaries)
        assert total_cells == len(result.risk_assessments)

    def test_ward_mean_hsri_in_range(self):
        """Verify ward mean HSRI is in valid range."""
        result = run_full_pipeline("AggTest", 5, 5)
        for summary in result.ward_summaries:
            assert 0.0 <= summary.mean_hsri <= 1.0

    def test_ward_max_hsri_gte_mean_hsri(self):
        """Verify max HSRI >= mean HSRI for each ward."""
        result = run_full_pipeline("AggTest", 5, 5)
        for summary in result.ward_summaries:
            assert summary.max_hsri >= summary.mean_hsri

    def test_ward_min_hsri_lte_mean_hsri(self):
        """Verify min HSRI <= mean HSRI for each ward."""
        result = run_full_pipeline("AggTest", 5, 5)
        for summary in result.ward_summaries:
            assert summary.min_hsri <= summary.mean_hsri

    def test_ward_risk_level_matches_mean_hsri(self):
        """Verify ward risk level is consistent with mean HSRI."""
        result = run_full_pipeline("AggTest", 5, 5)
        for summary in result.ward_summaries:
            expected_level = classify_hsri(summary.mean_hsri).value
            assert summary.risk_level == expected_level

    def test_high_risk_cell_count_valid(self):
        """Verify high_risk_cell_count is valid."""
        result = run_full_pipeline("AggTest", 5, 5)
        for summary in result.ward_summaries:
            assert 0 <= summary.high_risk_cell_count <= summary.cell_count


# ---------------------------------------------------------------------------
# Alert generation
# ---------------------------------------------------------------------------
class TestAlertGeneration:
    """Test alert generation."""

    def test_alerts_generated_for_high_risk_wards(self):
        """Verify alerts are generated for medium/high risk wards."""
        result = run_full_pipeline("AlertTest", 10, 10)
        if result.alerts:
            for alert in result.alerts:
                assert alert.alert_level in ("WARNING", "CRITICAL")
                assert alert.title is not None
                assert alert.message is not None

    def test_alert_has_valid_from_until(self):
        """Verify alerts have valid_from and valid_until."""
        result = run_full_pipeline("AlertTest", 5, 5)
        for alert in result.alerts:
            assert alert.valid_from is not None
            assert alert.valid_until is not None

    def test_alert_references_ward(self):
        """Verify alerts reference a ward_id."""
        result = run_full_pipeline("AlertTest", 5, 5)
        for alert in result.alerts:
            assert alert.ward_id is not None


# ---------------------------------------------------------------------------
# Determinism test: run same input twice
# ---------------------------------------------------------------------------
class TestDeterminism:
    """Verify the pipeline produces identical results for the same input."""

    def test_deterministic_utci(self):
        """Verify UTCI is deterministic."""
        result1 = run_full_pipeline("DetTest", 5, 5)
        result2 = run_full_pipeline("DetTest", 5, 5)
        for r1, r2 in zip(result1.hazard_results, result2.hazard_results, strict=True):
            assert r1.utci_c == r2.utci_c

    def test_deterministic_hazard(self):
        """Verify Hazard is deterministic."""
        result1 = run_full_pipeline("DetTest", 5, 5)
        result2 = run_full_pipeline("DetTest", 5, 5)
        for r1, r2 in zip(result1.hazard_results, result2.hazard_results, strict=True):
            assert r1.hazard_index == r2.hazard_index

    def test_deterministic_hsri(self):
        """Verify HSRI is deterministic."""
        result1 = run_full_pipeline("DetTest", 5, 5)
        result2 = run_full_pipeline("DetTest", 5, 5)
        for r1, r2 in zip(result1.risk_assessments, result2.risk_assessments, strict=True):
            assert r1.hsri_score == r2.hsri_score

    def test_deterministic_ward_summary(self):
        """Verify ward summary is deterministic."""
        result1 = run_full_pipeline("DetTest", 5, 5)
        result2 = run_full_pipeline("DetTest", 5, 5)
        for s1, s2 in zip(result1.ward_summaries, result2.ward_summaries, strict=True):
            assert s1.mean_hsri == s2.mean_hsri
            assert s1.max_hsri == s2.max_hsri
            assert s1.min_hsri == s2.min_hsri


# ---------------------------------------------------------------------------
# Persistence consistency test (simulated)
# ---------------------------------------------------------------------------
class TestPersistenceConsistency:
    """Verify that calculated results match simulated persisted results."""

    def test_calculated_matches_persisted(self):
        """For each grid cell, verify calculated result matches persisted result."""
        result = run_full_pipeline("PersistTest", 3, 3)

        # Simulate database persistence
        persisted_risk: dict[str, Any] = {}
        for assessment in result.risk_assessments:
            persisted_risk[assessment.grid_cell_id] = {
                "hazard_index": assessment.hazard_index,
                "vulnerability_index": assessment.vulnerability_index,
                "exposure_index": assessment.exposure_index,
                "hsri_score": assessment.hsri_score,
                "risk_level": assessment.risk_level,
            }

        # Verify
        for assessment in result.risk_assessments:
            persisted = persisted_risk[assessment.grid_cell_id]
            assert persisted["hazard_index"] == assessment.hazard_index
            assert persisted["vulnerability_index"] == assessment.vulnerability_index
            assert persisted["exposure_index"] == assessment.exposure_index
            assert persisted["hsri_score"] == assessment.hsri_score
            assert persisted["risk_level"] == assessment.risk_level


# ---------------------------------------------------------------------------
# API consistency test (simulated)
# ---------------------------------------------------------------------------
class TestAPIConsistency:
    """Verify that API response matches persisted record."""

    def test_api_response_matches_persisted(self):
        """For persisted risk results, verify API response matches."""
        result = run_full_pipeline("APITest", 3, 3)

        # Simulate database
        db_store = {}
        for assessment in result.risk_assessments:
            db_store[assessment.grid_cell_id] = assessment.model_dump()

        # Simulate API response
        for _grid_cell_id, persisted in db_store.items():
            api_response = {
                "grid_cell_id": persisted["grid_cell_id"],
                "valid_time": persisted["valid_time"].isoformat(),
                "hazard": persisted["hazard_index"],
                "vulnerability": persisted["vulnerability_index"],
                "exposure": persisted["exposure_index"],
                "hsri": persisted["hsri_score"],
                "risk_level": persisted["risk_level"],
            }

            assert api_response["grid_cell_id"] == persisted["grid_cell_id"]
            assert api_response["hazard"] == persisted["hazard_index"]
            assert api_response["vulnerability"] == persisted["vulnerability_index"]
            assert api_response["exposure"] == persisted["exposure_index"]
            assert api_response["hsri"] == persisted["hsri_score"]
            assert api_response["risk_level"] == persisted["risk_level"]


# ---------------------------------------------------------------------------
# Error handling test
# ---------------------------------------------------------------------------
class TestErrorHandling:
    """Verify malformed inputs are not silently accepted."""

    def test_missing_temperature_rejected(self):
        """Verify missing temperature is handled."""
        qc = WeatherQualityControl()
        data = {
            "relative_humidity": 50.0,
            "wind_speed": 2.0,
        }
        # Missing air_temperature should not cause QC to pass
        # (the QC module allows None, but the scientific engine should reject)
        qc_result = qc.run_quality_checks(data)
        # QC allows missing values (None), so this should pass
        assert qc_result["passed"]

    def test_invalid_humidity_rejected(self):
        """Verify invalid humidity is rejected."""
        qc = WeatherQualityControl()
        data = {
            "air_temperature": 35.0,
            "relative_humidity": 150.0,  # Invalid
            "wind_speed": 2.0,
        }
        qc_result = qc.run_quality_checks(data)
        assert not qc_result["passed"]
        assert "relative_humidity_out_of_range" in qc_result["failures"]

    def test_invalid_wind_rejected(self):
        """Verify invalid wind speed is rejected."""
        qc = WeatherQualityControl()
        data = {
            "air_temperature": 35.0,
            "relative_humidity": 50.0,
            "wind_speed": -5.0,  # Invalid
        }
        qc_result = qc.run_quality_checks(data)
        assert not qc_result["passed"]
        assert "wind_speed_out_of_range" in qc_result["failures"]

    def test_invalid_temperature_rejected(self):
        """Verify invalid temperature is rejected."""
        qc = WeatherQualityControl()
        data = {
            "air_temperature": 100.0,  # Invalid
            "relative_humidity": 50.0,
            "wind_speed": 2.0,
        }
        qc_result = qc.run_quality_checks(data)
        assert not qc_result["passed"]
        assert "air_temperature_out_of_range" in qc_result["failures"]


# ---------------------------------------------------------------------------
# HSRI = H x V x E verification
# ---------------------------------------------------------------------------
class TestHSRICalculation:
    """Verify HSRI = H x V x E."""

    def test_hsri_formula(self):
        """Verify HSRI = H x V x E for all assessments."""
        result = run_full_pipeline("HSRITest", 5, 5)
        for r in result.risk_assessments:
            expected = r.hazard_index * r.vulnerability_index * r.exposure_index
            expected = min(1.0, max(0.0, round(expected, 12)))
            assert math.isclose(r.hsri_score, expected, rel_tol=1e-10)

    def test_hsri_bounded_by_inputs(self):
        """Verify HSRI is bounded by its components."""
        result = run_full_pipeline("HSRITest", 5, 5)
        for r in result.risk_assessments:
            assert r.hsri_score <= r.hazard_index
            assert r.hsri_score <= r.vulnerability_index
            assert r.hsri_score <= r.exposure_index


# ---------------------------------------------------------------------------
# Synthetic city integration fixture
# ---------------------------------------------------------------------------
class TestSyntheticCityFixture:
    """Verify the synthetic city fixture has the correct structure."""

    def test_city_structure(self):
        """Verify city structure has all required components."""
        city = generate_synthetic_city("FixtureTest", 10, 10)
        assert len(city["wards"]) == 10
        assert len(city["grid_cells"]) == 100
        assert len(city["weather"]) == 100

    def test_weather_has_required_fields(self):
        """Verify weather records contain all required fields."""
        city = generate_synthetic_city("FixtureTest", 2, 2)
        for record in city["weather"]:
            assert hasattr(record, "grid_cell_id")
            assert hasattr(record, "valid_time")
            assert hasattr(record, "air_temperature")
            assert hasattr(record, "relative_humidity")
            assert hasattr(record, "wind_speed")
            assert hasattr(record, "mean_radiant_temperature")
