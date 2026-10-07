from dataclasses import replace
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from zenithsync.contrast_gp import ContrastGP
from zenithsync.farin_replay import partition_curves

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/farin_gp_benchmark.py'
SPEC = importlib.util.spec_from_file_location('farin_gp_runner', SCRIPT)
RUNNER = importlib.util.module_from_spec(SPEC)
# The runner's companion script is loaded explicitly so test imports do not
# depend on the shell's working directory or an installed scripts package.
COMPANION = importlib.util.spec_from_file_location('farin_replay_benchmark', SCRIPT.with_name('farin_replay_benchmark.py'))
COMPANION_MODULE = importlib.util.module_from_spec(COMPANION)
COMPANION.loader.exec_module(COMPANION_MODULE)
import sys
sys.modules['farin_replay_benchmark'] = COMPANION_MODULE
SPEC.loader.exec_module(RUNNER)


def curve(identifier='O01'):
    frame = pd.DataFrame([
        {'curve_id': identifier+':fixture', 'organoid_id': identifier, 'concentration': float(d),
         'replicate_label': str(r), 'source_row': d*3+r, 'is_control': d == 0,
         'eligible': True, 'raw_luminescence': float(100*np.exp(-d/4)*(1+.02*r))}
        for d in range(8) for r in (1, 2, 3)
    ])
    return partition_curves(frame)[0][0]


def test_replay_never_reads_audit_and_hides_unmeasured_pool_values():
    original = curve()
    poisoned_pool, poisoned_audit = original.pool.copy(), original.audit.copy()
    poisoned_pool.loc[~poisoned_pool.index.isin([0, 2, 14]), 'raw_luminescence'] = 1e20
    poisoned_audit.loc[:, 'raw_luminescence'] = 1e30
    poisoned = replace(original, pool=poisoned_pool, audit=poisoned_audit)
    model = ContrastGP(1., .5, .3, 2.)
    a = next(RUNNER.replay(original, model, 'ivr', None))
    b = next(RUNNER.replay(poisoned, model, 'ivr', None))
    assert a[0] == b[0] == 3
    np.testing.assert_array_equal(a[1], b[1])
    np.testing.assert_array_equal(a[2], b[2])
    assert a[4] == b[4]
    audit_only = replace(original, audit=poisoned_audit)
    for a, b in zip(RUNNER.replay(original, model, 'ivr', None),
                    RUNNER.replay(audit_only, model, 'ivr', None), strict=True):
        np.testing.assert_array_equal(a[1], b[1])
        assert a[4] == b[4]


def test_complete_information_posterior_is_policy_invariant():
    original, model = curve(), ContrastGP(1., .5, .3, 2.)
    outputs = [list(RUNNER.replay(original, model, policy, seed))[-1]
               for policy, seed in [('ivr', None), ('space_filling', None), ('random', 7)]]
    for result in outputs:
        assert result[0] == 16 and len(set(result[4])) == 16
        np.testing.assert_allclose(result[1], outputs[0][1], atol=1e-12)
        np.testing.assert_allclose(result[2], outputs[0][2], atol=1e-12)


def test_tuning_excludes_entire_held_id_and_every_audit_outcome():
    a, b = curve('O01'), curve('O02')
    before = RUNNER.fit_leave_id_out([a, b])[0]
    poisoned = a.pool.copy()
    poisoned.raw_luminescence = np.exp(np.linspace(1, 15, len(poisoned)))
    audits = a.audit.copy()
    audits.raw_luminescence = 1e30
    after, _, ledger = RUNNER.fit_leave_id_out([replace(a, pool=poisoned, audit=audits),
                                              replace(b, audit=audits) ])
    for mode in ['joint', 'diagonal']:
        assert before[('O01', mode)] == after[('O01', mode)]
    assert all(row['held_out_organoid_id'] not in row['training_ids'] for row in ledger)
