"""Weather pipeline - quality control module."""


class WeatherQualityControl:
    """Handles quality control of weather data."""

    def __init__(self, thresholds: dict | None = None):
        self.thresholds = thresholds or {
            "temperature_min": -50,
            "temperature_max": 60,
            "humidity_min": 0,
            "humidity_max": 100,
            "wind_speed_min": 0,
            "wind_speed_max": 100,
        }

    def validate_temperature(self, value: float) -> bool:
        """Validate temperature is within reasonable bounds."""
        if value is None:
            return True  # Allow missing values
        return (
            self.thresholds["temperature_min"]
            <= value
            <= self.thresholds["temperature_max"]
        )

    def validate_humidity(self, value: float) -> bool:
        """Validate humidity is within 0-100%."""
        if value is None:
            return True
        return (
            self.thresholds["humidity_min"]
            <= value
            <= self.thresholds["humidity_max"]
        )

    def validate_wind_speed(self, value: float) -> bool:
        """Validate wind speed is within reasonable bounds."""
        if value is None:
            return True
        return (
            self.thresholds["wind_speed_min"]
            <= value
            <= self.thresholds["wind_speed_max"]
        )

    def run_quality_checks(self, data: dict) -> dict:
        """Run all quality checks on weather data.

        Args:
            data: Dictionary of weather variables.

        Returns:
            Dictionary with quality check results.
        """
        results = {
            "passed": True,
            "failures": [],
        }

        if "air_temperature" in data and not self.validate_temperature(data["air_temperature"]):
            results["passed"] = False
            results["failures"].append("air_temperature_out_of_range")

        if "relative_humidity" in data and not self.validate_humidity(data["relative_humidity"]):
            results["passed"] = False
            results["failures"].append("relative_humidity_out_of_range")

        if "wind_speed" in data and not self.validate_wind_speed(data["wind_speed"]):
            results["passed"] = False
            results["failures"].append("wind_speed_out_of_range")

        return results
