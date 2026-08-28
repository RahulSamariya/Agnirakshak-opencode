"""Model registry service - bridges YAML config to database."""
from datetime import UTC
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scientific import ModelRun, ScientificModel

CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "scientific" / "configuration"


class ModelRegistryService:
    """Service for managing scientific model registry."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_models(
        self,
        model_type: str | None = None,
        status: str | None = None,
    ) -> list[ScientificModel]:
        """Get all registered scientific models."""
        query = select(ScientificModel)
        if model_type:
            query = query.where(ScientificModel.model_type == model_type)
        if status:
            query = query.where(ScientificModel.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_model_by_id(self, model_id: str) -> ScientificModel | None:
        """Get a specific model by ID."""
        query = select(ScientificModel).where(ScientificModel.id == model_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_model_by_name(self, name: str) -> ScientificModel | None:
        """Get a specific model by name."""
        query = select(ScientificModel).where(ScientificModel.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def register_model(
        self,
        name: str,
        model_type: str,
        version: str,
        description: str | None = None,
        parameters: dict[str, Any] | None = None,
        configuration_yaml: str | None = None,
    ) -> ScientificModel:
        """Register a new scientific model."""
        model = ScientificModel(
            name=name,
            model_type=model_type,
            version=version,
            description=description,
            parameters=parameters,
            configuration_yaml=configuration_yaml,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_model_runs(
        self,
        model_id: str,
        status: str | None = None,
    ) -> list[ModelRun]:
        """Get runs for a specific model."""
        query = select(ModelRun).where(ModelRun.model_id == model_id)
        if status:
            query = query.where(ModelRun.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_model_run_by_id(self, run_id: str) -> ModelRun | None:
        """Get a specific model run."""
        query = select(ModelRun).where(ModelRun.id == run_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def start_model_run(
        self,
        model_id: str,
        input_parameters: dict[str, Any] | None = None,
    ) -> ModelRun:
        """Start a new model run."""
        from datetime import datetime

        run = ModelRun(
            model_id=model_id,
            run_start=datetime.now(UTC),
            status="running",
            input_parameters=input_parameters,
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def complete_model_run(
        self,
        run_id: str,
        output_summary: dict[str, Any] | None = None,
        execution_time_ms: int | None = None,
    ) -> ModelRun | None:
        """Mark a model run as completed."""
        from datetime import datetime

        run = await self.get_model_run_by_id(run_id)
        if run:
            run.status = "completed"
            run.run_end = datetime.now(UTC)
            run.output_summary = output_summary
            run.execution_time_ms = execution_time_ms
            await self.session.commit()
            await self.session.refresh(run)
        return run

    async def fail_model_run(
        self,
        run_id: str,
        error_message: str,
    ) -> ModelRun | None:
        """Mark a model run as failed."""
        from datetime import datetime

        run = await self.get_model_run_by_id(run_id)
        if run:
            run.status = "failed"
            run.run_end = datetime.now(UTC)
            run.error_message = error_message
            await self.session.commit()
            await self.session.refresh(run)
        return run

    def load_yaml_config(self, config_name: str) -> dict[str, Any]:
        """Load a YAML configuration file."""
        config_path = CONFIG_DIR / f"{config_name}.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

    def get_all_configurations(self) -> dict[str, Any]:
        """Load all scientific configurations."""
        configs = {}
        for config_file in CONFIG_DIR.glob("*.yaml"):
            config_name = config_file.stem
            configs[config_name] = self.load_yaml_config(config_name)
        return configs
