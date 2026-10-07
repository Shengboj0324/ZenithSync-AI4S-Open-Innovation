from copy import deepcopy

import numpy as np
import pytest

from zenithsync.well_workflow import plan_wells


def request():
    return {'schema_version': 1, 'assay_context': 'research_single_agent_organoid',
            'experiment_id': 'synthetic-contract-test', 'plate_id': 'plate-1', 'concentration_unit': 'nM',
            'reference_control_id': 'c1', 'future_control_count': 2, 'additional_wells': 2,
            'wells': [{'id': 'c1', 'kind': 'vehicle_control', 'dose': 0, 'signal': 100},
                      {'id': 'c2', 'kind': 'vehicle_control', 'dose': 0, 'signal': None},
                      {'id': 'c3', 'kind': 'vehicle_control', 'dose': 0, 'signal': None},
                      *[{'id': f't{i}', 'kind': 'treatment', 'dose': d, 'signal': signal}
                        for i, (d, signal) in enumerate([(1, 95), (10, None), (100, None), (1000, 10)])]]}


def test_well_budget_and_conditional_variance_contract():
    value = request()
    result = plan_wells(value)
    assert len(result['selected_wells']) == result['additional_wells'] == 2
    assert result['observed_wells'] == 3
    assert not {r['id'] for r in result['selected_wells']} & {'c1', 't0', 't3'}
    before = np.mean([p['latent_variance'] for p in result['predictions']])
    after = np.mean([p['expected_latent_variance_after_batch'] for p in result['predictions']])
    assert before-after == pytest.approx(result['variance_reduction'])
    assert after < before
    assert value == request()


def test_scale_and_dose_unit_equivalence():
    value = request()
    first = plan_wells(value)
    second = deepcopy(value)
    second['concentration_unit'] = 'uM'
    for well in second['wells']:
        well['dose'] /= 1000
        if well['signal'] is not None:
            well['signal'] *= 1e20
    other = plan_wells(second)
    assert [r['id'] for r in first['selected_wells']] == [r['id'] for r in other['selected_wells']]
    np.testing.assert_allclose([p['mean_log_response'] for p in first['predictions']],
                               [p['mean_log_response'] for p in other['predictions']], atol=1e-12)


@pytest.mark.parametrize('defect', ['missing_control', 'nonpositive', 'bool_budget', 'excess_budget',
                                   'missing_extreme', 'duplicate_id', 'extra_field', 'mixed_units'])
def test_invalid_requests_are_rejected(defect):
    value = request()
    if defect == 'missing_control':
        value['wells'][0]['signal'] = None
    elif defect == 'nonpositive':
        value['wells'][0]['signal'] = 0
    elif defect == 'bool_budget':
        value['additional_wells'] = True
    elif defect == 'excess_budget':
        value['additional_wells'] = 10
    elif defect == 'missing_extreme':
        value['wells'][-1]['signal'] = None
    elif defect == 'duplicate_id':
        value['wells'][-1]['id'] = 'c1'
    elif defect == 'extra_field':
        value['private_truth'] = [1, 2, 3]
    else:
        value['wells'][-1]['unit'] = 'uM'
    with pytest.raises(ValueError):
        plan_wells(value)


def test_zero_budget_and_full_observation_are_valid():
    value = request()
    value['additional_wells'] = 0
    result = plan_wells(value)
    assert result['selected_wells'] == [] and result['variance_reduction'] == 0
    for well in value['wells']:
        if well['signal'] is None:
            well['signal'] = 50
    assert plan_wells(value)['optimization']['subsets_represented'] == 1


def test_extreme_finite_dose_ratio_does_not_overflow():
    value = request()
    for well, dose in zip(value['wells'][3:], [1e-308, 1., 1e100, 1e308], strict=True):
        well['dose'] = dose
    result = plan_wells(value)
    assert all(np.isfinite(p['mean_log_response']) for p in result['predictions'])


def test_arbitrary_precision_json_integer_is_rejected_cleanly():
    value = request()
    value['wells'][0]['signal'] = 10**400
    with pytest.raises(ValueError, match='floating-point range'):
        plan_wells(value)


def test_large_search_is_rejected_before_enumeration():
    value = request()
    value['wells'].extend({'id': f'extra-{i}', 'kind': 'treatment', 'dose': i+2., 'signal': None}
                          for i in range(14))
    with pytest.raises(ValueError, match='enumeration bound exceeded'):
        plan_wells(value)
