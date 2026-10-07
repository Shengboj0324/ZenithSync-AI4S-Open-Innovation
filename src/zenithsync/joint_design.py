"""Fixed-parameter Gaussian design with correlated observation noise.

Targets and candidate measurements are distinct random variables. Conditioning
updates their entire joint law, including future noise correlated with past
measurements. No independence shortcut, jitter, or submodularity is assumed.
"""
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy.linalg import cho_factor, cho_solve


def _indices(values, n, name):
    values = tuple(values)
    if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, np.integer))
           for v in values):
        raise ValueError(f"{name} must contain integer indices")
    if len(set(values)) != len(values) or any(v < 0 or v >= n for v in values):
        raise ValueError(f"{name} contains duplicate or out-of-range indices")
    return values


@dataclass(frozen=True)
class JointGaussian:
    """Joint latent/observation law; covariance is conditional on fixed parameters."""

    mean: np.ndarray
    covariance: np.ndarray

    def __post_init__(self):
        mean = np.array(self.mean, dtype=float, copy=True)
        covariance = np.array(self.covariance, dtype=float, copy=True)
        if mean.ndim != 1 or not len(mean) or covariance.shape != (len(mean), len(mean)):
            raise ValueError("Nonempty vector and aligned square covariance required")
        if not np.isfinite(mean).all() or not np.isfinite(covariance).all():
            raise ValueError("Joint law must be finite")
        scale = max(float(np.max(np.abs(covariance))), np.finfo(float).tiny)
        tolerance = 100 * np.finfo(float).eps * len(mean) * scale
        if np.max(np.abs(covariance-covariance.T)) > tolerance:
            raise ValueError("Covariance is not symmetric")
        covariance = (covariance+covariance.T)/2
        if np.linalg.eigvalsh(covariance).min() < -tolerance:
            raise ValueError("Covariance is not positive semidefinite")
        mean.setflags(write=False)
        covariance.setflags(write=False)
        object.__setattr__(self, "mean", mean)
        object.__setattr__(self, "covariance", covariance)

    def condition(self, observed, values):
        """Retain all coordinates; observed coordinates become deterministic.

        The supplied coordinates must refer to actual observation variables,
        with their noise already included in the joint law. Reobserving a
        deterministic coordinate raises rather than adding artificial noise.
        """
        observed = _indices(observed, len(self.mean), "observed")
        values = np.asarray(values, dtype=float)
        if values.shape != (len(observed),) or not np.isfinite(values).all():
            raise ValueError("Finite values must align with observations")
        if not observed:
            return self
        columns = self.covariance[:, observed]
        block = self.covariance[np.ix_(observed, observed)]
        try:
            factor = cho_factor(block, lower=True)
        except np.linalg.LinAlgError as error:
            raise ValueError("Observation block must be positive definite") from error
        innovation = values-self.mean[list(observed)]
        mean = self.mean+np.einsum("ij,j->i", columns, cho_solve(factor, innovation))
        covariance = self.covariance-np.einsum(
            "ik,kj->ij", columns, cho_solve(factor, columns.T))
        # These entries are analytically exact and avoid cancellation residuals.
        mean[list(observed)] = values
        covariance[list(observed), :] = 0
        covariance[:, list(observed)] = 0
        return JointGaussian(mean, covariance)

    def variance_reduction(self, targets, actions, weights):
        """Weighted reduction in latent target variance from a candidate batch."""
        targets = _indices(targets, len(self.mean), "targets")
        actions = _indices(actions, len(self.mean), "actions")
        if not targets or set(targets) & set(actions):
            raise ValueError("Nonempty targets must be distinct from observation actions")
        weights = np.asarray(weights, dtype=float)
        if (weights.shape != (len(targets),) or not np.isfinite(weights).all()
                or np.any(weights < 0) or not np.isclose(weights.sum(), 1, rtol=0, atol=1e-12)):
            raise ValueError("Weights must form a target probability vector")
        if not actions:
            return 0.0
        block = self.covariance[np.ix_(actions, actions)]
        cross = self.covariance[np.ix_(targets, actions)]
        try:
            factor = cho_factor(block, lower=True)
        except np.linalg.LinAlgError as error:
            raise ValueError("Action block must be positive definite") from error
        reduction = np.einsum("ij,ji->i", cross, cho_solve(factor, cross.T))
        return float(np.sum(weights*reduction))


