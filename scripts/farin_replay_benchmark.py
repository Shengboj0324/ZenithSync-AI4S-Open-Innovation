"""Development-only, counted-well comparisons against hidden audit responses."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from zenithsync.farin import load_farin
from zenithsync.farin_replay import (
    WellOracle, audit_log_response, interpolation_prediction, partition_curves,
)


def action_order(design, *, seed=None, controls_first=False):
    initial = [int(design.index[(design.concentration.eq(dose)) &
                               design.replicate_label.eq('1')][0])
               for dose in [0., design.loc[~design.is_control, 'concentration'].min(),
                            design.concentration.max()]]
    if controls_first:
        initial.extend(int(i) for i in design.index[design.is_control] if i not in initial)
    remaining = [i for i in design.index if i not in initial]
    if seed is not None:
        return initial + np.random.default_rng(seed).permutation(remaining).tolist()
    x = np.log1p(design.concentration.to_numpy() /
                 design.loc[~design.is_control, 'concentration'].min())
    selected = initial.copy()
    while remaining:
        distance = np.min(np.abs(x[remaining, None] - x[selected]), axis=1)
        chosen = remaining[int(np.argmax(distance))]
        selected.append(chosen)
        remaining.remove(chosen)
    return selected


def main():
    output = ROOT / 'artifacts/farin_replay_v1'
    output.mkdir(parents=True, exist_ok=True)
    protocol_path = ROOT / 'configs/farin-replay-protocol.json'
    protocol = json.loads(protocol_path.read_text())
    curves, admission = partition_curves(load_farin(ROOT / 'data/raw/farin/Drug_sensitivity_all_lines.txt'))
    admission.to_csv(output / 'admission.csv', index=False)
    rows, selections = [], []
    for curve in curves:
        # Outcomes are obtained only by the evaluator, never passed to selection
        # or prediction. Complete-case admission remains retrospective.
        truth = audit_log_response(curve)
        policies = [('space_filling', None, False), ('control_first_space', None, True)]
        policies.extend(('random', seed, False) for seed in range(20))
        for policy, seed, controls_first in policies:
            oracle = WellOracle(curve)
            order = action_order(oracle.design, seed=seed, controls_first=controls_first)
            selections.append({'curve_id': curve.curve_id, 'policy': policy,
                               'seed': -1 if seed is None else seed,
                               'source_rows': json.dumps(oracle.design.iloc[order].source_row.tolist())})
            for index in order:
                oracle.reveal(index)
                if oracle.spent not in protocol['budgets']:
                    continue
                observations = oracle.observations
                for method in ['constant', 'linear', 'pchip']:
                    prediction = interpolation_prediction(observations, curve.doses, method=method)
                    rows.append({'curve_id': curve.curve_id, 'organoid_id': curve.organoid_id,
                                 'policy': policy, 'seed': -1 if seed is None else seed,
                                 'method': method, 'budget': oracle.spent,
                                 'mse': float(np.mean((prediction - truth) ** 2))})
    results = pd.DataFrame(rows)
    if not np.isfinite(results.mse).all():
        raise ArithmeticError('Nonfinite measured replay loss')
    for budget in (3, 16):
        spread = results[results.budget.eq(budget)].groupby(['curve_id', 'method']).mse.agg(['min', 'max'])
        if not np.allclose(spread['min'], spread['max'], rtol=1e-12, atol=1e-12):
            raise AssertionError('Matched initial or full-information endpoint disagrees across policies')
    results.to_csv(output / 'results.csv', index=False, float_format='%.12g')
    pd.DataFrame(selections).to_csv(output / 'selections.csv', index=False)
    # Seeds first, then curves per ID, then IDs: no pseudoreplication from seeds.
    per_curve = results.groupby(['curve_id', 'organoid_id', 'policy', 'method', 'budget']).mse.mean()
    per_id = per_curve.groupby(['organoid_id', 'policy', 'method', 'budget']).mean()
    per_id.rename('mse').to_csv(output / 'organoid_results.csv', float_format='%.12g')
    summary = per_id.groupby(['policy', 'method', 'budget']).mean().rename('mse').reset_index()
    summary['rmse'] = np.sqrt(summary.mse)
    summary.to_csv(output / 'summary.csv', index=False, float_format='%.12g')
    record = {'status': 'development baseline; no novel-method superiority tested',
              'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
              'admitted_curves': len(curves), 'organoid_ids': len({c.organoid_id for c in curves}),
              'random_seeds': 20, 'result_rows': len(results),
              'noise_floor_subtracted': False, 'independent_patients_verified': False,
              'external_confirmation': False}
    (output / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)
    print(summary[summary.budget.isin([3, 8, 16])].to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
