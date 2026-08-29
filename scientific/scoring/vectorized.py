"""Vectorized scoring functions for vulnerability and exposure.

These functions accept both scalar and array-like inputs (NumPy arrays,
pandas Series) and return the same results as the scalar classifiers
in vulnerability/scoring.py and exposure/scoring.py.

Usage:
    import numpy as np
    from scientific.scoring.vectorized import vectorized_score_age

    ages = np.array([3, 15, 28, 50, 70])
    scores = vectorized_score_age(ages)
    # array([1.0, 0.66, 0.33, 0.66, 1.0])
"""
from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _to_numpy(arr: ArrayLike) -> NDArray[np.float64]:
    """Convert input to NumPy float64 array."""
    return np.asarray(arr, dtype=np.float64)


# ---------------------------------------------------------------------------
# Vulnerability vectorized classifiers
# ---------------------------------------------------------------------------

def vectorized_score_age(ages: ArrayLike) -> NDArray[np.float64]:
    """Vectorized age scoring.

    Boundary convention:
        age < 5          -> 1.00
        5 <= age < 24    -> 0.66
        24 <= age <= 40  -> 0.33
        40 < age <= 65   -> 0.66
        age > 65         -> 1.00
    """
    a = _to_numpy(ages)
    result = np.full_like(a, np.nan, dtype=np.float64)
    result[a < 5] = 1.0
    mask = (a >= 5) & (a < 24)
    result[mask] = 0.66
    mask = (a >= 24) & (a <= 40)
    result[mask] = 0.33
    mask = (a > 40) & (a <= 65)
    result[mask] = 0.66
    result[a > 65] = 1.0
    return result


def vectorized_score_bmi(bmis: ArrayLike) -> NDArray[np.float64]:
    """Vectorized BMI scoring.

    Boundary convention:
        < 17.0            -> 1.00
        17.0 <= bmi < 18.5 -> 0.66
        18.5 <= bmi < 25.0 -> 0.33
        25.0 <= bmi < 30.0 -> 0.66
        >= 30.0            -> 1.00
    """
    b = _to_numpy(bmis)
    result = np.full_like(b, np.nan, dtype=np.float64)
    result[b < 17.0] = 1.0
    mask = (b >= 17.0) & (b < 18.5)
    result[mask] = 0.66
    mask = (b >= 18.5) & (b < 25.0)
    result[mask] = 0.33
    mask = (b >= 25.0) & (b < 30.0)
    result[mask] = 0.66
    result[b >= 30.0] = 1.0
    return result


def vectorized_score_social_isolation(
    num_adults: ArrayLike,
) -> NDArray[np.float64]:
    """Vectorized social isolation scoring.

    Convention:
        > 1 other adult  -> 0.33
        == 1 other adult -> 0.66
        0 (living alone) -> 1.00
    """
    n = _to_numpy(num_adults).astype(np.float64)
    result = np.full_like(n, np.nan, dtype=np.float64)
    result[n > 1] = 0.33
    result[n == 1] = 0.66
    result[n == 0] = 1.0
    return result


# ---------------------------------------------------------------------------
# Exposure vectorized classifiers
# ---------------------------------------------------------------------------

def vectorized_score_fluid_intake(
    fluid_deficit_pcts: ArrayLike,
) -> NDArray[np.float64]:
    """Vectorized fluid intake scoring.

    Convention:
        deficit <= 4% -> 0.33 (meets requirement)
        deficit > 4%  -> 1.00 (dehydration risk)
    """
    f = _to_numpy(fluid_deficit_pcts)
    result = np.full_like(f, np.nan, dtype=np.float64)
    result[f <= 4.0] = 0.33
    result[f > 4.0] = 1.0
    return result


def vectorized_score_healthcare_access(
    travel_times: ArrayLike,
) -> NDArray[np.float64]:
    """Vectorized healthcare access scoring.

    Convention:
        < 30 min  -> 0.33
        30-60 min -> 0.66 (intermediate NOT YET SPECIFIED)
        > 60 min  -> 1.00
    """
    t = _to_numpy(travel_times)
    result = np.full_like(t, np.nan, dtype=np.float64)
    result[t < 30.0] = 0.33
    mask = (t >= 30.0) & (t <= 60.0)
    result[mask] = 0.66
    result[t > 60.0] = 1.0
    return result


# ---------------------------------------------------------------------------
# Hazard vectorized normalization
# ---------------------------------------------------------------------------

def vectorized_normalize_utci(
    utci_values: ArrayLike,
    bounds: list[tuple[float, float, float, float]],
) -> NDArray[np.float64]:
    """Vectorized UTCI to Hazard Index normalization.

    Args:
        utci_values: Array of UTCI values in Celsius.
        bounds: List of (utci_min, utci_max, h_min, h_max) tuples
                loaded from hazard_categories.yaml.

    Returns:
        Array of H values in [0, 1].
    """
    u = _to_numpy(utci_values)
    result = np.full_like(u, np.nan, dtype=np.float64)

    first_min = bounds[0][0]
    last_max = bounds[-1][1]

    # Valid range mask (excluding NaN)
    valid = ~np.isnan(u)

    # Below minimum -> 0.0
    mask_below = valid & (u <= first_min)
    result[mask_below] = 0.0

    # Above maximum -> 1.0
    mask_above = valid & (u >= last_max)
    result[mask_above] = 1.0

    # Within each band -> linear interpolation
    for utci_min, utci_max, h_min, h_max in bounds:
        mask = valid & (u > utci_min) & (u < utci_max)
        if np.any(mask):
            ratio = (u[mask] - utci_min) / (utci_max - utci_min)
            result[mask] = h_min + ratio * (h_max - h_min)

    return np.clip(result, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Weighted BBWM aggregation (vectorized)
# ---------------------------------------------------------------------------

def vectorized_weighted_sum(
    scores: dict[str, ArrayLike],
    weights: dict[str, float],
) -> NDArray[np.float64]:
    """Compute weighted sum for BBWM vulnerability or exposure.

    Args:
        scores: Dict mapping factor name to array of scores.
        weights: Dict mapping factor name to weight (must sum to ~1.0).

    Returns:
        Array of weighted sum values.
    """
    result = None
    for name, weight in weights.items():
        if name not in scores:
            raise ValueError(f"Missing score for factor: {name!r}")
        arr = _to_numpy(scores[name])
        if result is None:
            result = weight * arr
        else:
            result = result + weight * arr
    return result  # type: ignore[return-value]
