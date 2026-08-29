"""UTCI thermal comfort model — polynomial approximation.

Implementation based on the UTCI multi-dimensional polynomial regression
from Fiala et al. (2012), using the exact coefficient set from
pythermalcomfort (licensed BSD-3).

The polynomial uses variables:
    tdb  = air temperature (°C)
    v    = wind speed (m/s)
    delta_t_tr = Tmrt - Tdb (mean radiant temp minus air temp)
    pa   = water vapour pressure (kPa)

Result: UTCI = tdb + polynomial(tdb, v, delta_t_tr, pa)

Reference:
    Fiala D, Havenith G, Bröde P, Kampmann B, Jendritzky G. (2012).
    UTCI-Fiala multi-node model of human heat transfer and temperature
    regulation. Int J Biometeorol. 56:429-441.

    pythermalcomfort library (BSD-3 licensed):
    https://github.com/PMontero-Macias/pythermalcomfort
"""
from __future__ import annotations

import math

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scientific.thermal_comfort.base import ThermalComfortModel


class UTCIInput(BaseModel):
    """Meteorological inputs required for UTCI calculation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    air_temperature: float = Field(
        ...,
        description="Air temperature in degrees Celsius.",
    )
    relative_humidity: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Relative humidity in percentage (0-100).",
    )
    wind_speed: float = Field(
        ...,
        ge=0.0,
        description="Wind speed in m/s at 10 m height.",
    )
    mean_radiant_temperature: float = Field(
        ...,
        description="Mean radiant temperature in degrees Celsius.",
    )

    @model_validator(mode="after")
    def validate_ranges(self) -> UTCIInput:
        if not (-50.0 <= self.air_temperature <= 50.0):
            raise ValueError(
                f"Air temperature must be in [-50, 50]°C, got {self.air_temperature}"
            )
        if not (self.air_temperature - 30 <= self.mean_radiant_temperature <= self.air_temperature + 70):
            raise ValueError(
                f"Mean radiant temperature must be in [Ta-30, Ta+70], "
                f"got {self.mean_radiant_temperature} for Ta={self.air_temperature}"
            )
        if not (0.5 <= self.wind_speed <= 17.0):
            raise ValueError(
                f"Wind speed must be in [0.5, 17.0] m/s, got {self.wind_speed}"
            )
        ea = _vapour_pressure_hpa(self.air_temperature, self.relative_humidity)
        if ea > 50.0:
            raise ValueError(
                f"Water vapour pressure must be <= 50 hPa, got {ea:.1f}"
            )
        return self


class UTCIOutput(BaseModel):
    """Result from UTCI calculation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    utci_c: float = Field(
        ...,
        description="Universal Thermal Climate Index in degrees Celsius.",
    )
    air_temperature: float
    relative_humidity: float
    wind_speed: float
    mean_radiant_temperature: float
    wind_clamped: bool = Field(
        default=False,
        description="True if wind speed was clamped from < 0.5 m/s to 0.5 m/s.",
    )
    original_wind_speed: float | None = Field(
        default=None,
        description="Original wind speed before clamping (if clamping occurred).",
    )


def _vapour_pressure_hpa(ta: float, rh: float) -> float:
    """Calculate water vapour pressure from air temperature and RH.

    Uses the Buck (1981) equation.
    """
    es = 6.1121 * math.exp((18.678 - ta / 234.5) * (ta / (257.14 + ta)))
    return es * rh / 100.0


def _saturated_vapour_pressure(tk: float) -> float:
    """Calculate saturated vapour pressure using the exponential formula.

    Uses the same formulation as pythermalcomfort.
    """
    g = [
        -2836.5744,
        -6028.076559,
        19.54263612,
        -0.02737830188,
        0.000016261698,
        7.0229056e-10,
        -1.8680009e-13,
    ]
    es = 2.7150305 * math.log(tk)
    for count, i in enumerate(g):
        es = es + (i * tk ** (count - 2))
    return math.exp(es) * 0.01  # Pa to hPa


