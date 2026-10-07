"""Preserve model, selection and exact-batch contrasts as distinct questions."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    sources = {'baseline': 'farin_replay_v1', 'gp': 'farin_gp_v1', 'exact': 'farin_exact_v1'}
    data = pd.concat([pd.read_csv(ROOT/'artifacts'/folder/'organoid_results.csv').assign(source=source)
                      for source, folder in sources.items()], ignore_index=True)
    values = data.groupby(['organoid_id', 'source', 'policy', 'method']).mse.mean().unstack(['source', 'policy', 'method'])
    comparisons = [
        (('gp', 'ivr', 'joint'), ('gp', 'ivr', 'diagonal_tuned'), 'combined noise/design effect'),
        (('gp', 'random', 'joint'), ('gp', 'random', 'diagonal_tuned'), 'noise model at common random designs'),
        (('gp', 'ivr', 'joint'), ('gp', 'random', 'joint'), 'greedy design at common estimator'),
        (('exact', 'exact_fixed_budget', 'joint'), ('gp', 'random', 'joint'), 'exact batch versus random'),
        (('exact', 'exact_fixed_budget', 'joint'), ('gp', 'ivr', 'joint'), 'exact batch versus greedy'),
        (('exact', 'exact_fixed_budget', 'joint'), ('baseline', 'random', 'linear'), 'full method versus linear random'),
    ]
    draws = np.random.default_rng(1729).integers(0, len(values), (10000, len(values)))
    rows = []
    for candidate, reference, question in comparisons:
        a, b = values[candidate].to_numpy(), values[reference].to_numpy()
        if not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError('Incomplete paired coverage')
        delta = a-b
        low, high = np.quantile(delta[draws].mean(axis=1), [.025, .975])
        rows.append({'question': question, 'candidate': '/'.join(candidate), 'reference': '/'.join(reference),
                     'candidate_mean_budget_mse': float(a.mean()), 'reference_mean_budget_mse': float(b.mean()),
                     'paired_difference': float(delta.mean()), 'bootstrap_low': float(low), 'bootstrap_high': float(high),
                     'ids_favoring_candidate': int((delta < 0).sum()), 'total_ids': len(delta)})
    output = ROOT/'artifacts/farin_gp_v1'
    result = pd.DataFrame(rows)
    result.to_csv(output/'paired_comparisons.csv', index=False, float_format='%.12g')
    (output/'comparison_limits.json').write_text(json.dumps({
        'status': 'Exploratory development comparisons after method development; not confirmation.',
        'endpoint': 'Mean MSE over all fourteen budgets, with equal ID weight.',
        'bootstrap': '10000 paired ID resamples, seed 1729; patient independence unverified.',
        'coverage_claim': 'Marginal empirical coverage only; no simultaneous or distribution-free guarantee.',
        'novelty': 'Pinned GP, Gaussian covariance modeling and exhaustive design are established mathematical tools.',
        'assay_savings_established': False,
    }, indent=2)+'\n')
    print(result.to_string(index=False))


if __name__ == '__main__':
    main()
