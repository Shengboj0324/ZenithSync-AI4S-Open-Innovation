"""Paired development comparisons without treating seeds as biological units."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / 'artifacts/farin_replay_v1'
    data = pd.read_csv(output / 'organoid_results.csv')
    # Equal weight to each of the 14 prespecified budgets, including common
    # initial and complete endpoints. This is not an assay-saving estimate.
    table = data.groupby(['organoid_id', 'policy', 'method']).mse.mean().unstack(['policy', 'method'])
    if table.isna().any().any():
        raise ValueError('Paired comparisons require complete matched ID coverage')
    draws = np.random.default_rng(1729).integers(0, len(table), (10000, len(table)))
    rows = []
    for method in ['constant', 'linear', 'pchip']:
        candidate = table[('control_first_space', method)].to_numpy()
        for policy in ['space_filling', 'random']:
            reference = table[(policy, method)].to_numpy()
            paired = candidate - reference
            low, high = np.quantile(paired[draws].mean(axis=1), [.025, .975])
            rows.append({'candidate': 'control_first_space', 'reference': policy,
                         'method': method, 'organoid_ids': len(table),
                         'candidate_budget_mean_mse': float(candidate.mean()),
                         'reference_budget_mean_mse': float(reference.mean()),
                         'paired_difference': float(paired.mean()),
                         'exploratory_id_bootstrap_low': float(low),
                         'exploratory_id_bootstrap_high': float(high)})
    result = pd.DataFrame(rows)
    result.to_csv(output / 'paired_comparisons.csv', index=False, float_format='%.12g')
    (output / 'comparison_limits.json').write_text(json.dumps({
        'direction': 'Negative paired difference favors control-first spacing.',
        'status': 'Post-inspection development baseline comparison, not confirmatory inference.',
        'resampling': '10000 paired organoid-ID bootstrap draws, seed 1729; patient independence unverified.',
        'multiplicity': 'Six exploratory contrasts; no familywise significance claim.',
        'metric': 'Equal mean MSE across budgets 3 through 16, then equal mean across IDs.',
        'assay_savings_established': False,
    }, indent=2) + '\n')
    print(result.to_string(index=False))


if __name__ == '__main__':
    main()