def shared_control_noise(treatment_variances, control_groups, control_variances):
    """Noise of log treatment minus mean log control, as in Document 22.

    Group identifiers must be supplied from source metadata. Control variances
    describe the mean log control, not individual raw control measurements.
    """
    variances = np.asarray(treatment_variances, dtype=float)
    groups = tuple(control_groups)
    if (variances.ndim != 1 or not len(variances) or len(groups) != len(variances)
            or not np.isfinite(variances).all() or np.any(variances <= 0)):
        raise ValueError("Positive finite treatment variances and aligned groups required")
    if any(not isinstance(g, str) or not g for g in groups):
        raise ValueError("Explicit nonempty control-group identifiers required")
    if set(groups) != set(control_variances):
        raise ValueError("Control variances must exactly cover the used groups")
    result = np.diag(variances)
    for group, variance in control_variances.items():
        if not np.isscalar(variance) or not np.isfinite(variance) or variance < 0:
            raise ValueError("Control variances must be finite and nonnegative")
        member = np.asarray([g == group for g in groups], dtype=float)
        result += variance*np.outer(member, member)
    return result


def exact_budget_design(joint, targets, candidates, weights, costs, budget,
                        batch_ids=None, setup_costs=None, max_candidates=18):
    """Enumerate feasible subsets and maximize conditional variance reduction.

    Exact only over the provided finite candidate set, fixed Gaussian law and
    cost model. The empty set is admissible. Positive per-action costs plus
    optional per-batch setup charges are incremental costs in the same units.
    This routine deliberately refuses large enumerations rather than silently
    substituting an approximation. Mandatory controls belong in the caller's
    feasible action definition; they are not inferred here.
    """
    candidates = _indices(candidates, len(joint.mean), "candidates")
    targets = _indices(targets, len(joint.mean), "targets")
    if (isinstance(max_candidates, bool) or not isinstance(max_candidates, int)
            or max_candidates < 0 or max_candidates > 24 or len(candidates) > max_candidates):
        raise ValueError("Candidate set exceeds the explicitly bounded exhaustive search")
    if set(targets) & set(candidates):
        raise ValueError("Candidates must be observation coordinates distinct from targets")
    costs = np.asarray(costs, dtype=float)
    if (costs.shape != (len(candidates),) or not np.isfinite(costs).all()
            or np.any(costs <= 0) or not np.isfinite(budget) or budget < 0):
        raise ValueError("Positive aligned costs and finite nonnegative budget required")
    if (batch_ids is None) != (setup_costs is None):
        raise ValueError("Supply batch identifiers and setup costs together")
    if batch_ids is None:
        batch_ids, setup_costs = ("" for _ in candidates), {"": 0.0}
    batch_ids = tuple(batch_ids)
    if len(batch_ids) != len(candidates) or any(not isinstance(b, str) for b in batch_ids):
        raise ValueError("Batch identifiers must align with candidates")
    if not set(batch_ids).issubset(setup_costs):
        raise ValueError("Every batch requires an explicit setup cost")
    if any(not np.isscalar(v) or not np.isfinite(v) or v < 0 for v in setup_costs.values()):
        raise ValueError("Setup costs must be finite and nonnegative")
    best_actions, best_cost = (), 0.0
    best_gain = joint.variance_reduction(targets, (), weights)
    evaluated = 1
    for size in range(1, len(candidates)+1):
        for positions in combinations(range(len(candidates)), size):
            cost = float(sum(costs[p] for p in positions)
                         + sum(setup_costs[b] for b in {batch_ids[p] for p in positions}))
            if cost > budget:
                continue
            actions = tuple(candidates[p] for p in positions)
            gain = joint.variance_reduction(targets, actions, weights)
            evaluated += 1
            if gain > best_gain or (gain == best_gain and cost < best_cost):
                best_actions, best_cost, best_gain = actions, cost, gain
    return {"actions": best_actions, "cost": best_cost,
            "variance_reduction": best_gain, "feasible_subsets_evaluated": evaluated,
            "assurance": "exact finite-set fixed-Gaussian variance objective"}


def exact_cardinality_designs(joint, targets, candidates, weights, *, max_candidates=18):
    """Best set for every exact well count, enumerating each subset once.

    Every action must cost one equal unit and every subset must be feasible.
    Returned sets need not be nested: each is a separate fixed-budget campaign.
    """
    candidates = _indices(candidates, len(joint.mean), 'candidates')
    targets = _indices(targets, len(joint.mean), 'targets')
    if (isinstance(max_candidates, bool) or not isinstance(max_candidates, int)
            or max_candidates < 0 or max_candidates > 24 or len(candidates) > max_candidates):
        raise ValueError('Candidate set exceeds the explicitly bounded exhaustive search')
    if set(candidates) & set(targets):
        raise ValueError('Actions and targets must be distinct')
    empty_gain = joint.variance_reduction(targets, (), weights)
    results = [{'actions': (), 'variance_reduction': empty_gain, 'subsets_evaluated': 1}]
    for count in range(1, len(candidates)+1):
        best_actions, best_gain, evaluated = None, -np.inf, 0
        for actions in combinations(candidates, count):
            gain = joint.variance_reduction(targets, actions, weights)
            evaluated += 1
            if gain > best_gain:
                best_actions, best_gain = actions, gain
        results.append({'actions': best_actions, 'variance_reduction': best_gain,
                        'subsets_evaluated': evaluated})
    return results
