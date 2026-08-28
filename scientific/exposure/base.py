from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ExposureResult:
    """Result from exposure calculation."""
    exposure_index: float
    factor_scores: dict[str, float]
    weighted_scores: dict[str, float]
    metadata: dict[str, Any]


class ExposureModel(ABC):
    """Abstract base class for exposure models.

    Exposure uses weighted factors based on infrastructure,
    lifestyle, and environmental conditions.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the exposure model."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version of the exposure model."""

    @property
    @abstractmethod
    def weights(self) -> dict[str, float]:
        """Return the current weight configuration."""

    @abstractmethod
    def score_factor(self, factor_name: str, raw_value: Any) -> float:
        """Score a raw factor value.

        Args:
            factor_name: Name of the factor.
            raw_value: Raw input value.

        Returns:
            Score between 0.0 and 1.0.
        """

    @abstractmethod
    def calculate(self, profile: dict[str, Any]) -> ExposureResult:
        """Calculate exposure index from profile data.

        Args:
            profile: Dictionary containing factor values.

        Returns:
            ExposureResult with index and component scores.
        """

    def get_residual_floor(self) -> float:
        """Return the residual risk floor for exposure.

        Default is 0.33 as per scientific specification.
        """
        return 0.33
