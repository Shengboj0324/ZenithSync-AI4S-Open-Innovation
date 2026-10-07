"""Analytic design/estimator ablations under declared synthetic joint laws.

This is a mechanism check, not biological validation. Expected squared error is
calculated under the true joint law, including covariance misspecification.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np
from scipy.linalg import cho_factor, cho_solve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.joint_design import JointGaussian, exact_budget_design


def scenario(control_variance, diagonal=False):
    x = np.linspace(0, 1, 6)
    kernel = np.exp(-np.abs(x[:, None]-x[None, :])/.3)
    group = np.zeros((6, 2))
    group[:3, 0], group[3:, 1] = 1, 1
    common = control_variance*np.einsum('ik,jk->ij', group, group)
    treatments = kernel+common+.1*np.eye(6)
    cross_controls = control_variance*group
    if diagonal:
        treatments = kernel+np.diag(np.diag(common))+.1*np.eye(6)
        cross_controls = np.zeros((6, 2))
    covariance = np.block([
        [kernel, kernel, np.zeros((6, 2))],
        [kernel, treatments, cross_controls],
        [np.zeros((2, 6)), cross_controls.T, (control_variance+.05)*np.eye(2)]])
    return JointGaussian(np.zeros(14), covariance)


def expected_mse(truth, model, actions):
    """Exact unconditional MSE of the model's linear posterior mean, zero means."""
    targets = list(range(6))
    if not actions:
        return float(np.diag(truth.covariance)[:6].mean())
    cross = model.covariance[np.ix_(targets, actions)]
    block = model.covariance[np.ix_(actions, actions)]
    coefficients = cho_solve(cho_factor(block, lower=True), cross.T).T
    true_cross = truth.covariance[np.ix_(targets, actions)]
    true_block = truth.covariance[np.ix_(actions, actions)]
    error = (np.diag(truth.covariance)[:6]
             - 2*np.einsum('ij,ij->i', coefficients, true_cross)
             + np.einsum('ij,jk,ik->i', coefficients, true_block, coefficients))
    return float(error.mean())


def main():
    rows = []
    for control_variance in (0., .1, 1., 4.):
        truth = scenario(control_variance)
        diagonal = scenario(control_variance, diagonal=True)
        for budget in (1., 2., 3., 4., 5., 6.):
            full = exact_budget_design(truth, range(6), range(6, 14), [1/6]*6,
                                       [1.]*6+[.5]*2, budget)
            flat = exact_budget_design(diagonal, range(6), range(6, 14), [1/6]*6,
                                       [1.]*6+[.5]*2, budget)
            for label, design, estimator in (
                    ('joint_design_joint_estimator', full, truth),
                    ('diagonal_design_joint_estimator', flat, truth),
                    ('diagonal_design_diagonal_estimator', flat, diagonal)):
                mse = expected_mse(truth, estimator, design['actions'])
                rows.append({'control_variance': control_variance, 'budget': budget,
                             'method': label, 'actions': ','.join(map(str, design['actions'])),
                             'cost': design['cost'], 'true_expected_mse': mse,
                             'assumed_variance_reduction': design['variance_reduction']})
            # Exact true-model design cannot lose to any feasible competitor
            # under this particular correctly specified variance objective.
            assert rows[-3]['true_expected_mse'] <= rows[-2]['true_expected_mse']+1e-12
    output = ROOT/'artifacts/joint_design_v1'
    output.mkdir(parents=True, exist_ok=True)
    with (output/'analytic_ablation.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    record = {'evidence_type': 'analytic synthetic mechanism check', 'rows': len(rows),
              'target_count': 6, 'candidate_count': 8, 'biological_campaigns': 0,
              'control_variances': [0, .1, 1, 4], 'budgets': [1, 2, 3, 4, 5, 6],
              'units': 'synthetic latent-response squared units; artificial action costs',
              'scope': 'Known true Gaussian law; no empirical superiority, novelty or assay savings claim',
              'label_access': 'Design has covariance only; no sampled outcomes exist'}
    (output/'record.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(json.dumps(record, sort_keys=True))


if __name__ == '__main__':
    main()
