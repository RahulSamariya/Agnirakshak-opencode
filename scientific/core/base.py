from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class ModelVersion:
    """Represents a versioned scientific model configuration."""

    def __init__(
        self,
        version: str,
        name: str,
        parameters: Dict[str, Any],
        description: Optional[str] = None,
    ):
        self.version = version
        self.name = name
        self.parameters = parameters
        self.description = description
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
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
        pass

    @property
    @abstractmethod
    def model_version(self) -> ModelVersion:
        """Version information for this model instance."""
        pass

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate that inputs meet model requirements.

        Args:
            inputs: Dictionary of input parameters.

        Returns:
            True if inputs are valid.

        Raises:
            ValueError: If inputs are invalid with descriptive message.
        """
        pass

    @abstractmethod
    def compute(self, inputs: Dict[str, Any]) -> Any:
        """Execute the scientific computation.

        Args:
            inputs: Validated input parameters.

        Returns:
            Computation result with type defined by subclass.
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return model metadata for audit trail."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version.to_dict(),
        }
