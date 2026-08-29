"""Risk pipeline - validate module.

Delegates validation to the scientific engine to avoid duplication.
"""
from pydantic import ValidationError

from scientific.risk.hsri import HSRIInput, classify_hsri


class RiskValidator:
    """Handles validation of risk calculation results.

    Delegates to scientific.risk.hsri for input validation and classification.
    """

    def validate_inputs(
        self,
        hazard: float,
        vulnerability: float,
        exposure: float,
    ) -> dict:
        """Validate risk calculation inputs via HSRIInput Pydantic model.

        Args:
            hazard: Hazard index.
            vulnerability: Vulnerability index.
            exposure: Exposure index.

        Returns:
            Dictionary with validation results.
        """
        results = {
            "valid": True,
            "errors": [],
        }

        try:
            HSRIInput(
                hazard_index=hazard,
                vulnerability_index=vulnerability,
                exposure_index=exposure,
            )
        except ValidationError as e:
            results["valid"] = False
            for err in e.errors():
                results["errors"].append(f"{err['loc'][0]}: {err['msg']}")

        return results

    def validate_result(self, hsri: float, risk_category: str) -> dict:
        """Validate risk calculation result using classify_hsri.

        Args:
            hsri: Calculated HSRI.
            risk_category: Classified risk category.

        Returns:
            Dictionary with validation results.
        """
        results = {
            "valid": True,
            "errors": [],
        }

        if not (0.0 <= hsri <= 1.0):
            results["valid"] = False
            results["errors"].append(f"hsri_out_of_range: {hsri}")

        expected_category = classify_hsri(hsri).value
        if risk_category != expected_category:
            results["valid"] = False
            results["errors"].append(
                f"category_mismatch: expected {expected_category}, got {risk_category}"
            )

        return results
