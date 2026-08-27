"""Initial schema - all domain tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology")
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Geography tables
    op.create_table(
        "states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "cities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "state_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("states.id"),
            nullable=False,
        ),
        sa.Column("population", sa.Integer),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_cities_state_id", "cities", ["state_id"])

    op.create_table(
        "wards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "city_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cities.id"),
            nullable=False,
        ),
        sa.Column("ward_code", sa.String(20)),
        sa.Column("population", sa.Integer),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_wards_city_id", "wards", ["city_id"])

    op.create_table(
        "grid_cells",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cell_code", sa.String(50), nullable=False, unique=True),
        sa.Column(
            "ward_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wards.id"),
        ),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("geometry", Geometry(geometry_type="POLYGON", srid=4326)),
        sa.Column("centroid", Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_grid_cells_ward_id", "grid_cells", ["ward_id"])
    op.create_index("ix_grid_cells_lat_lon", "grid_cells", ["latitude", "longitude"])

    # Spatial indexes
    op.execute("CREATE INDEX ix_states_geometry ON states USING GIST (geometry)")
    op.execute("CREATE INDEX ix_cities_geometry ON cities USING GIST (geometry)")
    op.execute("CREATE INDEX ix_wards_geometry ON wards USING GIST (geometry)")
    op.execute("CREATE INDEX ix_grid_cells_geometry ON grid_cells USING GIST (geometry)")
    op.execute(
        "CREATE INDEX ix_grid_cells_centroid ON grid_cells USING GIST (centroid)"
    )

    # Weather tables
    op.create_table(
        "weather_stations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("station_code", sa.String(20), nullable=False, unique=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("elevation", sa.Float),
        sa.Column("geometry", Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        "CREATE INDEX ix_weather_stations_geometry ON weather_stations USING GIST (geometry)"
    )

    op.create_table(
        "weather_observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "station_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("weather_stations.id"),
            nullable=False,
        ),
        sa.Column(
            "observation_time", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("air_temperature", sa.Float),
        sa.Column("relative_humidity", sa.Float),
        sa.Column("wind_speed", sa.Float),
        sa.Column("wind_direction", sa.Float),
        sa.Column("mean_radiant_temperature", sa.Float),
        sa.Column("pressure", sa.Float),
        sa.Column("precipitation", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_weather_observations_station_time",
        "weather_observations",
        ["station_id", "observation_time"],
    )
    op.create_index(
        "ix_weather_observations_time",
        "weather_observations",
        ["observation_time"],
    )

    op.create_table(
        "weather_forecast_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_name", sa.String(50), nullable=False),
        sa.Column("run_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("source", sa.String(100)),
        sa.Column("resolution", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_forecast_runs_model_time",
        "weather_forecast_runs",
        ["model_name", "run_time"],
    )

    op.create_table(
        "weather_forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("weather_forecast_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "grid_cell_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("grid_cells.id"),
            nullable=False,
        ),
        sa.Column("valid_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lead_time_hours", sa.Integer, nullable=False),
        sa.Column("air_temperature", sa.Float),
        sa.Column("relative_humidity", sa.Float),
        sa.Column("wind_speed", sa.Float),
        sa.Column("wind_direction", sa.Float),
        sa.Column("mean_radiant_temperature", sa.Float),
        sa.Column("pressure", sa.Float),
        sa.Column("precipitation_probability", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_weather_forecasts_run_grid",
        "weather_forecasts",
        ["run_id", "grid_cell_id"],
    )
    op.create_index(
        "ix_weather_forecasts_valid_time",
        "weather_forecasts",
        ["valid_time"],
    )
    op.create_index(
        "ix_weather_forecasts_grid_valid",
        "weather_forecasts",
        ["grid_cell_id", "valid_time"],
    )

    # Scientific model registry
    op.create_table(
        "scientific_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("model_type", sa.String(50), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("parameters", postgresql.JSON),
        sa.Column("configuration_yaml", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scientific_models_type", "scientific_models", ["model_type"])
    op.create_index(
        "ix_scientific_models_status", "scientific_models", ["status"]
    )

    op.create_table(
        "model_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "model_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scientific_models.id"),
            nullable=False,
        ),
        sa.Column("run_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("run_end", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("input_parameters", postgresql.JSON),
        sa.Column("output_summary", postgresql.JSON),
        sa.Column("error_message", sa.Text),
        sa.Column("execution_time_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_model_runs_model_id", "model_runs", ["model_id"])
    op.create_index("ix_model_runs_status", "model_runs", ["status"])
    op.create_index("ix_model_runs_start", "model_runs", ["run_start"])

    # Hazard
    op.create_table(
        "hazard_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "grid_cell_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("grid_cells.id"),
            nullable=False,
        ),
        sa.Column("valid_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("utci_value", sa.Float, nullable=False),
        sa.Column("hazard_index", sa.Float, nullable=False),
        sa.Column("hazard_category", sa.String(50), nullable=False),
        sa.Column("air_temperature", sa.Float),
        sa.Column("relative_humidity", sa.Float),
        sa.Column("wind_speed", sa.Float),
        sa.Column("mean_radiant_temperature", sa.Float),
        sa.Column("calculation_metadata", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_hazard_assessments_grid_time",
        "hazard_assessments",
        ["grid_cell_id", "valid_time"],
    )
    op.create_index(
        "ix_hazard_assessments_run", "hazard_assessments", ["model_run_id"]
    )

    # Vulnerability
    op.create_table(
        "vulnerability_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "ward_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wards.id"),
            nullable=False,
        ),
        sa.Column(
            "model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id"),
        ),
        sa.Column("vulnerability_index", sa.Float, nullable=False),
        sa.Column("score_details", postgresql.JSON),
        sa.Column("metadata_json", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_vulnerability_profiles_ward", "vulnerability_profiles", ["ward_id"]
    )

    op.create_table(
        "vulnerability_factors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vulnerability_profiles.id"),
            nullable=False,
        ),
        sa.Column("factor_name", sa.String(50), nullable=False),
        sa.Column("raw_value", sa.Text),
        sa.Column("factor_score", sa.Float, nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("weighted_score", sa.Float, nullable=False),
        sa.Column("sub_factors", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_vulnerability_factors_profile",
        "vulnerability_factors",
        ["profile_id"],
    )

    # Exposure
    op.create_table(
        "exposure_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "ward_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wards.id"),
            nullable=False,
        ),
        sa.Column(
            "model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id"),
        ),
        sa.Column("exposure_index", sa.Float, nullable=False),
        sa.Column("score_details", postgresql.JSON),
        sa.Column("metadata_json", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_exposure_profiles_ward", "exposure_profiles", ["ward_id"]
    )

    op.create_table(
        "exposure_factors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exposure_profiles.id"),
            nullable=False,
        ),
        sa.Column("factor_name", sa.String(50), nullable=False),
        sa.Column("raw_value", sa.Text),
        sa.Column("factor_score", sa.Float, nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("weighted_score", sa.Float, nullable=False),
        sa.Column("sub_factors", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_exposure_factors_profile", "exposure_factors", ["profile_id"]
    )

    # Risk
    op.create_table(
        "risk_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "hazard_model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id"),
            nullable=False,
        ),
        sa.Column("run_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("run_end", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("total_assessments", sa.Integer),
        sa.Column("completed_assessments", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_risk_runs_status", "risk_runs", ["status"])

    op.create_table(
        "risk_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "risk_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risk_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "grid_cell_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("grid_cells.id"),
            nullable=False,
        ),
        sa.Column(
            "hazard_assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hazard_assessments.id"),
            nullable=False,
        ),
        sa.Column(
            "vulnerability_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vulnerability_profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "exposure_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exposure_profiles.id"),
            nullable=False,
        ),
        sa.Column("valid_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hazard", sa.Float, nullable=False),
        sa.Column("vulnerability", sa.Float, nullable=False),
        sa.Column("exposure", sa.Float, nullable=False),
        sa.Column("hsri", sa.Float, nullable=False),
        sa.Column("risk_category", sa.String(20), nullable=False),
        sa.Column("calculation_metadata", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_risk_assessments_run_grid",
        "risk_assessments",
        ["risk_run_id", "grid_cell_id"],
    )
    op.create_index(
        "ix_risk_assessments_valid_time",
        "risk_assessments",
        ["valid_time"],
    )
    op.create_index(
        "ix_risk_assessments_category",
        "risk_assessments",
        ["risk_category"],
    )

    op.create_table(
        "risk_assessment_components",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "risk_assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risk_assessments.id"),
            nullable=False,
        ),
        sa.Column("component_type", sa.String(20), nullable=False),
        sa.Column("factor_name", sa.String(50), nullable=False),
        sa.Column("factor_value", sa.Float, nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("weighted_value", sa.Float, nullable=False),
        sa.Column("rank", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_risk_components_assessment",
        "risk_assessment_components",
        ["risk_assessment_id"],
    )

    op.create_table(
        "ward_risk_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "risk_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risk_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "ward_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wards.id"),
            nullable=False,
        ),
        sa.Column("valid_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mean_hazard", sa.Float, nullable=False),
        sa.Column("mean_vulnerability", sa.Float, nullable=False),
        sa.Column("mean_exposure", sa.Float, nullable=False),
        sa.Column("mean_hsri", sa.Float, nullable=False),
        sa.Column("max_hsri", sa.Float, nullable=False),
        sa.Column("min_hsri", sa.Float, nullable=False),
        sa.Column("risk_category", sa.String(20), nullable=False),
        sa.Column("cell_count", sa.Integer, nullable=False),
        sa.Column("high_risk_cell_count", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_ward_risk_summaries_run_ward",
        "ward_risk_summaries",
        ["risk_run_id", "ward_id"],
    )
    op.create_index(
        "ix_ward_risk_summaries_ward", "ward_risk_summaries", ["ward_id"]
    )

    # Operations
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "risk_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risk_runs.id"),
        ),
        sa.Column(
            "ward_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wards.id"),
        ),
        sa.Column("alert_level", sa.String(20), nullable=False),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("metadata_json", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_level", "alerts", ["alert_level"])
    op.create_index("ix_alerts_active", "alerts", ["is_active"])
    op.create_index(
        "ix_alerts_valid", "alerts", ["valid_from", "valid_until"]
    )

    op.create_table(
        "action_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alerts.id"),
            nullable=False,
        ),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("target_audience", sa.String(100)),
        sa.Column(
            "is_acknowledged", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_action_recommendations_alert",
        "action_recommendations",
        ["alert_id"],
    )

    # Additional indexes for query performance
    op.create_index(
        "ix_hazard_assessments_valid_time",
        "hazard_assessments",
        ["valid_time"],
    )
    op.create_index(
        "ix_risk_runs_start",
        "risk_runs",
        ["run_start"],
    )
    op.create_index(
        "ix_alerts_ward",
        "alerts",
        ["ward_id"],
    )
    op.create_index(
        "ix_vulnerability_factors_name",
        "vulnerability_factors",
        ["factor_name"],
    )
    op.create_index(
        "ix_exposure_factors_name",
        "exposure_factors",
        ["factor_name"],
    )
    op.create_index(
        "ix_risk_components_type",
        "risk_assessment_components",
        ["component_type"],
    )
    op.create_index(
        "ix_ward_risk_summaries_valid_time",
        "ward_risk_summaries",
        ["valid_time"],
    )


def downgrade() -> None:
    op.drop_index("ix_ward_risk_summaries_valid_time", "ward_risk_summaries")
    op.drop_index("ix_risk_components_type", "risk_assessment_components")
    op.drop_index("ix_exposure_factors_name", "exposure_factors")
    op.drop_index("ix_vulnerability_factors_name", "vulnerability_factors")
    op.drop_index("ix_alerts_ward", "alerts")
    op.drop_index("ix_risk_runs_start", "risk_runs")
    op.drop_index("ix_hazard_assessments_valid_time", "hazard_assessments")
    op.drop_index("ix_action_recommendations_alert", "action_recommendations")
    op.drop_table("action_recommendations")
    op.drop_table("alerts")
    op.drop_table("ward_risk_summaries")
    op.drop_table("risk_assessment_components")
    op.drop_table("risk_assessments")
    op.drop_table("risk_runs")
    op.drop_table("exposure_factors")
    op.drop_table("exposure_profiles")
    op.drop_table("vulnerability_factors")
    op.drop_table("vulnerability_profiles")
    op.drop_table("hazard_assessments")
    op.drop_table("model_runs")
    op.drop_table("scientific_models")
    op.drop_table("weather_forecasts")
    op.drop_table("weather_forecast_runs")
    op.drop_table("weather_observations")
    op.drop_table("weather_stations")
    op.drop_table("grid_cells")
    op.drop_table("wards")
    op.drop_table("cities")
    op.drop_table("states")
