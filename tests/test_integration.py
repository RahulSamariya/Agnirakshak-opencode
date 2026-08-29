"""End-to-end integration test for the complete pipeline.

Tests the full flow:
    Synthetic Weather → UTCI → H → V → E → HSRI → Ward Aggregation → Alert

This is a deterministic integration test, not a real-world forecast.
"""
from __future__ import annotations

import math

from scientific.integration import (
    PipelineResult,
    run_full_pipeline,
    run_weather_to_hazard,
    run_risk_assessment,
    aggregate_to_wards,
    generate_alerts,
    generate_synthetic_city,
    generate_synthetic_vulnerability,
    generate_synthetic_exposure,
)
from scientific.risk.hsri import classify_hsri
from scientific.vulnerability.scoring import BBWMVulnerabilityModel
from scientific.exposure.scoring import BBWMExposureModel


class TestSyntheticCityGeneration:
    """Test synthetic city data generation."""

    def test_generates_correct_structure(self):
        """Verify city structure has all required components."""
        city = generate_synthetic_city(
            city_name="TestCity",
            num_wards=10,
            grid_cells_per_ward=10,
        )
        assert "city" in city
        assert "wards" in city
        assert "grid_cells" in city
        assert "weather" in city
        assert len(city["wards"]) == 10
        assert len(city["grid_cells"]) == 100
        assert len(city["weather"]) == 100

    def test_deterministic_output(self):
        """Same inputs produce identical outputs."""
        city1 = generate_synthetic_city("TestCity", 5, 5)
        city2 = generate_synthetic_city("TestCity", 5, 5)
        assert city1["city"]["id"] == city2["city"]["id"]
        assert len(city1["wards"]) == len(city2["wards"])
        assert len(city1["grid_cells"]) == len(city2["grid_cells"])

    def test_weather_records_have_required_fields(self):
        """Verify weather records contain all required fields."""
        city = generate_synthetic_city("TestCity", 2, 2)
        for record in city["weather"]:
            assert hasattr(record, "grid_cell_id")
            assert hasattr(record, "valid_time")
            assert hasattr(record, "air_temperature")
            assert hasattr(record, "relative_humidity")
            assert hasattr(record, "wind_speed")
            assert hasattr(record, "mean_radiant_temperature")


class TestVulnerabilityGeneration:
    """Test synthetic vulnerability profile generation."""

    def test_generates_profiles_for_all_wards(self):
        """Verify profiles are generated for each ward."""
        city = generate_synthetic_city("TestCity", 5, 5)
        ward_ids = [w["id"] for w in city["wards"]]
        profiles = generate_synthetic_vulnerability(ward_ids)
        assert len(profiles) == 5

    def test_vulnerability_index_in_range(self):
        """Verify V is in valid range [0.33, 1.0]."""
        city = generate_synthetic_city("TestCity", 5, 5)
        ward_ids = [w["id"] for w in city["wards"]]
        profiles = generate_synthetic_vulnerability(ward_ids)
        for profile in profiles:
            assert 0.33 <= profile["vulnerability_index"] <= 1.0


class TestExposureGeneration:
    """Test synthetic exposure profile generation."""

    def test_generates_profiles_for_all_wards(self):
        """Verify profiles are generated for each ward."""
        city = generate_synthetic_city("TestCity", 5, 5)
        ward_ids = [w["id"] for w in city["wards"]]
        profiles = generate_synthetic_exposure(ward_ids)
        assert len(profiles) == 5

    def test_exposure_index_in_range(self):
        """Verify E is in valid range [0.33, 1.0]."""
        city = generate_synthetic_city("TestCity", 5, 5)
        ward_ids = [w["id"] for w in city["wards"]]
        profiles = generate_synthetic_exposure(ward_ids)
        for profile in profiles:
            assert 0.33 <= profile["exposure_index"] <= 1.0


