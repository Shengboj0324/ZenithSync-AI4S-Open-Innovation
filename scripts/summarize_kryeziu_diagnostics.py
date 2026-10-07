"""Prespecified subgroup, full-budget and uncertainty summaries; no retuning."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/kryeziu_confirmation_v1'


def patient_summary(frame, dimensions, metrics):
    context = frame.groupby([*dimensions, 'patient', 'sample_id', 'context'])[metrics].mean()
    sample = context.groupby([*dimensions, 'patient', 'sample_id']).mean()
    patient = sample.groupby([*dimensions, 'patient']).mean()
    summary = patient.groupby(dimensions).mean()
    summary['patients'] = patient.groupby(dimensions).size()
    return patient, summary


def main():
    data = pd.read_csv(OUT/'results.csv.gz')
    metrics = ['mse', 'coverage90', 'width90']
    patient, overall = patient_summary(data, ['orientation', 'method'], metrics)
    patient.to_csv(OUT/'patient-diagnostics.csv', float_format='%.12g')
    overall.to_csv(OUT/'overall-diagnostics.csv', float_format='%.12g')
    for field in ['drug', 'library_id']:
        _, summary = patient_summary(data, ['orientation', field, 'method'], metrics)
        summary.to_csv(OUT/f'{field}-diagnostics.csv', float_format='%.12g')
    _, budget = patient_summary(data, ['orientation', 'full_pool_size', 'budget', 'method'], metrics)
    budget.to_csv(OUT/'budget-diagnostics.csv', float_format='%.12g')
    contexts = data[data.orientation.eq('p1_to_p2')].drop_duplicates('context')
    reference = np.ceil(.75*contexts.full_pool_size).astype(int)
    candidate = np.floor(.8*reference).astype(int)
    distribution = pd.DataFrame({'full_pool_size': contexts.full_pool_size,
                                 'reference_wells': reference, 'candidate_wells': candidate})
    distribution = distribution.value_counts().rename('contexts').reset_index()
    distribution['fraction_fewer_wells'] = 1-distribution.candidate_wells/distribution.reference_wells
    distribution.to_csv(OUT/'efficiency-budgets.csv', index=False, float_format='%.12g')
    joint = patient.xs(('p1_to_p2', 'exact_joint'), level=('orientation', 'method'))
    report = {'status': 'prespecified diagnostics; no model changes',
              'primary_exact_joint_coverage90': float(overall.loc[('p1_to_p2', 'exact_joint'), 'coverage90']),
              'primary_exact_joint_width90': float(overall.loc[('p1_to_p2', 'exact_joint'), 'width90']),
              'patient_coverage_range': [float(joint.coverage90.min()), float(joint.coverage90.max())],
              'min_fraction_fewer_wells': float(distribution.fraction_fewer_wells.min()),
              'max_fraction_fewer_wells': float(distribution.fraction_fewer_wells.max()),
              'limits': ['patient coverages summarize correlated doses and budgets',
                         'subgroup effects are diagnostic, not independently powered tests',
                         'assay counts exclude preparation overhead and audit costs',
                         'controls are charged per isolated drug context; no plate-wide cost claim']}
    (OUT/'diagnostics.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    print(distribution.to_string(index=False))


if __name__ == '__main__':
    main()