def _utci_polynomial(tdb: float, v: float, delta_t_tr: float, pa: float) -> float:
    """Compute UTCI using the polynomial approximation from pythermalcomfort.

    Args:
        tdb: Air temperature (°C)
        v: Wind speed (m/s)
        delta_t_tr: Mean radiant temp minus air temp (°C)
        pa: Water vapour pressure (kPa)

    Returns:
        UTCI increment to add to tdb
    """
    return (
        0.607562052
        + (-0.0227712343) * tdb
        + (8.06470249e-4) * tdb ** 2
        + (-1.54271372e-4) * tdb ** 3
        + (-3.24651735e-6) * tdb ** 4
        + (7.32602852e-8) * tdb ** 5
        + (1.35959073e-9) * tdb ** 6
        + (-2.25836520) * v
        + 0.0880326035 * tdb * v
        + 0.00216844454 * tdb ** 2 * v
        + (-1.53347087e-5) * tdb ** 3 * v
        + (-5.72983704e-7) * tdb ** 4 * v
        + (-2.55090145e-9) * tdb ** 5 * v
        + (-0.751269505) * v ** 2
        + (-0.00408350271) * tdb * v ** 2
        + (-5.21670675e-5) * tdb ** 2 * v ** 2
        + (1.94544667e-6) * tdb ** 3 * v ** 2
        + (1.14099531e-8) * tdb ** 4 * v ** 2
        + 0.158137256 * v ** 3
        + (-6.57263143e-5) * tdb * v ** 3
        + (2.22697524e-7) * tdb ** 2 * v ** 3
        + (-4.16117031e-8) * tdb ** 3 * v ** 3
        + (-0.0127762753) * v ** 4
        + (9.66891875e-6) * tdb * v ** 4
        + (2.52785852e-9) * tdb ** 2 * v ** 4
        + (4.56306672e-4) * v ** 5
        + (-1.74202546e-7) * tdb * v ** 5
        + (-5.91491269e-6) * v ** 6
        + 0.398374029 * delta_t_tr
        + (1.83945314e-4) * tdb * delta_t_tr
        + (-1.73754510e-4) * tdb ** 2 * delta_t_tr
        + (-7.60781159e-7) * tdb ** 3 * delta_t_tr
        + (3.77830287e-8) * tdb ** 4 * delta_t_tr
        + (5.43079673e-10) * tdb ** 5 * delta_t_tr
        + (-0.0200518269) * v * delta_t_tr
        + (8.92859837e-4) * tdb * v * delta_t_tr
        + (3.45433048e-6) * tdb ** 2 * v * delta_t_tr
        + (-3.77925774e-7) * tdb ** 3 * v * delta_t_tr
        + (-1.69699377e-9) * tdb ** 4 * v * delta_t_tr
        + (1.69992415e-4) * v ** 2 * delta_t_tr
        + (-4.99204314e-5) * tdb * v ** 2 * delta_t_tr
        + (2.47417178e-7) * tdb ** 2 * v ** 2 * delta_t_tr
        + (1.07596466e-8) * tdb ** 3 * v ** 2 * delta_t_tr
        + (8.49242932e-5) * v ** 3 * delta_t_tr
        + (1.35191328e-6) * tdb * v ** 3 * delta_t_tr
        + (-6.21531254e-9) * tdb ** 2 * v ** 3 * delta_t_tr
        + (-4.99410301e-6) * v ** 4 * delta_t_tr
        + (-1.89489258e-8) * tdb * v ** 4 * delta_t_tr
        + (8.15300114e-8) * v ** 5 * delta_t_tr
        + (7.55043090e-4) * delta_t_tr ** 2
        + (-5.65095215e-5) * tdb * delta_t_tr ** 2
        + (-4.52166564e-7) * tdb ** 2 * delta_t_tr ** 2
        + (2.46688878e-8) * tdb ** 3 * delta_t_tr ** 2
        + (2.42674348e-10) * tdb ** 4 * delta_t_tr ** 2
        + (1.54547250e-4) * v * delta_t_tr ** 2
        + (5.24110970e-6) * tdb * v * delta_t_tr ** 2
        + (-8.75874982e-8) * tdb ** 2 * v * delta_t_tr ** 2
        + (-1.50743064e-9) * tdb ** 3 * v * delta_t_tr ** 2
        + (-1.56236307e-5) * v ** 2 * delta_t_tr ** 2
        + (-1.33895614e-7) * tdb * v ** 2 * delta_t_tr ** 2
        + (2.49709824e-9) * tdb ** 2 * v ** 2 * delta_t_tr ** 2
        + (6.51711721e-7) * v ** 3 * delta_t_tr ** 2
        + (1.94960053e-9) * tdb * v ** 3 * delta_t_tr ** 2
        + (-1.00361113e-8) * v ** 4 * delta_t_tr ** 2
        + (-1.21206673e-5) * delta_t_tr ** 3
        + (-2.18203660e-7) * tdb * delta_t_tr ** 3
        + (7.51269482e-9) * tdb ** 2 * delta_t_tr ** 3
        + (9.79063848e-11) * tdb ** 3 * delta_t_tr ** 3
        + (1.25006734e-6) * v * delta_t_tr ** 3
        + (-1.81584736e-9) * tdb * v * delta_t_tr ** 3
        + (-3.52197671e-10) * tdb ** 2 * v * delta_t_tr ** 3
        + (-3.36514630e-8) * v ** 2 * delta_t_tr ** 3
        + (1.35908359e-10) * tdb * v ** 2 * delta_t_tr ** 3
        + (4.17032620e-10) * v ** 3 * delta_t_tr ** 3
        + (-1.30369025e-9) * delta_t_tr ** 4
        + (4.13908461e-10) * tdb * delta_t_tr ** 4
        + (9.22652254e-12) * tdb ** 2 * delta_t_tr ** 4
        + (-5.08220384e-9) * v * delta_t_tr ** 4
        + (-2.24730961e-11) * tdb * v * delta_t_tr ** 4
        + (1.17139133e-10) * v ** 2 * delta_t_tr ** 4
        + (6.62154879e-10) * delta_t_tr ** 5
        + (4.03863260e-13) * tdb * delta_t_tr ** 5
        + (1.95087203e-12) * v * delta_t_tr ** 5
        + (-4.73602469e-12) * delta_t_tr ** 6
        + 5.12733497 * pa
        + (-0.312788561) * tdb * pa
        + (-0.0196701861) * tdb ** 2 * pa
        + (9.99690870e-4) * tdb ** 3 * pa
        + (9.51738512e-6) * tdb ** 4 * pa
        + (-4.66426341e-7) * tdb ** 5 * pa
        + 0.548050612 * v * pa
        + (-0.00330552823) * tdb * v * pa
        + (-0.00164119440) * tdb ** 2 * v * pa
        + (-5.16670694e-6) * tdb ** 3 * v * pa
        + (9.52692432e-7) * tdb ** 4 * v * pa
        + (-0.0429223622) * v ** 2 * pa
        + 0.00500845667 * tdb * v ** 2 * pa
        + (1.00601257e-6) * tdb ** 2 * v ** 2 * pa
        + (-1.81748644e-6) * tdb ** 3 * v ** 2 * pa
        + (-1.25813502e-3) * v ** 3 * pa
        + (-1.79330391e-4) * tdb * v ** 3 * pa
        + (2.34994441e-6) * tdb ** 2 * v ** 3 * pa
        + (1.29735808e-4) * v ** 4 * pa
        + (1.29064870e-6) * tdb * v ** 4 * pa
        + (-2.28558686e-6) * v ** 5 * pa
        + (-0.0369476348) * delta_t_tr * pa
        + 0.00162325322 * tdb * delta_t_tr * pa
        + (-3.14279680e-5) * tdb ** 2 * delta_t_tr * pa
        + (2.59835559e-6) * tdb ** 3 * delta_t_tr * pa
        + (-4.77136523e-8) * tdb ** 4 * delta_t_tr * pa
        + (8.64203390e-3) * v * delta_t_tr * pa
        + (-6.87405181e-4) * tdb * v * delta_t_tr * pa
        + (-9.13863872e-6) * tdb ** 2 * v * delta_t_tr * pa
        + (5.15916806e-7) * tdb ** 3 * v * delta_t_tr * pa
        + (-3.59217476e-5) * v ** 2 * delta_t_tr * pa
        + (3.28696511e-5) * tdb * v ** 2 * delta_t_tr * pa
        + (-7.10542454e-7) * tdb ** 2 * v ** 2 * delta_t_tr * pa
        + (-1.24382300e-5) * v ** 3 * delta_t_tr * pa
        + (-7.38584400e-9) * tdb * v ** 3 * delta_t_tr * pa
        + (2.20609296e-7) * v ** 4 * delta_t_tr * pa
        + (-7.32469180e-4) * delta_t_tr ** 2 * pa
        + (-1.87381964e-5) * tdb * delta_t_tr ** 2 * pa
        + (4.80925239e-6) * tdb ** 2 * delta_t_tr ** 2 * pa
        + (-8.75492040e-8) * tdb ** 3 * delta_t_tr ** 2 * pa
        + (2.77862930e-5) * v * delta_t_tr ** 2 * pa
        + (-5.06004592e-6) * tdb * v * delta_t_tr ** 2 * pa
        + (1.14325367e-7) * tdb ** 2 * v * delta_t_tr ** 2 * pa
        + (2.53016723e-6) * v ** 2 * delta_t_tr ** 2 * pa
        + (-1.72857035e-8) * tdb * v ** 2 * delta_t_tr ** 2 * pa
        + (-3.95079398e-8) * v ** 3 * delta_t_tr ** 2 * pa
        + (-3.59413173e-7) * delta_t_tr ** 3 * pa
        + (7.04388046e-7) * tdb * delta_t_tr ** 3 * pa
        + (-1.89309167e-8) * tdb ** 2 * delta_t_tr ** 3 * pa
        + (-4.79768731e-7) * v * delta_t_tr ** 3 * pa
        + (7.96079978e-9) * tdb * v * delta_t_tr ** 3 * pa
        + (1.62897058e-9) * v ** 2 * delta_t_tr ** 3 * pa
        + (3.94367674e-8) * delta_t_tr ** 4 * pa
        + (-1.18566247e-9) * tdb * delta_t_tr ** 4 * pa
        + (3.34678041e-10) * v * delta_t_tr ** 4 * pa
        + (-1.15606447e-10) * delta_t_tr ** 5 * pa
        + (-2.80626406) * pa ** 2
        + 0.548712484 * tdb * pa ** 2
        + (-0.00399428410) * tdb ** 2 * pa ** 2
        + (-9.54009191e-4) * tdb ** 3 * pa ** 2
        + (1.93090978e-5) * tdb ** 4 * pa ** 2
        + (-0.308806365) * v * pa ** 2
        + 0.0116952364 * tdb * v * pa ** 2
        + (4.95271903e-4) * tdb ** 2 * v * pa ** 2
        + (-1.90710882e-5) * tdb ** 3 * v * pa ** 2
        + 0.00210787756 * v ** 2 * pa ** 2
        + (-6.98445738e-4) * tdb * v ** 2 * pa ** 2
        + (2.30109073e-5) * tdb ** 2 * v ** 2 * pa ** 2
        + (4.17856590e-4) * v ** 3 * pa ** 2
        + (-1.27043871e-5) * tdb * v ** 3 * pa ** 2
        + (-3.04620472e-6) * v ** 4 * pa ** 2
        + 0.0514507424 * delta_t_tr * pa ** 2
        + (-0.00432510997) * tdb * delta_t_tr * pa ** 2
        + (8.99281156e-5) * tdb ** 2 * delta_t_tr * pa ** 2
        + (-7.14663943e-7) * tdb ** 3 * delta_t_tr * pa ** 2
        + (-2.66016305e-4) * v * delta_t_tr * pa ** 2
        + (2.63789586e-4) * tdb * v * delta_t_tr * pa ** 2
        + (-7.01199003e-6) * tdb ** 2 * v * delta_t_tr * pa ** 2
        + (-1.06823306e-4) * v ** 2 * delta_t_tr * pa ** 2
        + (3.61341136e-6) * tdb * v ** 2 * delta_t_tr * pa ** 2
        + (2.29748967e-7) * v ** 3 * delta_t_tr * pa ** 2
        + (3.04788893e-4) * delta_t_tr ** 2 * pa ** 2
        + (-6.42070836e-5) * tdb * delta_t_tr ** 2 * pa ** 2
        + (1.16257971e-6) * tdb ** 2 * delta_t_tr ** 2 * pa ** 2
        + (7.68023384e-6) * v * delta_t_tr ** 2 * pa ** 2
        + (-5.47446896e-7) * tdb * v * delta_t_tr ** 2 * pa ** 2
        + (-3.59937910e-8) * v ** 2 * delta_t_tr ** 2 * pa ** 2
        + (-4.36497725e-6) * delta_t_tr ** 3 * pa ** 2
        + (1.68737969e-7) * tdb * delta_t_tr ** 3 * pa ** 2
        + (2.67489271e-8) * v * delta_t_tr ** 3 * pa ** 2
        + (3.23926897e-9) * delta_t_tr ** 4 * pa ** 2
        + (-0.0353874123) * pa ** 3
        + (-0.221201190) * tdb * pa ** 3
        + 0.0155126038 * tdb ** 2 * pa ** 3
        + (-2.63917279e-4) * tdb ** 3 * pa ** 3
        + 0.0453433455 * v * pa ** 3
        + (-0.00432943862) * tdb * v * pa ** 3
        + (1.45389826e-4) * tdb ** 2 * v * pa ** 3
        + (2.17508610e-4) * v ** 2 * pa ** 3
        + (-6.66724702e-5) * tdb * v ** 2 * pa ** 3
        + (3.33217140e-5) * v ** 3 * pa ** 3
        + (-0.00226921615) * delta_t_tr * pa ** 3
        + (3.80261982e-4) * tdb * delta_t_tr * pa ** 3
        + (-5.45314314e-9) * tdb ** 2 * delta_t_tr * pa ** 3
        + (-7.96355448e-4) * v * delta_t_tr * pa ** 3
        + (2.53458034e-5) * tdb * v * delta_t_tr * pa ** 3
        + (-6.31223658e-6) * v ** 2 * delta_t_tr * pa ** 3
        + (3.02122035e-4) * delta_t_tr ** 2 * pa ** 3
        + (-4.77403547e-6) * tdb * delta_t_tr ** 2 * pa ** 3
        + (1.73825715e-6) * v * delta_t_tr ** 2 * pa ** 3
        + (-4.09087898e-7) * delta_t_tr ** 3 * pa ** 3
        + 0.614155345 * pa ** 4
        + (-0.0616755931) * tdb * pa ** 4
        + 0.00133374846 * tdb ** 2 * pa ** 4
        + 0.00355375387 * v * pa ** 4
        + (-5.13027851e-4) * tdb * v * pa ** 4
        + (1.02449757e-4) * v ** 2 * pa ** 4
        + (-0.00148526421) * delta_t_tr * pa ** 4
        + (-4.11469183e-5) * tdb * delta_t_tr * pa ** 4
        + (-6.80434415e-6) * v * delta_t_tr * pa ** 4
        + (-9.77675906e-6) * delta_t_tr ** 2 * pa ** 4
        + 0.0882773108 * pa ** 5
        + (-0.00301859306) * tdb * pa ** 5
        + 0.00104452989 * v * pa ** 5
        + (2.47090539e-4) * delta_t_tr * pa ** 5
        + 0.00148348065 * pa ** 6
    )


