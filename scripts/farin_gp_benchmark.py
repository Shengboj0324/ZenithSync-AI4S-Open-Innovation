"""Group-held-out GP tuning and matched-information measured-well replay."""
from dataclasses import asdict, replace
from itertools import product
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.contrast_gp import ContrastGP, contrast_design
from zenithsync.farin import load_farin
from zenithsync.farin_replay import WellOracle, audit_log_response, interpolation_prediction, partition_curves
from farin_replay_benchmark import action_order


def fit_leave_id_out(curves):
    """Tune on other IDs' pool responses only, never any audit response."""
    grids = {mode: [ContrastGP(a, length, noise, slope, correlated=mode == 'joint')
                   for a, length, noise, slope in product([1., 2.], [.2, .5, 1.],
                                                         [.15, .3, .6], [0., 2., 4.])]
             for mode in ['joint', 'diagonal']}
    rows = []
    for curve in curves:
        _, coordinates, ref = contrast_design(curve.pool)
        keep = np.arange(len(coordinates)) != ref
        logs = np.log(curve.pool.raw_luminescence.to_numpy())
        for mode, models in grids.items():
            for index, model in enumerate(models):
                rows.append({'curve_id': curve.curve_id, 'organoid_id': curve.organoid_id,
                             'mode': mode, 'config': index,
                             'nll': model.negative_log_likelihood(coordinates[keep], logs[keep]-logs[ref])})
    scores = pd.DataFrame(rows)
    id_scores = scores.groupby(['organoid_id', 'mode', 'config']).nll.mean().reset_index()
    selected, ledger = {}, []
    for held_id in sorted(id_scores.organoid_id.unique()):
        training = id_scores[~id_scores.organoid_id.eq(held_id)]
        for mode in grids:
            ranking = training[training['mode'].eq(mode)].groupby('config').nll.mean()
            best = int(ranking.idxmin())
            selected[(held_id, mode)] = grids[mode][best]
            ledger.append({'held_out_organoid_id': held_id, 'mode': mode, 'config': best,
                           'parameters': asdict(grids[mode][best]),
                           'training_ids': sorted(training.organoid_id.unique()),
                           'training_nll': float(ranking.loc[best])})
    return selected, scores, ledger


def replay(curve, model, policy, seed):
    oracle = WellOracle(curve)
    targets, coordinates, ref = contrast_design(oracle.design)
    pool_indices = [i for i in range(len(coordinates)) if i != ref]
    mapping = {pool_index: len(targets)+i for i, pool_index in enumerate(pool_indices)}
    posterior = model.joint(targets, coordinates[pool_indices])
    fixed_order = action_order(oracle.design, seed=seed)
    chosen = []
    reference_log = None
    for step in range(len(coordinates)):
        if step < 3 or policy != 'ivr':
            action = fixed_order[step]
        else:
            remaining = [i for i in pool_indices if i not in chosen]
            gains = [posterior.variance_reduction(range(len(targets)), [mapping[i]],
                                                  np.full(len(targets), 1/len(targets)))
                     for i in remaining]
            action = remaining[int(np.argmax(gains))]
        observation = oracle.reveal(action)
        chosen.append(action)
        value = np.log(observation.raw_luminescence)
        if action == ref:
            reference_log = value
        else:
            if reference_log is None:
                raise AssertionError('Reference control must be measured first')
            posterior = posterior.condition([mapping[action]], [value-reference_log])
        if oracle.spent < 3:
            continue
        mean = posterior.mean[:len(targets)]
        latent_var = np.diag(posterior.covariance)[:len(targets)]
        # Audit contrasts have fresh treatment and control errors. Marginal
        # variance adds 2 sigma^2; joint audit errors also share their control.
        predictive_sd = np.sqrt(np.maximum(latent_var, 0) + 2*model.noise_sd**2)
        yield oracle.spent, mean, predictive_sd, oracle.observations, chosen.copy()


