from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from zenithsync.farin_replay import (
    WellOracle, audit_log_response, interpolation_prediction, partition_curves,
)


def complete_frame():
    return pd.DataFrame([
        {'curve_id': 'example', 'organoid_id': 'O01', 'concentration': float(dose),
         'replicate_label': str(rep), 'source_row': 3 * dose + rep,
         'is_control': dose == 0, 'eligible': True,
         'raw_luminescence': float(100 / (dose + 1))}
        for dose in range(8) for rep in (1, 2, 3)
    ])


def test_partition_is_disjoint_and_complete():
    curves, ledger = partition_curves(complete_frame())
    curve, = curves
    assert ledger.admitted.all()
    assert len(curve.pool) == 16 and len(curve.audit) == 8
    assert set(curve.pool.source_row).isdisjoint(curve.audit.source_row)
    assert set(curve.pool.source_row) | set(curve.audit.source_row) == set(range(1, 25))
    np.testing.assert_allclose(audit_log_response(curve), -np.log(np.arange(2, 9)))


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'excluded', 'label', 'control'])
def test_partition_rejects_ambiguous_or_incomplete_curves(defect):
    frame = complete_frame()
    if defect == 'missing':
        frame = frame.iloc[:-1]
    elif defect == 'duplicate':
        frame.loc[1, 'replicate_label'] = '1'
    elif defect == 'excluded':
        frame.loc[1, 'eligible'] = False
    elif defect == 'label':
        frame.loc[1, 'replicate_label'] = '4'
    else:
        frame.loc[1, 'is_control'] = False
    curves, ledger = partition_curves(frame)
    assert not curves and not ledger.admitted.any()
    assert ledger.reason.str.len().gt(0).all()


def test_oracle_counts_controls_and_rejects_repeat_measurements():
    curve = partition_curves(complete_frame())[0][0]
    oracle = WellOracle(curve)
    assert 'raw_luminescence' not in oracle.design
    assert oracle.spent == 0
    oracle.reveal(0)
    assert oracle.spent == 1 and oracle.observations.is_control.all()
    for index in [0, -1, 16, True, 1.5]:
        with pytest.raises(ValueError):
            oracle.reveal(index)
    assert oracle.spent == 1
    copied = oracle.observations
    copied.loc[:, 'raw_luminescence'] = 999.
    assert oracle.observations.raw_luminescence.iloc[0] == 100.


def test_hidden_pool_and_audit_values_cannot_change_observed_predictions():
    curve = partition_curves(complete_frame())[0][0]
    pool, audit = curve.pool.copy(), curve.audit.copy()
    # Preserve only the three revealed wells: initial control and dose extremes.
    selected = [0, 2, 14]
    pool.loc[~pool.index.isin(selected), 'raw_luminescence'] = 1e30
    audit.loc[:, 'raw_luminescence'] = 1e-30
    poisoned = replace(curve, pool=pool, audit=audit)
    a, b = WellOracle(curve), WellOracle(poisoned)
    pd.testing.assert_frame_equal(a.design, b.design)
    for index in selected:
        a.reveal(index)
        b.reveal(index)
    for method in ['linear', 'pchip', 'constant']:
        np.testing.assert_array_equal(
            interpolation_prediction(a.observations, curve.doses, method=method),
            interpolation_prediction(b.observations, curve.doses, method=method))


def test_log_interpolation_recovers_fixture_and_is_scale_invariant():
    curve = partition_curves(complete_frame())[0][0]
    oracle = WellOracle(curve)
    for index in [0, 2, 14]:
        oracle.reveal(index)
    expected = -np.log(np.arange(2, 9))
    prediction = interpolation_prediction(oracle.observations, curve.doses)
    np.testing.assert_allclose(prediction, expected)
    scaled = oracle.observations
    scaled.raw_luminescence *= 123.
    np.testing.assert_allclose(interpolation_prediction(scaled, curve.doses), expected)
