"""Outcome-free admission of paired plate dose curves; no response filtering."""
from decimal import Decimal, InvalidOperation
import hashlib
import json

import pandas as pd

GROUP = ['sample_id', 'run_id', 'library_id']


def load_design(path, record_path):
    record = json.loads(record_path.read_text())
    expected = next(s['sha256'] for s in record['sheets'] if s['design_file'] == path.name)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('Design projection hash mismatch')
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    if 'signal' in frame or 'viability' in frame:
        raise ValueError('Outcome fields are forbidden during design admission')
    if frame.duplicated(['source_sheet', 'source_row']).any():
        raise ValueError('Source row identities must be unique')
    return frame


def canonical_dose(value):
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError('Invalid drug concentration') from error
    if not number.is_finite() or number <= 0:
        raise ValueError('Drug concentrations must be finite and positive')
    return str(number.normalize())


def paired_inventory(frame):
    """Pair p1/p2 only within sample, run, library and exact drug/dose support.

    Control identities come from source compound_type and name, not assumed
    numeric-zero conventions. Their inconsistent concentration labels are kept
    as an unresolved source annotation rather than silently repaired.
    """
    if not set(frame.plate).issubset({'p1', 'p2'}):
        raise ValueError('Unknown plate label requires source review')
    controls = frame[frame.compound_type.eq('control_negative')]
    if not controls.compound_name.eq('DMSO').all():
        raise ValueError('Unrecognized negative control identity')
    single = frame[frame.compound_type.eq('single')].copy()
    physical = pd.concat([single, controls], ignore_index=True)
    if physical.duplicated([*GROUP, 'plate', 'drow', 'dcol']).any():
        raise ValueError('Single-agent/control physical well identities are duplicated')
    single['canonical_dose'] = single.concentration.map(canonical_dose)
    control_map = {tuple(key): group for key, group in controls.groupby([*GROUP, 'plate'], sort=True)}
    decisions, cohorts = [], []
    for key, curve in single.groupby([*GROUP, 'compound_name'], sort=True):
        reason = ''
        one, two = curve[curve.plate.eq('p1')], curve[curve.plate.eq('p2')]
        c1, c2 = control_map.get((*key[:3], 'p1')), control_map.get((*key[:3], 'p2'))
        if not curve.concentration_unit.eq('nM').all():
            reason = 'non-nM or unknown concentration unit'
        elif one.empty or two.empty:
            reason = 'missing paired plate'
        elif one.canonical_dose.duplicated().any() or two.canonical_dose.duplicated().any():
            reason = 'duplicate dose within one plate'
        elif set(one.canonical_dose) != set(two.canonical_dose):
            reason = 'plate dose supports differ'
        elif len(one) < 4:
            reason = 'fewer than four paired drug doses'
        elif c1 is None or c2 is None or len(c1) < 2 or len(c2) < 2:
            reason = 'insufficient separately labeled plate controls'
        row = dict(zip([*GROUP, 'compound_name'], key))
        decisions.append({**row, 'admitted_by_design': not reason, 'reason': reason,
                          'p1_doses': len(one), 'p2_doses': len(two),
                          'p1_controls': 0 if c1 is None else len(c1),
                          'p2_controls': 0 if c2 is None else len(c2)})
        if reason:
            continue
        cohorts.append({**row,
                        'pool_treatment_source_rows': one.source_row.astype(int).tolist(),
                        'audit_treatment_source_rows': two.source_row.astype(int).tolist(),
                        'pool_control_source_rows': c1.source_row.astype(int).tolist(),
                        'audit_control_source_rows': c2.source_row.astype(int).tolist()})
    return pd.DataFrame(decisions), cohorts