def calculate_utci(
    air_temperature: float,
    relative_humidity: float,
    wind_speed: float,
    mean_radiant_temperature: float,
) -> UTCIOutput:
    """Calculate UTCI from meteorological inputs.

    Uses the UTCI polynomial approximation from Fiala et al. (2012)
    via the pythermalcomfort coefficient set.

    Calm-wind policy:
        If wind_speed < 0.5 m/s, it is clamped to 0.5 m/s and a quality
        flag (wind_clamped=True) is recorded. The original wind speed is
        preserved for reference.

    Args:
        air_temperature: Air temperature in C
        relative_humidity: Relative humidity in % (0-100)
        wind_speed: Wind speed in m/s at 10m height
        mean_radiant_temperature: Mean radiant temperature in C

    Returns:
        UTCIOutput with UTCI value, input echoes, and quality flags

    Raises:
        ValueError: If inputs are outside valid ranges.
    """
    if not (-50.0 <= air_temperature <= 50.0):
        raise ValueError(
            f"Air temperature must be in [-50, 50]C, got {air_temperature}"
        )
    if not (0.0 <= relative_humidity <= 100.0):
        raise ValueError(
            f"Relative humidity must be in [0, 100]%, got {relative_humidity}"
        )
    if not (air_temperature - 30 <= mean_radiant_temperature <= air_temperature + 70):
        raise ValueError(
            f"Mean radiant temperature must be in [Ta-30, Ta+70], "
            f"got {mean_radiant_temperature} for Ta={air_temperature}"
        )
    ea = _vapour_pressure_hpa(air_temperature, relative_humidity)
    if ea > 50.0:
        raise ValueError(
            f"Water vapour pressure must be <= 50 hPa, got {ea:.1f}"
        )

    # Calm-wind policy: clamp wind speed < 0.5 m/s to 0.5 m/s
    wind_clamped = False
    original_wind_speed = None
    if wind_speed < 0.5:
        original_wind_speed = wind_speed
        wind_speed = 0.5
        wind_clamped = True

    if not (0.5 <= wind_speed <= 17.0):
        raise ValueError(
            f"Wind speed must be in [0.5, 17.0] m/s, got {wind_speed}"
        )

    tk = air_temperature + 273.15
    eh_pa = _saturated_vapour_pressure(tk) * (relative_humidity / 100.0)
    pa = eh_pa / 10.0  # hPa to kPa

    delta_t_tr = mean_radiant_temperature - air_temperature

    utci = air_temperature + _utci_polynomial(
        air_temperature, wind_speed, delta_t_tr, pa
    )

    return UTCIOutput(
        utci_c=round(utci, 1),
        air_temperature=air_temperature,
        relative_humidity=relative_humidity,
        wind_speed=wind_speed,
        mean_radiant_temperature=mean_radiant_temperature,
        wind_clamped=wind_clamped,
        original_wind_speed=original_wind_speed,
    )


# ---------------------------------------------------------------------------
# Concrete Phase-1 interface implementation
# ---------------------------------------------------------------------------

class UTCICalculatorModel(ThermalComfortModel):
    """Configuration-driven UTCI calculator using polynomial approximation.

    Implements the Fiala et al. (2012) UTCI polynomial regression
    using the pythermalcomfort coefficient set (BSD-3 licensed).
    """

    @property
    def model_name(self) -> str:
        return "utci-polynomial-v1"

    @property
    def model_version(self) -> str:
        return "1.0.0"

    def calculate_utci(
        self,
        air_temperature: float,
        relative_humidity: float,
        wind_speed: float,
        mean_radiant_temperature: float,
    ) -> UTCIOutput:
        return calculate_utci(
            air_temperature=air_temperature,
            relative_humidity=relative_humidity,
            wind_speed=wind_speed,
            mean_radiant_temperature=mean_radiant_temperature,
        )

    def get_hazard_index(self, utci: float) -> float:
        """Convert UTCI to normalized hazard index."""
        from scientific.hazard.utci.normalization import normalize_utci
        return normalize_utci(utci)