class TestWeatherToHazard:
    """Test weather → UTCI → Hazard pipeline."""

    def test_produces_hazard_results(self):
        """Verify hazard results are generated for all weather records."""
        city = generate_synthetic_city("TestCity", 2, 2)
        results = run_weather_to_hazard(city["weather"])
        assert len(results) == 4

    def test_hazard_index_in_range(self):
        """Verify H is in valid range [0, 1]."""
        city = generate_synthetic_city("TestCity", 2, 2)
        results = run_weather_to_hazard(city["weather"])
        for result in results:
            assert 0.0 <= result.hazard_index <= 1.0

    def test_utci_in_valid_range(self):
        """Verify UTCI is in valid range."""
        city = generate_synthetic_city("TestCity", 2, 2)
        results = run_weather_to_hazard(city["weather"])
        for result in results:
            assert -50 <= result.utci_c <= 50


class TestRiskAssessment:
    """Test HSRI = H × V × E calculation."""

    def test_produces_risk_assessments(self):
        """Verify risk assessments are generated."""
        city = generate_synthetic_city("TestCity", 2, 2)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]
        vuln_profiles = generate_synthetic_vulnerability(ward_ids)
        exp_profiles = generate_synthetic_exposure(ward_ids)
        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        assert len(assessments) == 4

    def test_hsri_in_valid_range(self):
        """Verify HSRI is in valid range [0, 1]."""
        city = generate_synthetic_city("TestCity", 2, 2)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]
        vuln_profiles = generate_synthetic_vulnerability(ward_ids)
        exp_profiles = generate_synthetic_exposure(ward_ids)
        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        for assessment in assessments:
            assert 0.0 <= assessment.hsri_score <= 1.0

    def test_hsri_equals_h_times_v_times_e(self):
        """Verify HSRI = H × V × E within floating-point tolerance."""
        city = generate_synthetic_city("TestCity", 2, 2)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]
        vuln_profiles = generate_synthetic_vulnerability(ward_ids)
        exp_profiles = generate_synthetic_exposure(ward_ids)
        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        for assessment in assessments:
            expected = assessment.hazard_index * assessment.vulnerability_index * assessment.exposure_index
            expected = min(1.0, max(0.0, round(expected, 12)))
            assert math.isclose(assessment.hsri_score, expected, rel_tol=1e-10)


class TestWardAggregation:
    """Test grid → ward aggregation."""

    def test_produces_ward_summaries(self):
        """Verify ward summaries are generated."""
        city = generate_synthetic_city("TestCity", 3, 3)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]
        vuln_profiles = generate_synthetic_vulnerability(ward_ids)
        exp_profiles = generate_synthetic_exposure(ward_ids)
        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        summaries = aggregate_to_wards(assessments, city["grid_cells"])
        assert len(summaries) == 3

    def test_ward_summary_has_required_fields(self):
        """Verify ward summary contains all required fields."""
        city = generate_synthetic_city("TestCity", 2, 2)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]
        vuln_profiles = generate_synthetic_vulnerability(ward_ids)
        exp_profiles = generate_synthetic_exposure(ward_ids)
        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        summaries = aggregate_to_wards(assessments, city["grid_cells"])
        for summary in summaries:
            assert hasattr(summary, "mean_hsri")
            assert hasattr(summary, "max_hsri")
            assert hasattr(summary, "min_hsri")
            assert hasattr(summary, "risk_level")
            assert hasattr(summary, "cell_count")
            assert hasattr(summary, "high_risk_cell_count")

    def test_ward_risk_level_matches_mean_hsri(self):
        """Verify ward risk level is consistent with mean HSRI."""
        city = generate_synthetic_city("TestCity", 2, 2)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]
        vuln_profiles = generate_synthetic_vulnerability(ward_ids)
        exp_profiles = generate_synthetic_exposure(ward_ids)
        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        summaries = aggregate_to_wards(assessments, city["grid_cells"])
        for summary in summaries:
            expected_level = classify_hsri(summary.mean_hsri).value
            assert summary.risk_level == expected_level