def main():
    output = ROOT/'artifacts/farin_gp_v1'
    output.mkdir(parents=True, exist_ok=True)
    curves, _ = partition_curves(load_farin(ROOT/'data/raw/farin/Drug_sensitivity_all_lines.txt'))
    models, scores, ledger = fit_leave_id_out(curves)
    scores.to_csv(output/'tuning_scores.csv', index=False, float_format='%.12g')
    (output/'tuning.json').write_text(json.dumps(ledger, indent=2)+'\n')
    print('Tuning complete: audit outcomes unused; held-out IDs excluded.', flush=True)
    rows, orders = [], []
    for curve in curves:
        truth = audit_log_response(curve)
        joint = models[(curve.organoid_id, 'joint')]
        estimators = {'joint': joint, 'diagonal_matched': replace(joint, correlated=False),
                      'diagonal_tuned': models[(curve.organoid_id, 'diagonal')]}
        for name, model in estimators.items():
            policies = [('ivr', None), ('space_filling', None)]
            policies.extend(('random', seed) for seed in range(20))
            for policy, seed in policies:
                for budget, mean, sd, observations, chosen in replay(curve, model, policy, seed):
                    error = truth-mean
                    # Exact univariate Gaussian CRPS, and marginal interval coverage.
                    z = error/sd
                    crps = sd*(z*(2*ndtr(z)-1)+2*np.exp(-z*z/2)/np.sqrt(2*np.pi)-1/np.sqrt(np.pi))
                    base = {'curve_id': curve.curve_id, 'organoid_id': curve.organoid_id,
                            'policy': policy, 'seed': -1 if seed is None else seed, 'budget': budget}
                    rows.append({**base, 'method': name, 'mse': float(np.mean(error**2)),
                                 'coverage90': float(np.mean(np.abs(z) <= 1.6448536269514722)),
                                 'interval_width90': float(np.mean(2*1.6448536269514722*sd)),
                                 'crps': float(np.mean(crps))})
                    if name == 'joint' and policy == 'ivr':
                        for baseline in ['linear', 'pchip']:
                            prediction = interpolation_prediction(observations, curve.doses, method=baseline)
                            rows.append({**base, 'method': baseline, 'mse': float(np.mean((prediction-truth)**2)),
                                         'coverage90': None, 'interval_width90': None, 'crps': None})
                    if budget == 16:
                        orders.append({**base, 'method': name,
                                       'source_rows': json.dumps(curve.pool.iloc[chosen].source_row.tolist())})
    results = pd.DataFrame(rows)
    if not np.isfinite(results.mse).all():
        raise ArithmeticError('Nonfinite GP replay result')
    for budget in [3, 16]:
        spread = results[results.budget.eq(budget)].groupby(['curve_id', 'method']).mse.agg(['min', 'max'])
        if not np.allclose(spread['min'], spread['max'], atol=1e-10, rtol=1e-10):
            raise AssertionError('Matched-information endpoint mismatch')
    results.to_csv(output/'results.csv', index=False, float_format='%.12g')
    pd.DataFrame(orders).to_csv(output/'selections.csv', index=False)
    metrics = ['mse', 'coverage90', 'interval_width90', 'crps']
    per_curve = results.groupby(['curve_id', 'organoid_id', 'policy', 'method', 'budget'])[metrics].mean()
    per_id = per_curve.groupby(['organoid_id', 'policy', 'method', 'budget']).mean()
    per_id.to_csv(output/'organoid_results.csv', float_format='%.12g')
    summary = per_id.groupby(['policy', 'method', 'budget']).mean().reset_index()
    summary['rmse'] = np.sqrt(summary.mse)
    summary.to_csv(output/'summary.csv', index=False, float_format='%.12g')
    (output/'record.json').write_text(json.dumps({
        'status': 'development; standard GP method, no novelty claim',
        'curves': len(curves), 'organoid_ids': len({c.organoid_id for c in curves}),
        'result_rows': len(results), 'tuning': 'leave organoid ID out; pool labels 1/2 only; 54 configurations per noise model',
        'selection': 'one-step IVR; not globally optimal batch design',
        'historical_training_assays_counted_in_online_budget': False,
        'audit_used_in_tuning': False, 'independent_confirmation': False,
        'assumptions': ['independent equal-variance raw log errors', 'pinned Matern 5/2 shape prior',
                        'hyperparameters treated as fixed', 'no plate or patient independence claim'],
    }, indent=2)+'\n')
    print(summary[summary.budget.isin([3, 8, 16])].to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
