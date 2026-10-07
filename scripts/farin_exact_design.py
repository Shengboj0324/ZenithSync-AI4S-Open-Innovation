"""Separate fixed-budget campaigns; exhaustive design is not a nested policy."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.contrast_gp import ContrastGP, contrast_design
from zenithsync.farin import load_farin
from zenithsync.farin_replay import WellOracle, audit_log_response, partition_curves
from zenithsync.joint_design import exact_cardinality_designs
from farin_replay_benchmark import action_order


def main():
    output = ROOT/'artifacts/farin_exact_v1'
    output.mkdir(parents=True, exist_ok=True)
    tuning_path = ROOT/'artifacts/farin_gp_v1/tuning.json'
    tuning = json.loads(tuning_path.read_text())
    models = {(r['held_out_organoid_id'], r['mode']): ContrastGP(**r['parameters']) for r in tuning}
    curves, _ = partition_curves(load_farin(ROOT/'data/raw/farin/Drug_sensitivity_all_lines.txt'))
    cached = {}
    rows, selections = [], []
    for curve in curves:
        metadata = WellOracle(curve).design
        targets, coordinates, ref = contrast_design(metadata)
        pool = [i for i in range(len(coordinates)) if i != ref]
        mapping = {index: len(targets)+i for i, index in enumerate(pool)}
        inverse = {v: k for k, v in mapping.items()}
        initial = action_order(metadata)[:3]
        observed = [mapping[i] for i in initial if i != ref]
        remaining = [mapping[i] for i in pool if i not in initial]
        truth = audit_log_response(curve)
        for mode in ['joint', 'diagonal']:
            model = models[(curve.organoid_id, mode)]
            prior = model.joint(targets, coordinates[pool])
            # Covariance is independent of observed values for fixed parameters.
            # Cache by exact coordinates, model and initial design, never outcomes.
            key = (model, tuple(targets), tuple(coordinates), tuple(initial))
            if key not in cached:
                conditional = prior.condition(observed, prior.mean[observed])
                cached[key] = exact_cardinality_designs(conditional, range(len(targets)), remaining,
                                                       np.full(len(targets), 1/len(targets)))
                print(f'Enumerated design {len(cached)}: {sum(r["subsets_evaluated"] for r in cached[key])} subsets', flush=True)
            for extra, result in enumerate(cached[key]):
                selected = initial + [inverse[i] for i in result['actions']]
                oracle = WellOracle(curve)
                for index in selected:
                    oracle.reveal(index)
                observations = oracle.observations
                reference = observations.loc[observations.source_row.eq(metadata.iloc[ref].source_row),
                                             'raw_luminescence'].iloc[0]
                actual = [i for i in selected if i != ref]
                values = np.log(observations.raw_luminescence.to_numpy()[1:]) - np.log(reference)
                posterior = prior.condition([mapping[i] for i in actual], values)
                mean = posterior.mean[:len(targets)]
                sd = np.sqrt(np.diag(posterior.covariance)[:len(targets)]+2*model.noise_sd**2)
                rows.append({'curve_id': curve.curve_id, 'organoid_id': curve.organoid_id,
                             'method': mode, 'policy': 'exact_fixed_budget', 'budget': 3+extra,
                             'mse': float(np.mean((mean-truth)**2)),
                             'coverage90': float(np.mean(np.abs(mean-truth) <= 1.6448536269514722*sd)),
                             'posterior_target_variance': float(np.mean(np.diag(posterior.covariance)[:len(targets)])),
                             'incremental_variance_reduction': result['variance_reduction'],
                             'subsets_evaluated_at_count': result['subsets_evaluated']})
                selections.append({'curve_id': curve.curve_id, 'method': mode, 'budget': 3+extra,
                                   'source_rows': json.dumps(metadata.iloc[selected].source_row.tolist())})
    frame = pd.DataFrame(rows)
    if not np.isfinite(frame.mse).all():
        raise ArithmeticError('Nonfinite exact-design evaluation')
    frame.to_csv(output/'results.csv', index=False, float_format='%.12g')
    pd.DataFrame(selections).to_csv(output/'selections.csv', index=False)
    per_id = frame.groupby(['organoid_id', 'policy', 'method', 'budget'])[
        ['mse', 'coverage90', 'posterior_target_variance']].mean()
    per_id.to_csv(output/'organoid_results.csv', float_format='%.12g')
    summary = per_id.groupby(['policy', 'method', 'budget']).mean().reset_index()
    summary['rmse'] = np.sqrt(summary.mse)
    summary.to_csv(output/'summary.csv', index=False, float_format='%.12g')
    (output/'record.json').write_text(json.dumps({
        'status': 'development fixed-budget design; no sequential stopping claim',
        'unique_design_enumerations': len(cached), 'subsets_per_design': 8192,
        'tuning_sha256': hashlib.sha256(tuning_path.read_bytes()).hexdigest(),
        'selection_uses_outcomes': False, 'tuning_uses_other_ID_pool_outcomes': True,
        'assurance': 'Optimal posterior variance among the supplied remaining thirteen wells at each exact count, conditional on a fixed Gaussian model; not optimal biological error.',
    }, indent=2)+'\n')
    print(summary[summary.budget.isin([3, 8, 16])].to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
