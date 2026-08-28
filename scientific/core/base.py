from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any


class ModelVersion:
    """Represents a versioned scientific model configuration."""

    def __init__(
        self,
        version: str,
        name: str,
        parameters: dict[str, Any],
        description: str | None = None,
    ):
        self.version = version
        self.name = name
        self.parameters = parameters
        self.description = description
        self.created_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "parameters": self.parameters,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


class ScientificModel(ABC):
    """Base abstract class for all scientific models.

    All scientific models must implement this interface to ensure:
    - Deterministic computation
    - Version tracking
    - Configuration transparency
    - Independent testability
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Unique name identifier for the model."""

    @property
    @abstractmethod
    def model_version(self) -> ModelVersion:
        """Version information for this model instance."""

    @abstractmethod
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate that inputs meet model requirements.

        Args:
            inputs: Dictionary of input parameters.

        Returns:
            True if inputs are valid.

        Raises:
            ValueError: If inputs are invalid with descriptive message.
        """

    @abstractmethod
    def compute(self, inputs: dict[str, Any]) -> Any:
        """Execute the scientific computation.

        Args:
            inputs: Validated input parameters.

        Returns:
            Computation result with type defined by subclass.
        """

    def get_metadata(self) -> dict[str, Any]:
        """Return model metadata for audit trail."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version.to_dict(),
        }
