"""Frozen-protocol preflight and independent confirmation, with immutable runs."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.confirmation import build_plans, predict

OUT = ROOT/'artifacts/kryeziu_confirmation_v1'
DESIGN = ROOT/'artifacts/kryeziu_design_v1'
CODE = ['src/zenithsync/confirmation.py', 'src/zenithsync/symmetric_design.py',
        'src/zenithsync/joint_design.py', 'scripts/kryeziu_confirmation.py',
        'scripts/unblind_kryeziu.py']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    freeze = json.loads((DESIGN/'protocol-freeze.json').read_text())
    for name, expected in freeze['sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('Frozen protocol/admission content changed: '+name)
    protocol = json.loads((ROOT/'configs/kryeziu-confirmation-protocol.json').read_text())
    metadata = pd.read_csv(DESIGN/'design-1.csv', dtype=str, keep_default_na=False)
    extraction = json.loads((DESIGN/'extraction.json').read_text())
    if digest(DESIGN/'design-1.csv') != extraction['sheets'][0]['sha256']:
        raise ValueError('Design projection changed')
    metadata.index = metadata.source_row.astype(int)
    admitted = pd.read_csv(DESIGN/'patient-admission.csv', dtype=str, keep_default_na=False)
    keyfields = ['sample_id', 'run_id', 'library_id', 'compound_name']
    patients = {tuple(row[f] for f in keyfields): row['patient'] for row in admitted.to_dict('records')
                if row['patient_mapping_available'] == 'True'}
    cohort = json.loads((DESIGN/'paired_source_rows.json').read_text())
    groups = defaultdict(list)
    for row in cohort:
        key = tuple(row[f] for f in keyfields)
        if key not in patients:
            continue
        for orientation in ['p1_to_p2', 'p2_to_p1']:
            first, second = ('pool', 'audit') if orientation == 'p1_to_p2' else ('audit', 'pool')
            treatment = sorted(row[first+'_treatment_source_rows'], key=lambda i: float(metadata.loc[i, 'concentration']))
            audit = sorted(row[second+'_treatment_source_rows'], key=lambda i: float(metadata.loc[i, 'concentration']))
            controls = sorted(row[first+'_control_source_rows'])
            audit_controls = sorted(row[second+'_control_source_rows'])
            doses = metadata.loc[treatment, 'concentration'].astype(float).to_numpy()
            if not np.array_equal(doses, metadata.loc[audit, 'concentration'].astype(float).to_numpy()):
                raise ValueError('Audit doses do not exactly match pool doses')
            targets = np.log1p(doses/doses.min())
            targets /= targets.max()
            geometry = (tuple(targets), len(controls))
            groups[geometry].append({'context': '|'.join(key), 'patient': patients[key],
                                     'sample_id': key[0], 'run_id': key[1], 'library_id': key[2],
                                     'drug': key[3], 'orientation': orientation,
                                     'pool_rows': controls+treatment, 'audit_rows': audit,
                                     'audit_controls': audit_controls})
    cache, designs = {}, []
    for geometry in sorted(groups):
        targets, controls = geometry
        plans, records = build_plans(np.array(targets), controls, protocol['fixed_model'])
        identity = hashlib.sha256(json.dumps(geometry).encode()).hexdigest()[:16]
        plan_hash = hashlib.sha256()
        for plan in plans:
            plan_hash.update(json.dumps([plan.method, plan.budget, plan.seed, plan.selected]).encode())
            for array in [plan.weights, plan.offset, plan.variance]:
                if array is not None:
                    plan_hash.update(array.tobytes())
        designs.append({'design_id': identity, 'targets': targets, 'pool_controls': controls,
                        'contexts': len(groups[geometry]), 'plans': len(plans),
                        'plan_sha256': plan_hash.hexdigest(), 'enumeration': records})
        cache[geometry] = plans
    manifest = {'protocol_freeze_sha256': digest(DESIGN/'protocol-freeze.json'),
                'code_sha256': {name: digest(ROOT/name) for name in CODE},
                'context_orientations': sum(map(len, groups.values())), 'designs': designs,
                'pool_order': 'controls by source row, then treatment doses ascending',
                'status': 'outcome-free preflight complete'}
    # JSON persists tuples as lists. Compare canonical persisted structures,
    # rather than rejecting an unchanged design on its container type alone.
    return protocol, groups, cache, json.loads(json.dumps(manifest))


def evaluate(protocol, groups, cache, manifest):
    saved = json.loads((OUT/'preflight.json').read_text())
    if saved != manifest:
        raise ValueError('Preflight code or designs changed; repeat blinded validation before unblinding')
    signal_manifest = json.loads((OUT/'signals-manifest.json').read_text())
    if signal_manifest['preflight_sha256'] != digest(OUT/'preflight.json'):
        original_path = OUT/'preflight-v1.json'
        original = json.loads(original_path.read_text())
        amendment = json.loads((OUT/'preflight-amendment.json').read_text())
        changed = {name for name in saved['code_sha256'] if saved['code_sha256'][name] != original['code_sha256'][name]}
        if (digest(original_path) != signal_manifest['preflight_sha256']
                or amendment['new_preflight_sha256'] != digest(OUT/'preflight.json')
                or original['designs'] != saved['designs']
                or original['protocol_freeze_sha256'] != saved['protocol_freeze_sha256']
                or changed != {'scripts/kryeziu_confirmation.py'}):
            raise ValueError('Unblinding/preflight amendment chain is inconsistent')
    signal_path = ROOT/'data/raw/kryeziu/signals-projection.csv'
    if digest(signal_path) != signal_manifest['sha256']:
        raise ValueError('Signal projection hash mismatch')
    started = {'started_utc': datetime.now(timezone.utc).isoformat(), 'preflight_sha256': digest(OUT/'preflight.json')}
    with (OUT/'evaluation-started.json').open('x') as handle:
        json.dump(started, handle, indent=2)
    signals = pd.read_csv(signal_path, dtype=str, keep_default_na=False)
    signals.index = signals.source_row.astype(int)
    if signals.index.duplicated().any():
        raise ValueError('Duplicate signal source row')
    values = pd.to_numeric(signals.signal, errors='coerce')
    invalid = ~np.isfinite(values) | values.le(0)
    bad = set(values.index[invalid])
    exclusions, frames = [], []
    for geometry in sorted(groups):
        targets, control_count = geometry
        targets = np.array(targets)
        contexts = []
        for row in groups[geometry]:
            failed = sorted(bad.intersection(row['pool_rows']+row['audit_rows']+row['audit_controls']))
            if failed:
                exclusions.append({**{k: row[k] for k in ['context', 'patient', 'orientation']},
                                   'invalid_source_rows': failed,
                                   'reasons': {str(i): ('missing_or_nonfinite' if not np.isfinite(values.loc[i])
                                                        else 'nonpositive') for i in failed}})
            else:
                contexts.append(row)
        if not contexts:
            continue
        log_pool = np.log(np.array([values.loc[row['pool_rows']].to_numpy(float) for row in contexts]))
        truth = np.array([np.log(values.loc[row['audit_rows']].to_numpy(float))-
                          np.log(values.loc[row['audit_controls']].to_numpy(float)).mean() for row in contexts])
        audit_counts = np.array([len(row['audit_controls']) for row in contexts])
        accumulated = {}
        for plan in cache[geometry]:
            prediction = predict(plan, log_pool, targets, control_count)
            error = prediction-truth
            metrics = {'mse': np.mean(error**2, axis=1)}
            if plan.variance is not None:
                sd = np.sqrt(plan.variance[None, :]+protocol['fixed_model']['noise_sd']**2*(1+1/audit_counts[:, None]))
                metrics['coverage90'] = np.mean(np.abs(error) <= 1.6448536269514722*sd, axis=1)
                metrics['width90'] = np.mean(2*1.6448536269514722*sd, axis=1)
            key = (plan.method, plan.budget)
            if key not in accumulated:
                accumulated[key] = [0, {name: np.zeros(len(contexts)) for name in metrics}]
            accumulated[key][0] += 1
            for name, value in metrics.items():
                accumulated[key][1][name] += value
        identity = pd.DataFrame([{k: row[k] for k in ['context', 'patient', 'sample_id', 'run_id', 'library_id', 'drug', 'orientation']}
                                 for row in contexts])
        for (method, budget), (count, metrics) in accumulated.items():
            expected = 20 if method.startswith('random_') else 1
            if count != expected:
                raise AssertionError('Incomplete random seeds or duplicated deterministic plan')
            frame = identity.assign(method=method, budget=budget, full_pool_size=log_pool.shape[1], seed_count=count)
            for name, value in metrics.items():
                frame[name] = value/count
            frames.append(frame)
    if not frames:
        raise ValueError('No valid confirmation contexts')
    result = pd.concat(frames, ignore_index=True)
    if not np.isfinite(result.mse).all():
        raise ArithmeticError('Nonfinite confirmation loss')
    result.to_csv(OUT/'results.csv.gz', index=False, float_format='%.12g', compression={'method': 'gzip', 'mtime': 0})
    (OUT/'exclusions.json').write_text(json.dumps(exclusions, indent=2)+'\n')
    summary = summarize(result)
    (OUT/'confirmation.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


def summarize(result):
    # Budget mean first; contexts (including runs/drugs) within samples, then
    # samples within patients. Computational seeds have already been averaged.
    per_context = result.groupby(['orientation', 'patient', 'sample_id', 'context', 'method']).mse.mean()
    per_sample = per_context.groupby(['orientation', 'patient', 'sample_id', 'method']).mean()
    per_patient = per_sample.groupby(['orientation', 'patient', 'method']).mean()
    per_patient.rename('mean_budget_mse').to_csv(OUT/'patient-results.csv', float_format='%.12g')
    reports = {}
    for orientation in ['p1_to_p2', 'p2_to_p1']:
        table = per_patient.loc[orientation].unstack('method')
        if table.isna().any().any():
            raise ValueError('Unmatched patient methods')
        draws = np.random.default_rng(1729).integers(0, len(table), (10000, len(table)))
        a, b = table.exact_joint.to_numpy(), table.random_joint.to_numpy()
        if b.mean() <= 0:
            raise ValueError('Relative effect undefined for zero reference MSE')
        delta = (a-b)[draws].mean(axis=1)
        ratio = 1-a[draws].mean(axis=1)/b[draws].mean(axis=1)
        interval = np.quantile(delta, [.025, .975])
        reduction = float(1-a.mean()/b.mean())
        reports[orientation] = {'patients': len(table), 'mean_budget_mse': table.mean().to_dict(),
                                'paired_difference': float((a-b).mean()), 'difference_interval95': interval.tolist(),
                                'relative_reduction': reduction, 'relative_reduction_interval95': np.quantile(ratio, [.025, .975]).tolist(),
                                'primary_criteria_met': bool(reduction >= .05 and interval[1] < 0)}
        sub = result[result.orientation.eq(orientation)].copy()
        reference_budget = np.ceil(.75*sub.full_pool_size).astype(int)
        candidate_budget = np.floor(.8*reference_budget).astype(int)
        selected = sub[(sub.method.eq('random_joint') & sub.budget.eq(reference_budget)) |
                       (sub.method.eq('exact_joint') & sub.budget.eq(candidate_budget))]
        sample = selected.groupby(['patient', 'sample_id', 'method']).mse.mean()
        patient = sample.groupby(['patient', 'method']).mean().unstack('method')
        patient = patient.reindex(table.index)
        if patient.isna().any().any() or candidate_budget.min() < 3:
            raise ValueError('Invalid secondary efficiency comparison')
        a, b = patient.exact_joint.to_numpy(), patient.random_joint.to_numpy()
        ratios = a[draws].mean(axis=1)/b[draws].mean(axis=1)
        interval = np.quantile(ratios, [.025, .975])
        reports[orientation]['efficiency_secondary'] = {'mse_ratio': float(a.mean()/b.mean()),
                                                       'ratio_interval95': interval.tolist(),
                                                       'noninferiority_criteria_met': bool(interval[1] <= 1.05)}
    return {'status': 'first frozen-protocol independent outcome evaluation', 'orientations': reports,
            'interpretation': 'Primary conclusion uses p1_to_p2 only. Reverse orientation is sensitivity. No rank or clinical guarantee.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evaluate', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    protocol, groups, cache, manifest = prepare()
    if args.evaluate:
        evaluate(protocol, groups, cache, manifest)
    else:
        target = OUT/'preflight.json'
        if target.exists() and json.loads(target.read_text()) != manifest:
            raise ValueError('Existing preflight differs; explicit amendment required')
        target.write_text(json.dumps(manifest, indent=2)+'\n')
        print(json.dumps({k: v for k, v in manifest.items() if k != 'designs'}, indent=2))
        print('Unique designs:', len(manifest['designs']), flush=True)


if __name__ == '__main__':
    main()
