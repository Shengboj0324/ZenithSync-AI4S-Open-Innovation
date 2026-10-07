"""Retrospective measured-pool replay with a disjoint final-generation audit.

The pool is the observed support of the original study, not an exhaustive
experimental oracle. This evaluator cannot establish prospective policy value.
"""
import numpy as np
from .linear import ridge_posterior
from .multidimensional import design
from .models import vector
from .acquisition import integrated_variance_reduction


def replay(initial_x, initial_y, pool_x, pool_y, audit_x, audit_y, policy, seed=0, max_budget=10):
    initial_x, pool_x, audit_x = [design(v, name) for v, name in
                                 [(initial_x, "initial_x"), (pool_x, "pool_x"), (audit_x, "audit_x")]]
    initial_y, pool_y, audit_y = [vector(v, name) for v, name in
                                 [(initial_y, "initial_y"), (pool_y, "pool_y"), (audit_y, "audit_y")]]
    for x, y in [(initial_x, initial_y), (pool_x, pool_y), (audit_x, audit_y)]:
        if not len(x) or len(x) != len(y) or x.shape[1] != initial_x.shape[1]:
            raise ValueError("Replay arrays must be nonempty and aligned")
    if policy not in ("random", "space_filling", "ridge_variance"):
        raise ValueError("Unknown policy")
    if not isinstance(max_budget, int) or max_budget < 0:
        raise ValueError("Budget must be a nonnegative integer")
    rng, selected, trace = np.random.default_rng(seed), [], []
    for budget in range(min(max_budget, len(pool_x))+1):
        x = np.vstack([initial_x, pool_x[selected]]) if selected else initial_x
        y = np.r_[initial_y, pool_y[selected]] if selected else initial_y
        predictions, _ = ridge_posterior(x, y, audit_x)
        trace.append({"budget": budget, "selected_pool_indices": list(selected),
                      "audit_predictions": predictions.tolist(),
                      "audit_observations": audit_y.tolist(),
                      "rmse": float(np.sqrt(np.mean((predictions-audit_y)**2))),
                      "mae": float(np.mean(abs(predictions-audit_y)))})
        if budget == min(max_budget, len(pool_x)):
            break
        available = np.setdiff1d(np.arange(len(pool_x)), selected)
        if policy == "random":
            chosen = int(rng.choice(available))
        elif policy == "space_filling":
            distance = np.sum((pool_x[available, None, :]-x[None, :, :])**2, axis=2).min(axis=1)
            chosen = int(available[np.argmax(distance)])
        else:
            mean, covariance = ridge_posterior(x, y, pool_x)
            scores = integrated_variance_reduction(mean, covariance, np.full(len(pool_x), .01), np.ones(len(pool_x)))
            chosen = int(available[np.argmax(scores[available])])
        selected.append(chosen)
    return trace