class TestAlertGeneration:
    """Test alert generation."""

    def test_generates_alerts_for_high_risk_wards(self):
        """Verify alerts are generated for medium/high risk wards."""
        # Use more extreme conditions to ensure high risk
        city = generate_synthetic_city("TestCity", 5, 5)
        hazard_results = run_weather_to_hazard(city["weather"])
        ward_ids = [w["id"] for w in city["wards"]]

        # Create vulnerability and exposure profiles with high values
        vuln_profiles = []
        exp_profiles = []
        model_v = BBWMVulnerabilityModel()
        model_e = BBWMExposureModel()

        for i, ward_id in enumerate(ward_ids):
            # High vulnerability
            vuln_data = {
                "age": 1.0,
                "bmi": 1.0,
                "economic_status": 1.0,
                "social_isolation": 1.0,
                "education": 1.0,
                "gender": 1.0,
                "health_issues": 1.0,
                "disability": 1.0,
            }
            vuln_result = model_v.calculate(vuln_data)
            vuln_profiles.append({
                "ward_id": ward_id,
                "vulnerability_index": vuln_result.vulnerability_index,
            })

            # High exposure
            exp_data = {
                "infrastructure_transit": {"condition": 1.0, "facilities": 1.0},
                "fluid_intake_activity": 1.0,
                "lifestyle": {"alcohol": 1.0, "sleep": 1.0, "tobacco": 1.0, "caffeine": 1.0},
                "air_quality": 1.0,
                "healthcare_accessibility": 1.0,
            }
            exp_result = model_e.calculate(exp_data)
            exp_profiles.append({
                "ward_id": ward_id,
                "exposure_index": exp_result.exposure_index,
            })

        vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}
        exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

        assessments = run_risk_assessment(
            hazard_results, vuln_map, exp_map, city["grid_cells"]
        )
        summaries = aggregate_to_wards(assessments, city["grid_cells"])
        alerts = generate_alerts(summaries)

        # At least some alerts should be generated
        assert len(alerts) > 0
        for alert in alerts:
            assert alert.alert_level in ("WARNING", "CRITICAL")


class TestFullPipeline:
    """Test the complete end-to-end pipeline."""

    def test_full_pipeline_completes(self):
        """Verify the full pipeline executes successfully."""
        result = run_full_pipeline(
            city_name="TestCity",
            num_wards=10,
            grid_cells_per_ward=10,
        )
        assert isinstance(result, PipelineResult)
        assert len(result.wards) == 10
        assert len(result.grid_cells) == 100
        assert len(result.hazard_results) == 100
        assert len(result.vulnerability_profiles) == 10
        assert len(result.exposure_profiles) == 10
        assert len(result.risk_assessments) == 100
        assert len(result.ward_summaries) == 10

    def test_full_pipeline_deterministic(self):
        """Verify the full pipeline produces identical results."""
        result1 = run_full_pipeline("TestCity", 5, 5)
        result2 = run_full_pipeline("TestCity", 5, 5)

        # Hazard results should be identical
        for r1, r2 in zip(result1.hazard_results, result2.hazard_results):
            assert r1.utci_c == r2.utci_c
            assert r1.hazard_index == r2.hazard_index

        # Risk assessments should be identical
        for r1, r2 in zip(result1.risk_assessments, result2.risk_assessments):
            assert r1.hsri_score == r2.hsri_score
            assert r1.risk_level == r2.risk_level

        # Ward summaries should be identical
        for s1, s2 in zip(result1.ward_summaries, result2.ward_summaries):
            assert s1.mean_hsri == s2.mean_hsri
            assert s1.max_hsri == s2.max_hsri

    def test_all_values_in_valid_ranges(self):
        """Verify all computed values are in valid ranges."""
        result = run_full_pipeline("TestCity", 5, 5)

        for h in result.hazard_results:
            assert 0.0 <= h.hazard_index <= 1.0
            assert -50 <= h.utci_c <= 50

        for v in result.vulnerability_profiles:
            assert 0.33 <= v["vulnerability_index"] <= 1.0

        for e in result.exposure_profiles:
            assert 0.33 <= e["exposure_index"] <= 1.0

        for r in result.risk_assessments:
            assert 0.0 <= r.hsri_score <= 1.0
            assert 0.0 <= r.hazard_index <= 1.0
            assert 0.33 <= r.vulnerability_index <= 1.0
            assert 0.33 <= r.exposure_index <= 1.0

    def test_hsri_equals_h_v_e_in_pipeline(self):
        """Verify HSRI = H × V × E for all assessments in pipeline."""
        result = run_full_pipeline("TestCity", 3, 3)
        for assessment in result.risk_assessments:
            expected = assessment.hazard_index * assessment.vulnerability_index * assessment.exposure_index
            expected = min(1.0, max(0.0, round(expected, 12)))
            assert math.isclose(assessment.hsri_score, expected, rel_tol=1e-10)
