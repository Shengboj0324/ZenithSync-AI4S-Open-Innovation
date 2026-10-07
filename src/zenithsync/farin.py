"""Traceable development-data adapter; ambiguous curves are not silently repaired."""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_HASH = 'f9a9a51fd77ae1a5b19ad71fc236ce446223b3c2fcc66631ab304ab69bec78f0'
KEYS = ['Organoid ID', 'Mono-/Coculture', 'Fibroblast ID', 'Drug']
REQUIRED = ['No.', *KEYS, 'Concentration', 'Replicate', 'RLU value', 'Used  value/comment']
UNITS = {'5-FU': 'uM', 'Oxa': 'uM', 'SN-38': 'nM', 'Gef': 'uM'}


def load_farin(path, *, expected_sha256=SOURCE_HASH):
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError('Farin input hash does not match the declared source')
    frame = pd.read_csv(path, sep='\t', dtype=str, keep_default_na=False)
    if not set(REQUIRED).issubset(frame.columns):
        raise ValueError('Source schema lacks required fields')
    extra = [column for column in frame.columns if column not in REQUIRED]
    if any(frame[column].str.strip().ne('').any() for column in extra):
        raise ValueError('Unexpected nonempty columns require source review')
    blank = frame.apply(lambda col: col.str.strip().eq('')).all(axis=1)
    frame = frame.loc[~blank, REQUIRED].copy()
    for col in REQUIRED:
        frame[col] = frame[col].str.strip()
    numbers = pd.to_numeric(frame['No.'], errors='raise')
    replicate = pd.to_numeric(frame['Replicate'], errors='raise')
    if (numbers.duplicated().any() or not np.isfinite(numbers).all()
            or (numbers <= 0).any() or (numbers % 1 != 0).any()
            or not np.isfinite(replicate).all() or (replicate <= 0).any()
            or (replicate % 1 != 0).any()):
        raise ValueError('Source row numbers must be unique; row/replicate IDs positive integers')
    if (not frame['Drug'].isin(UNITS).all()
            or not frame['Mono-/Coculture'].isin(['Monoculture', 'Coculture']).all()
            or not frame['Organoid ID'].str.fullmatch(r'O\d+').all()):
        raise ValueError('Unknown source identity, drug or culture type')
    mono = frame['Mono-/Coculture'].eq('Monoculture')
    if (mono & frame['Fibroblast ID'].ne('')).any() or (~mono & frame['Fibroblast ID'].eq('')).any():
        raise ValueError('Culture and fibroblast identifiers disagree')
    raw = pd.to_numeric(frame['RLU value'], errors='raise')
    if not np.isfinite(raw).all() or (raw < 0).any():
        raise ValueError('Raw luminescence must be finite and nonnegative')
    used = pd.to_numeric(frame['Used  value/comment'], errors='coerce')
    rejected = used.isna()
    if not frame.loc[rejected, 'Used  value/comment'].isin(['cells lost', 'seeding not uniform']).all():
        raise ValueError('Unrecognized exclusion annotation requires review')
    if not np.isfinite(used[~rejected]).all() or (used[~rejected] != raw[~rejected]).any():
        raise ValueError('Used values differ from raw measurements; review required')
    control = frame['Concentration'].eq('DMSO')
    dose = pd.to_numeric(frame['Concentration'].where(~control, '0'), errors='raise')
    if not np.isfinite(dose).all() or (dose < 0).any():
        raise ValueError('Concentrations must be finite and nonnegative')
    # Numeric zero appears among nonzero drug dilutions. Its intended value is
    # unknown; never impute it from adjacent rows or relabel it as a DMSO control.
    ambiguous = (~control & dose.eq(0)) | frame.duplicated(
        [*KEYS, 'Concentration', 'Replicate'], keep=False)
    curve_keys = pd.MultiIndex.from_frame(frame[KEYS])
    ambiguous_keys = set(curve_keys[ambiguous])
    bad_curve = np.asarray([key in ambiguous_keys for key in curve_keys])
    result = pd.DataFrame({
        'source_row': numbers.astype(int), 'organoid_id': frame['Organoid ID'],
        'culture': frame['Mono-/Coculture'], 'fibroblast_id': frame['Fibroblast ID'],
        'drug': frame['Drug'], 'concentration_label': frame['Concentration'],
        'concentration': dose, 'concentration_unit': frame['Drug'].map(UNITS),
        'replicate_label': frame['Replicate'], 'is_control': control,
        'raw_luminescence': raw, 'author_exclusion': frame['Used  value/comment'].where(rejected, ''),
        'ambiguous_curve': bad_curve,
        'eligible': ~rejected & ~bad_curve & (raw > 0),
    })
    result['curve_id'] = [':'.join(key) for key in curve_keys]
    result['source_doi'] = '10.17632/fypp6xhkjy.1'
    return result.reset_index(drop=True)


def profile_farin(frame):
    """Admission evidence, not patient independence or operational validation."""
    eligible = frame[frame.eligible]
    curves = []
    for curve_id, group in frame.groupby('curve_id', sort=True):
        admitted = group[group.eligible]
        curves.append({'curve_id': curve_id, 'rows': len(group),
                       'eligible_rows': len(admitted),
                       'eligible_controls': int(admitted.is_control.sum()),
                       'eligible_nonzero_doses': int(admitted.loc[~admitted.is_control, 'concentration'].nunique()),
                       'ambiguous': bool(group.ambiguous_curve.any())})
    return {
        'role': 'development', 'rows': len(frame), 'curves': len(curves),
        'organoid_ids': sorted(frame.organoid_id.unique()),
        'patient_independence_verified': False, 'plate_ids_available': False,
        'author_excluded_rows': int(frame.author_exclusion.ne('').sum()),
        'ambiguous_curve_rows': int(frame.ambiguous_curve.sum()),
        'eligible_rows': len(eligible),
        'ambiguous_curves': sorted(frame.loc[frame.ambiguous_curve, 'curve_id'].unique()),
        'zero_dose_source_rows': frame.loc[~frame.is_control & frame.concentration.eq(0), 'source_row'].tolist(),
        'curve_inventory': curves,
    }
