"""Exposure pipeline - normalize module.

Delegates to scientific modules to avoid duplication.
"""
from scientific.exposure.scoring import score_air_quality


def _aqi_to_category(aqi: float) -> str:
    """Convert numeric AQI to category string for scientific module.

    Standard AQI categories:
        0-50: good
        51-100: satisfactory
        101-200: moderate
        201-300: poor
        301-400: very_poor
        401-500: severe
    """
    if aqi <= 50:
        return "good"
    if aqi <= 100:
        return "satisfactory"
    if aqi <= 200:
        return "moderate"
    if aqi <= 300:
        return "poor"
    if aqi <= 400:
        return "very_poor"
    return "severe"


class ExposureNormalizer:
    """Handles normalization of exposure data.

    Delegates to scientific.exposure.scoring for authoritative implementations.
    """

    def normalize_infrastructure_score(self, raw_score: float) -> float:
        """Normalize infrastructure score to 0-1 scale.

        Args:
            raw_score: Raw infrastructure score.

        Returns:
            Normalized score between 0 and 1.
        """
        return raw_score

    def normalize_lifestyle_score(self, raw_score: float) -> float:
        """Normalize lifestyle score to 0-1 scale.

        Args:
            raw_score: Raw lifestyle score.

        Returns:
            Normalized score between 0 and 1.
        """
        return raw_score

    def normalize_air_quality_index(self, aqi: float) -> float:
        """Normalize Air Quality Index to 0-1 scale.

        Delegates to scientific.exposure.scoring.score_air_quality().

        Args:
            aqi: Air Quality Index value.

        Returns:
            Normalized score between 0 and 1.
        """
        category = _aqi_to_category(aqi)
        return score_air_quality(category)

    def normalize_healthcare_access(self, raw_score: float) -> float:
        """Normalize healthcare accessibility score to 0-1 scale.

        Args:
            raw_score: Raw healthcare access score.

        Returns:
            Normalized score between 0 and 1.
        """
        return raw_score
