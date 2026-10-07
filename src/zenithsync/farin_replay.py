"""Measured-well replay with a separate audit replicate and counted controls.

Replicate labels define a retrospective partition, not independent patients or
plates. Policies receive public design metadata and revealed responses only.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ReplayCurve:
    curve_id: str
    organoid_id: str
    doses: tuple[float, ...]
    pool: pd.DataFrame
    audit: pd.DataFrame


def partition_curves(frame):
    """Admit complete 8-dose by 3-label rectangles; return every rejection."""
    accepted, decisions = [], []
    for curve_id, group in frame.groupby('curve_id', sort=True):
        doses = tuple(sorted(group.concentration.unique()))
        labels = set(group.replicate_label)
        reason = ''
        if not group.eligible.all():
            reason = 'author exclusion, ambiguity or nonpositive measurement'
        elif len(doses) != 8 or doses[0] != 0 or labels != {'1', '2', '3'}:
            reason = 'requires one control and seven doses with labels 1, 2, 3'
        elif (len(group) != 24 or group.duplicated(['concentration', 'replicate_label']).any()
              or not group.groupby('concentration').size().eq(3).all()
              or not (group.is_control == group.concentration.eq(0)).all()):
            reason = 'incomplete or inconsistent dose by replicate rectangle'
        decisions.append({'curve_id': curve_id, 'admitted': not reason, 'reason': reason})
        if reason:
            continue
        ordered = group.sort_values(['concentration', 'replicate_label'])
        pool = ordered[ordered.replicate_label.isin(['1', '2'])].copy().reset_index(drop=True)
        audit = ordered[ordered.replicate_label.eq('3')].copy().reset_index(drop=True)
        accepted.append(ReplayCurve(curve_id, str(group.organoid_id.iloc[0]), doses, pool, audit))
    return accepted, pd.DataFrame(decisions)


class WellOracle:
    """One row costs one assay; hidden values never appear in design metadata."""
    def __init__(self, curve):
        self._pool = curve.pool.copy(deep=True)
        self._revealed = []
        self.curve_id = curve.curve_id
        self.design = self._pool[['source_row', 'concentration', 'replicate_label', 'is_control']].copy()
        self.design['cost'] = 1

    @property
    def spent(self):
        return len(self._revealed)

    @property
    def observations(self):
        return self._pool.iloc[self._revealed][
            ['source_row', 'concentration', 'replicate_label', 'is_control', 'raw_luminescence']
        ].copy()

    def reveal(self, index):
        if isinstance(index, (bool, np.bool_)) or not isinstance(index, (int, np.integer)):
            raise ValueError('Action must be an integer pool index')
        if index < 0 or index >= len(self._pool) or index in self._revealed:
            raise ValueError('Action is out of range or was already measured')
        self._revealed.append(int(index))
        return self.observations.iloc[-1].copy()


def audit_log_response(curve):
    """Noisy audit endpoint: log treatment signal minus log its held-out control."""
    audit = curve.audit.sort_values('concentration')
    return np.log(audit.raw_luminescence.to_numpy()[1:]) - np.log(audit.raw_luminescence.iloc[0])


def interpolation_prediction(observations, doses, *, method='linear'):
    """Mean log signals, measured-control normalization, constant extrapolation."""
    from scipy.interpolate import PchipInterpolator

    if method not in {'linear', 'pchip', 'constant'}:
        raise ValueError('Unknown interpolation baseline')
    if len(observations) == 0 or not observations.is_control.any():
        raise ValueError('A measured control is mandatory')
    values = observations.copy()
    values['log_signal'] = np.log(values.raw_luminescence)
    means = values.groupby('concentration').log_signal.mean()
    reference = min(d for d in doses if d > 0)
    query = np.log1p(np.asarray(doses[1:]) / reference)
    x = np.log1p(means.index.to_numpy() / reference)
    y = means.to_numpy() - means.loc[0]
    if method == 'constant':
        return np.full(len(query), y[1:].mean() if len(y) > 1 else 0.)
    if method == 'linear' or len(x) < 3:
        return np.interp(query, x, y)
    # Endpoint clipping explicitly matches the linear baseline's extrapolation.
    return PchipInterpolator(x, y)(np.clip(query, x[0], x[-1]))
