"""Finite-sample rank calculation; exchangeability is a caller responsibility."""
from decimal import Decimal, ROUND_CEILING
import numpy as np
from .models import vector


def conformal_quantile(group_scores, alpha=0.1):
    scores = vector(group_scores, "group scores")
    if not 0 < alpha < 1 or np.any(scores < 0):
        raise ValueError("Alpha must be in (0,1); scores must be nonnegative")
    # Decimal prevents accidental ceil(9.000000000000002) rank inflation.
    rank = int((Decimal(len(scores)+1) * (1-Decimal(str(alpha)))).to_integral_value(rounding=ROUND_CEILING))
    if rank > len(scores):
        return float("inf")
    return float(np.partition(scores, rank-1)[rank-1])


def group_max_scores(y, mean, scale, groups, scale_floor=1e-6):
    y, mean, scale = vector(y, "y"), vector(mean, "mean"), vector(scale, "scale")
    groups = np.asarray(groups)
    if groups.ndim != 1 or not (len(y) == len(mean) == len(scale) == len(groups)):
        raise ValueError("Calibration arrays must align")
    if np.any(scale < 0) or not np.isfinite(scale_floor) or scale_floor <= 0:
        raise ValueError("Invalid predictive scale")
    if any(g is None or str(g) in ("", "nan") for g in groups):
        raise ValueError("Independent group identities required")
    residual = np.abs(y-mean) / np.maximum(scale, scale_floor)
    return np.array([residual[groups == g].max() for g in np.unique(groups)])
