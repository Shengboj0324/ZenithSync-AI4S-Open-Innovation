import numpy as np
import pytest

from zenithsync.confirmation import build_plans, predict
from zenithsync.contrast_gp import ContrastGP

PARAMETERS = dict(amplitude=1., length=.5, noise_sd=.3, slope=2., correlated=True)


@pytest.fixture(scope='module')
def design():
    targets = np.array([.1, .3, .7, 1.])
    plans, records = build_plans(targets, 3, PARAMETERS)
    return targets, plans, records


def test_all_plans_have_budget_accounting_and_no_repeated_wells(design):
    _, plans, records = design
    for plan in plans:
        assert len(plan.selected) == len(set(plan.selected)) == plan.budget
        assert plan.selected[:3] == (0, 3, 6)
    assert all(r['subsets_represented'] == 16 for r in records)
    assert {p.budget for p in plans} == set(range(3, 8))


def test_batched_predictions_equal_direct_conditioning(design):
    targets, plans, _ = design
    pool = np.random.default_rng(9).normal(size=(3, 7))
    for plan in plans:
        if plan.weights is None:
            continue
        model = ContrastGP(**{**PARAMETERS, 'correlated': not plan.method.endswith('diagonal')})
        law = model.joint(targets, np.r_[0., 0., targets])
        indices = [4+i-1 for i in plan.selected if i != 0]
        expected = [law.condition(indices, row[[i for i in plan.selected if i != 0]]-row[0]).mean[:4]
                    for row in pool]
        np.testing.assert_allclose(predict(plan, pool, targets, 3), expected, atol=2e-14)


def test_unpurchased_values_and_global_signal_scale_cannot_change_predictions(design):
    targets, plans, _ = design
    pool = np.random.default_rng(10).normal(size=(2, 7))
    for plan in plans:
        if plan.budget != 4:
            continue
        expected = predict(plan, pool, targets, 3)
        poisoned = pool.copy()
        poisoned[:, [i for i in range(7) if i not in plan.selected]] = np.nan
        np.testing.assert_array_equal(predict(plan, poisoned, targets, 3), expected)
        np.testing.assert_allclose(predict(plan, pool+7, targets, 3), expected, atol=1e-14)


def test_full_information_methods_agree_across_design_policies(design):
    targets, plans, _ = design
    pool = np.random.default_rng(11).normal(size=(2, 7))
    outputs = {name: [] for name in ['joint', 'diagonal']}
    for plan in plans:
        if plan.budget == 7 and plan.weights is not None:
            outputs['diagonal' if plan.method.endswith('diagonal') else 'joint'].append(predict(plan, pool, targets, 3))
    for results in outputs.values():
        for result in results:
            np.testing.assert_allclose(result, results[0], atol=1e-14)
    interpolation = [predict(p, pool, targets, 3) for p in plans if p.budget == 7 and p.weights is None]
    expected = pool[:, 3:]-pool[:, :3].mean(axis=1)[:, None]
    for result in interpolation:
        np.testing.assert_allclose(result, expected, atol=1e-14)
