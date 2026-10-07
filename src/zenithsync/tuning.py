"""Training-only model selection with dose-group isolation.

Outer test rows must never be passed to these functions. Inner folds remove all
replicates at the same dose. The objective weights dose groups equally, avoiding
extra influence from conditions with more surviving replicate rows.
"""
from dataclasses import asdict
from itertools import product
import numpy as np
from scipy.interpolate import PchipInterpolator
from .models import GaussianProcess, vector


def gp_candidates():
    return [(GaussianProcess(amplitude=a, length_scale=l, mean=m), noise)
            for a, l, m, noise in product((25., 50., 100.), (.5, 1.5, 4.),
                                          (100.,), (10., 20., 40.))]


def tune_gp(x, y, candidates=None):
    x, y = vector(x, "x"), vector(y, "y")
    if len(x) != len(y) or len(np.unique(x)) < 3:
        raise ValueError("Tuning needs aligned observations at at least three distinct doses")
    candidates = gp_candidates() if candidates is None else list(candidates)
    if not candidates:
        raise ValueError("Candidate set cannot be empty")
    records = []
    for gp, noise_sd in candidates:
        if not np.isfinite(noise_sd) or noise_sd <= 0:
            raise ValueError("Candidate noise SD must be finite and positive")
        losses = []
        for held_x in np.unique(x):
            train = x != held_x
            mean, _ = gp.posterior(x[train], y[train], np.full(train.sum(), noise_sd**2), x[~train])
            losses.append(float(np.mean((mean-y[~train])**2)))
        records.append({"gp": asdict(gp), "noise_sd": float(noise_sd),
                        "inner_dose_mse": losses, "mean_inner_mse": float(np.mean(losses))})
    selected = int(np.argmin([r["mean_inner_mse"] for r in records]))
    return candidates[selected][0], candidates[selected][1], {
        "selected_index": selected, "candidates": records,
        "inner_group_count": len(np.unique(x)), "selection_rule": "minimum_dose_macro_mse_stable_first_tie"}


def interpolate_curve(x, y, query, method="linear"):
    """Dose means with explicit constant extension outside the observed range."""
    x, y, query = vector(x, "x"), vector(y, "y"), vector(query, "query")
    if len(x) != len(y) or len(np.unique(x)) < 2:
        raise ValueError("Interpolation needs two distinct observed doses")
    unique = np.unique(x)
    means = np.array([y[x == value].mean() for value in unique])
    if method == "linear":
        return np.interp(query, unique, means)
    if method == "pchip":
        return PchipInterpolator(unique, means)(np.clip(query, unique.min(), unique.max()))
    raise ValueError("Unknown interpolation method")
