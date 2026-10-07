"""Outcome-independent designs and batched evaluators for the frozen protocol."""
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import cho_factor, cho_solve

from .contrast_gp import ContrastGP
from .symmetric_design import exact_exchangeable_designs


@dataclass
class Plan:
    method: str
    budget: int
    seed: int
    selected: tuple
    weights: np.ndarray | None
    offset: np.ndarray | None
    variance: np.ndarray | None


def gp_plan(prior, target_count, selected, method, seed=-1):
    observed = [target_count+i-1 for i in selected if i != 0]
    cross = prior.covariance[:target_count, observed]
    block = prior.covariance[np.ix_(observed, observed)]
    weights = cho_solve(cho_factor(block, lower=True), cross.T).T
    offset = prior.mean[:target_count]-np.einsum('ij,j->i', weights, prior.mean[observed])
    variance = np.diag(prior.covariance)[:target_count]-np.einsum('ij,ij->i', weights, cross)
    if variance.min() < -1e-10:
        raise ArithmeticError('Materially negative predictive variance')
    return Plan(method, len(selected), seed, tuple(selected), weights, offset, np.maximum(variance, 0))


def build_plans(targets, control_count, parameters):
    targets = np.asarray(targets, float)
    if (targets.ndim != 1 or len(targets) < 4 or not np.isfinite(targets).all()
            or np.any(np.diff(targets) <= 0) or targets[0] <= 0 or targets[-1] != 1.
            or isinstance(control_count, bool) or not isinstance(control_count, int) or control_count < 2):
        raise ValueError('Sorted positive normalized targets and at least two controls required')
    coordinates = np.r_[np.zeros(control_count), targets]
    size, n = len(coordinates), len(targets)
    initial = [0, control_count, size-1]
    remaining = [i for i in range(size) if i not in initial]
    random_orders = [initial+np.random.default_rng(seed).permutation(remaining).tolist() for seed in range(20)]
    plans, design_records = [], []
    for mode in ['joint', 'diagonal']:
        model = ContrastGP(**{**parameters, 'correlated': mode == 'joint'})
        prior = model.joint(targets, coordinates[1:])
        to_joint = lambda i: n+i-1
        observed = [to_joint(i) for i in initial[1:]]
        conditioned = prior.condition(observed, prior.mean[observed])
        result = exact_exchangeable_designs(conditioned, range(n), [to_joint(i) for i in remaining],
                                           np.full(n, 1/n), [[to_joint(i) for i in range(1, control_count)]]
                                           if control_count > 2 else [])
        design_records.append({'mode': mode, 'representatives_evaluated': result['representatives_evaluated'],
                               'subsets_represented': result['subsets_represented']})
        for result_row in result['designs']:
            selected = initial+[i-n+1 for i in result_row['actions']]
            plans.append(gp_plan(prior, n, selected, 'exact_'+mode))
        if mode == 'joint':
            order = initial.copy()
            posterior = conditioned
            while len(order) < size:
                available = [i for i in remaining if i not in order]
                gains = [posterior.variance_reduction(range(n), [to_joint(i)], np.full(n, 1/n)) for i in available]
                action = available[int(np.argmax(gains))]
                order.append(action)
                posterior = posterior.condition([to_joint(action)], [posterior.mean[to_joint(action)]])
            for budget in range(3, size+1):
                plans.append(gp_plan(prior, n, order[:budget], 'greedy_joint'))
        for seed, order in enumerate(random_orders):
            for budget in range(3, size+1):
                plans.append(gp_plan(prior, n, order[:budget], 'random_'+mode, seed))
                if mode == 'joint':
                    for method in ['random_linear', 'random_pchip']:
                        plans.append(Plan(method, budget, seed, tuple(order[:budget]), None, None, None))
    return plans, design_records


def predict(plan, log_pool, targets, control_count):
    """Use only selected columns. Other candidate and audit outcomes are hidden."""
    log_pool = np.asarray(log_pool, float)
    selected = list(plan.selected)
    if log_pool.ndim != 2 or not np.isfinite(log_pool[:, selected]).all():
        raise ValueError('Selected log signals must form a finite matrix')
    if plan.weights is not None:
        nonreference = [i for i in selected if i != 0]
        contrasts = log_pool[:, nonreference]-log_pool[:, [0]]
        return plan.offset[None, :]+np.einsum('ij,bj->bi', plan.weights, contrasts)
    controls = [i for i in selected if i < control_count]
    treatment = sorted(i for i in selected if i >= control_count)
    x = np.r_[0., targets[np.array(treatment)-control_count]]
    control_mean = log_pool[:, controls].mean(axis=1)
    y = np.column_stack([np.zeros(len(log_pool)), log_pool[:, treatment]-control_mean[:, None]])
    if plan.method == 'random_pchip':
        return PchipInterpolator(x, y, axis=1)(targets)
    if plan.method != 'random_linear':
        raise ValueError('Unrecognized interpolation method')
    basis = np.eye(len(x))
    weights = np.column_stack([np.interp(targets, x, row) for row in basis])
    return np.einsum('ij,bj->bi', weights, y)
