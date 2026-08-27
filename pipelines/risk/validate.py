"""Risk pipeline - validate module."""


class RiskValidator:
    """Handles validation of risk calculation results."""

    def validate_inputs(
        self,
        hazard: float,
        vulnerability: float,
        exposure: float,
    ) -> dict:
        """Validate risk calculation inputs.

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

        if not (0.0 <= hazard <= 1.0):
            results["valid"] = False
            results["errors"].append(f"hazard_out_of_range: {hazard}")

        if not (0.0 <= vulnerability <= 1.0):
            results["valid"] = False
            results["errors"].append(f"vulnerability_out_of_range: {vulnerability}")

        if not (0.0 <= exposure <= 1.0):
            results["valid"] = False
            results["errors"].append(f"exposure_out_of_range: {exposure}")

        return results

    def validate_result(self, hsri: float, risk_category: str) -> dict:
        """Validate risk calculation result.

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

        valid_categories = {"low", "medium", "high"}
        if risk_category not in valid_categories:
            results["valid"] = False
            results["errors"].append(f"invalid_category: {risk_category}")

        return results
