"""Measured-pool exploration with held-out dose outcomes hidden from policies.

The policy receives observations only after selection. The audit outcome is
never supplied to the policy. Query coordinates are available by design.
"""
from dataclasses import dataclass
import numpy as np
from .models import GaussianProcess, vector
from .acquisition import integrated_variance_reduction, decision_voi, decision_voi_adaptive, threshold_probability


@dataclass
class Selection:
    index: int
    score: float
    quadrature_difference: float = 0.0


def select_next(x, observed_indices, observed_y, policy, rng, noise_variance=400.0, gp=None):
    x, observed_y = vector(x, "x"), vector(observed_y, "observed_y")
    indices = np.asarray(observed_indices)
    if indices.ndim != 1 or indices.dtype.kind not in "iu" or len(indices) != len(observed_y):
        raise ValueError("Observed integer indices must align with revealed outcomes")
    if len(set(indices)) != len(indices) or np.any(indices < 0) or np.any(indices >= len(x)):
        raise ValueError("Observed indices must be unique and in bounds")
    if not np.isfinite(noise_variance) or noise_variance <= 0:
        raise ValueError("Noise variance must be positive")
    available = np.setdiff1d(np.arange(len(x)), indices)
    if not len(available):
        raise ValueError("No remaining measured-pool candidates")
    if policy == "random":
        return Selection(int(rng.choice(available)), float(1/len(available)))
    if policy == "space_filling":
        distances = np.min(np.abs(x[available, None]-x[indices][None, :]), axis=1) if len(indices) else np.ones(len(available))
        j = int(np.argmax(distances))
        return Selection(int(available[j]), float(distances[j]))
    gp = GaussianProcess() if gp is None else gp
    mean, covariance = gp.posterior(x[indices], observed_y,
                                                  np.full(len(indices), noise_variance), x)
    noise, cost = np.full(len(x), noise_variance), np.ones(len(x))
    discrepancy = 0.0
    if policy == "integrated_variance":
        scores = integrated_variance_reduction(mean, covariance, noise, cost)
    elif policy == "decision_voi_adaptive":
        scores, errors = decision_voi_adaptive(mean, covariance, noise, cost)
        discrepancy = float(np.max(errors))
    elif policy == "decision_voi":
        low = decision_voi(mean, covariance, noise, cost, nodes=96)
        scores = decision_voi(mean, covariance, noise, cost, nodes=192)
        discrepancy = float(np.max(np.abs(scores-low)))
        if discrepancy > 0.003:
            refined = decision_voi(mean, covariance, noise, cost, nodes=768)
            discrepancy = float(np.max(np.abs(refined-scores)))
            scores = refined
            if discrepancy > 0.003:
                raise ArithmeticError("Decision VOI quadrature has not stabilized")
        if np.min(scores) < -0.003:
            raise ArithmeticError("Negative VOI exceeds numerical tolerance")
    else:
        raise ValueError(f"Unknown policy: {policy}")
    j = int(available[np.argmax(scores[available])])
    return Selection(j, float(scores[j]), discrepancy)


def replay_curve(x, outcomes, audit_index, policy, seed=0, noise_variance=400.0, gp=None):
    x, outcomes = vector(x, "x"), vector(outcomes, "outcomes")
    if len(x) != len(outcomes) or len(x) < 4 or len(np.unique(x)) != len(x):
        raise ValueError("Replay requires at least four unique measured doses")
    if not isinstance(audit_index, (int, np.integer)) or not 0 <= audit_index < len(x):
        raise ValueError("Audit index outside curve")
    if not np.isfinite(noise_variance) or noise_variance <= 0:
        raise ValueError("Noise variance must be positive")
    gp = GaussianProcess() if gp is None else gp
    pool = np.delete(np.arange(len(x)), audit_index)
    pool = pool[np.argsort(x[pool])]
    # Fixed endpoint initialization uses input coordinates, never outcome values.
    selected = [0, len(pool)-1]
    revealed = [float(outcomes[pool[i]]) for i in selected]
    rng, trace = np.random.default_rng(seed), []
    latest = None
    while True:
        mean, covariance = gp.posterior(x[pool[selected]], revealed,
                                                       np.full(len(selected), noise_variance), [x[audit_index]])
        probability = float(threshold_probability(mean, np.diag(covariance), 50)[0])
        trace.append({"budget": len(selected), "selected_indices": pool[selected].tolist(),
                      "revealed_outcomes": list(revealed), "audit_index": int(audit_index),
                      "prediction": float(mean[0]), "latent_sd": float(np.sqrt(max(0, covariance[0, 0]))),
                      "probability_below_50": probability,
                      "observed_audit_mean": float(outcomes[audit_index]),
                      "squared_error": float((mean[0]-outcomes[audit_index])**2),
                      "threshold_error": int((probability > .5) != (outcomes[audit_index] < 50)),
                      "last_acquisition_score": None if latest is None else latest.score,
                      "quadrature_difference": 0.0 if latest is None else latest.quadrature_difference})
        if len(selected) == len(pool):
            break
        latest = select_next(x[pool], selected, revealed, policy, rng, noise_variance, gp=gp)
        selected.append(latest.index)
        revealed.append(float(outcomes[pool[latest.index]]))
    return trace
