"""Stable Gaussian likelihood contributions for observed and censored values.

These functions are numerical primitives, not a fitted censoring-aware model.
"""
import numpy as np
from scipy.special import log_ndtr


def gaussian_log_probability(lower, upper, mean=0.0, sd=1.0):
    """Log P(lower < Y <= upper), including one-sided infinite boundaries."""
    lower, upper, mean, sd = np.broadcast_arrays(
        np.asarray(lower, float), np.asarray(upper, float),
        np.asarray(mean, float), np.asarray(sd, float))
    if np.any(np.isnan(lower)) or np.any(np.isnan(upper)) or np.any(lower >= upper):
        raise ValueError("Interval bounds must be ordered and not NaN")
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(sd)) or np.any(sd <= 0):
        raise ValueError("Gaussian mean and SD must be finite; SD positive")
    a, b = (lower-mean)/sd, (upper-mean)/sd
    # In the right tail subtract survival probabilities, avoiding CDF saturation.
    right = a > 0
    log_large = np.where(right, log_ndtr(-a), log_ndtr(b))
    log_small = np.where(right, log_ndtr(-b), log_ndtr(a))
    with np.errstate(divide="ignore", invalid="raise"):
        result = log_large + np.log(-np.expm1(log_small-log_large))
    return result
