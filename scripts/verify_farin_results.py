"""Cross-artifact scientific invariants, beyond isolated unit assertions."""
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.contrast_gp import ContrastGP
from zenithsync.farin import load_farin
from zenithsync.farin_replay import partition_curves
from farin_gp_benchmark import replay


def main():
    exact = pd.read_csv(ROOT/'artifacts/farin_exact_v1/results.csv')
    gp = pd.read_csv(ROOT/'artifacts/farin_gp_v1/results.csv')
    tuning = json.loads((ROOT/'artifacts/farin_gp_v1/tuning.json').read_text())
    models = {(r['held_out_organoid_id'], r['mode']): ContrastGP(**r['parameters']) for r in tuning}
    curves, _ = partition_curves(load_farin(ROOT/'data/raw/farin/Drug_sensitivity_all_lines.txt'))
    checked = 0
    for curve in curves:
        for mode in ['joint', 'diagonal']:
            model = models[(curve.organoid_id, mode)]
            rows = exact[exact.curve_id.eq(curve.curve_id) & exact.method.eq(mode)].set_index('budget')
            if set(rows.index) != set(range(3, 17)) or len(rows) != 14:
                raise AssertionError('Incomplete exact-design budgets')
            variances = rows.sort_index().posterior_target_variance.to_numpy()
            if np.any(np.diff(variances) > 1e-10):
                raise AssertionError('Exact fixed-model variance increased with budget')
            for budget, _, sd, _, _ in replay(curve, model, 'ivr', None):
                greedy_variance = float(np.mean(sd**2 - 2*model.noise_sd**2))
                if rows.loc[budget, 'posterior_target_variance'] > greedy_variance + 1e-10:
                    raise AssertionError('Exact fixed-budget objective worse than feasible greedy set')
                checked += 1
            method = 'joint' if mode == 'joint' else 'diagonal_tuned'
            for budget in [3, 16]:
                reference = gp[gp.curve_id.eq(curve.curve_id) & gp.method.eq(method) &
                               gp.policy.eq('ivr') & gp.budget.eq(budget)]
                if len(reference) != 1 or not np.isclose(rows.loc[budget, 'mse'], reference.mse.iloc[0],
                                                       rtol=1e-10, atol=1e-10):
                    raise AssertionError('Exact versus sequential matched-information MSE disagreement')
    result = {'status': 'passed', 'variance_comparisons': checked,
              'scope': ['complete budget support', 'monotone fixed-model exact variance',
                        'exact objective no worse than feasible greedy objective',
                        'identical initial and full-information prediction loss'],
              'does_not_verify': ['biological superiority', 'independent patient sampling', 'novelty']}
    (ROOT/'artifacts/farin_exact_v1/verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
