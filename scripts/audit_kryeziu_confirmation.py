"""Independent aggregation and cross-artifact checks of the first evaluation."""
from collections import defaultdict
import csv
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/kryeziu_confirmation_v1'


def main():
    report = json.loads((OUT/'confirmation.json').read_text())
    data = pd.read_csv(OUT/'results.csv.gz')
    methods = {'exact_joint', 'greedy_joint', 'random_joint', 'exact_diagonal',
               'random_diagonal', 'random_linear', 'random_pchip'}
    if set(data.method) != methods or not np.isfinite(data.mse).all():
        raise AssertionError('Missing methods or nonfinite losses')
    groups = data.groupby(['orientation', 'context', 'method'])
    counts = groups.budget.agg(['min', 'max', 'count', 'nunique'])
    if not ((counts['min'] == 3) & (counts['count'] == counts['max']-2) &
            (counts['count'] == counts['nunique'])).all():
        raise AssertionError('Incomplete or duplicated budget records')
    if not (data.seed_count == np.where(data.method.str.startswith('random_'), 20, 1)).all():
        raise AssertionError('Incorrect algorithmic repeat count')
    for endpoint in ['initial', 'full']:
        part = data[data.budget.eq(3) if endpoint == 'initial' else data.budget.eq(data.full_pool_size)]
        pivot = part.pivot(index=['orientation', 'context'], columns='method', values='mse')
        for family in [['exact_joint', 'greedy_joint', 'random_joint'], ['exact_diagonal', 'random_diagonal']]:
            spread = pivot[family].max(axis=1)-pivot[family].min(axis=1)
            if spread.max() > 1e-9:
                raise AssertionError('Matched-information prediction loss differs')
    # Recompute hierarchy with plain dictionaries from the serialized CSV,
    # independently of the runner's pandas groupby implementation.
    curve = defaultdict(lambda: [0., 0])
    efficiency = {}
    with gzip.open(OUT/'results.csv.gz', 'rt', newline='') as handle:
        for row in csv.DictReader(handle):
            key = tuple(row[k] for k in ['orientation', 'patient', 'sample_id', 'context', 'method'])
            curve[key][0] += float(row['mse'])
            curve[key][1] += 1
            reference_budget = (3*int(row['full_pool_size'])+3)//4
            candidate_budget = (4*reference_budget)//5
            desired = {'random_joint': reference_budget, 'exact_joint': candidate_budget}.get(row['method'])
            if int(row['budget']) == desired:
                if key in efficiency:
                    raise AssertionError('Duplicate efficiency endpoint')
                efficiency[key] = float(row['mse'])
    samples = defaultdict(list)
    for (orientation, patient, sample, _, method), (total, count) in curve.items():
        samples[(orientation, patient, sample, method)].append(total/count)
    patients = defaultdict(list)
    for (orientation, patient, _, method), values in samples.items():
        patients[(orientation, patient, method)].append(float(np.mean(values)))
    values = {key: float(np.mean(value)) for key, value in patients.items()}
    efficiency_samples = defaultdict(list)
    for (orientation, patient, sample, _, method), value in efficiency.items():
        efficiency_samples[(orientation, patient, sample, method)].append(value)
    efficiency_patients = defaultdict(list)
    for (orientation, patient, _, method), sample_values in efficiency_samples.items():
        efficiency_patients[(orientation, patient, method)].append(float(np.mean(sample_values)))
    efficiency_values = {key: float(np.mean(value)) for key, value in efficiency_patients.items()}
    comparisons = []
    for orientation in ['p1_to_p2', 'p2_to_p1']:
        ids = sorted({patient for ori, patient, _ in values if ori == orientation})
        expected = report['orientations'][orientation]
        for method in methods:
            actual = np.mean([values[(orientation, patient, method)] for patient in ids])
            if not np.isclose(actual, expected['mean_budget_mse'][method], rtol=1e-10, atol=1e-12):
                raise AssertionError('Independent patient aggregation disagrees')
        draws = np.random.default_rng(1729).integers(0, len(ids), (10000, len(ids)))
        ea = np.array([efficiency_values[(orientation, patient, 'exact_joint')] for patient in ids])
        eb = np.array([efficiency_values[(orientation, patient, 'random_joint')] for patient in ids])
        efficiency_interval = np.quantile(ea[draws].mean(axis=1)/eb[draws].mean(axis=1), [.025, .975])
        np.testing.assert_allclose(efficiency_interval, expected['efficiency_secondary']['ratio_interval95'],
                                   rtol=1e-9, atol=1e-11)
        for reference in ['random_joint', 'greedy_joint', 'exact_diagonal', 'random_pchip']:
            a = np.array([values[(orientation, patient, 'exact_joint')] for patient in ids])
            b = np.array([values[(orientation, patient, reference)] for patient in ids])
            interval = np.quantile((a-b)[draws].mean(axis=1), [.025, .975])
            if reference == 'random_joint':
                np.testing.assert_allclose(interval, expected['difference_interval95'], rtol=1e-9, atol=1e-11)
            comparisons.append({'orientation': orientation, 'candidate': 'exact_joint', 'reference': reference,
                                'mean_mse_difference': float((a-b).mean()), 'relative_reduction': float(1-a.mean()/b.mean()),
                                'difference_low95': interval[0], 'difference_high95': interval[1],
                                'status': 'primary' if reference == 'random_joint' and orientation == 'p1_to_p2'
                                          else 'secondary diagnostic; no multiplicity-adjusted claim'})
    pd.DataFrame(comparisons).to_csv(OUT/'paired-comparators.csv', index=False, float_format='%.12g')
    exclusion = json.loads((OUT/'exclusions.json').read_text())
    result = {'status': 'passed', 'result_rows': len(data),
              'primary_valid_contexts': int(data[data.orientation.eq('p1_to_p2')].context.nunique()),
              'samples': int(data.sample_id.nunique()), 'patients': int(data.patient.nunique()),
              'excluded_context_orientations': len(exclusion),
              'checks': ['complete methods/budgets/seeds', 'matched-information endpoints',
                         'independent serialized-data hierarchy', 'primary patient-bootstrap interval',
                         'integer-budget efficiency comparison and its bootstrap interval'],
              'limits': ['computational cross-check, not an external scientific review',
                         'retrospective separate-plate evaluation; no clinical or competition-rank guarantee']}
    (OUT/'verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    print(pd.DataFrame(comparisons).to_string(index=False))


if __name__ == '__main__':
    main()
