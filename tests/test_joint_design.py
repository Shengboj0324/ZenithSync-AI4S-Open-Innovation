import numpy as np
import pytest

from zenithsync.joint_design import JointGaussian, exact_budget_design, exact_cardinality_designs, shared_control_noise


def suppressor_law():
    # T=Z2; X1=Z1+e1; X2=Z1+Z2+e2. Independent errors have variance .1.
    return JointGaussian(np.zeros(3), [[1, 0, 1], [0, 1.1, 1], [1, 1, 2.1]])


def test_conditional_suppressor_counterexample():
    law = suppressor_law()
    assert law.variance_reduction([0], [1], [1]) == 0
    conditional = law.condition([2], [2])
    assert conditional.variance_reduction([0], [1], [1]) == pytest.approx(1000/2751)
    assert conditional.mean[0] == pytest.approx(2/2.1)


def test_exact_count_design_handles_non_nested_optima_and_greedy_failure():
    # Add X3=T+e3 with noise variance .5 to the suppressor example.
    law = JointGaussian(np.zeros(4), [[1, 0, 1, 1], [0, 1.1, 1, 0],
                                      [1, 1, 2.1, 1], [1, 0, 1, 1.5]])
    result = exact_cardinality_designs(law, [0], [1, 2, 3], [1])
    assert result[1]['actions'] == (3,)
    assert result[2]['actions'] == (1, 2)
    assert sum(item['subsets_evaluated'] for item in result) == 8
    assert result[2]['variance_reduction'] > law.variance_reduction([0], [2, 3], [1])
    for count, item in enumerate(result):
        reference = exact_budget_design(law, [0], [1, 2, 3], [1], [1]*3, count)
        assert item['variance_reduction'] == pytest.approx(reference['variance_reduction'])


def test_batch_conditioning_equals_sequential_with_correlated_noise():
    prior = np.exp(-np.abs(np.arange(3)[:, None]-np.arange(3)[None, :]))
    noise = shared_control_noise([.1, .2, .3], ['a', 'a', 'a'], {'a': .4})
    law = JointGaussian(np.zeros(6), np.block([[prior, prior], [prior, prior+noise]]))
    batch = law.condition([3, 4], [.7, -.2])
    sequential = law.condition([3], [.7]).condition([4], [-.2])
    np.testing.assert_allclose(batch.mean, sequential.mean, atol=1e-14)
    np.testing.assert_allclose(batch.covariance, sequential.covariance, atol=1e-14)
    gain = law.variance_reduction([0, 1, 2], [3, 4], [1/3]*3)
    actual = np.mean(np.diag(prior)-np.diag(batch.covariance)[:3])
    assert gain == pytest.approx(actual)
    assert 0 <= gain <= 1


def test_shared_control_uncertainty_floor_and_blocks():
    covariance = shared_control_noise([1]*10, ['a']*10, {'a': 1})
    assert covariance.sum()/100 == pytest.approx(1.1)
    separate = shared_control_noise([1, 1], ['a', 'b'], {'a': 2, 'b': 3})
    np.testing.assert_array_equal(separate, [[3, 0], [0, 4]])


def test_exact_budget_selection_accounts_for_setup():
    law = suppressor_law()
    result = exact_budget_design(law, [0], [1, 2], [1], [1, 1], 3,
                                 ['batch', 'batch'], {'batch': 1})
    assert result['actions'] == (1, 2)
    assert result['cost'] == 3
    assert result['feasible_subsets_evaluated'] == 4
    one = exact_budget_design(law, [0], [1, 2], [1], [1, 1], 2,
                              ['batch', 'batch'], {'batch': 1})
    assert one['actions'] == (2,)
    assert exact_budget_design(law, [0], [1, 2], [1], [1, 1], 0)['actions'] == ()


@pytest.mark.parametrize('covariance', [ [[1, 2], [2, 1]],
                                       [[1e-12, 2e-12], [2e-12, 1e-12]],
                                       [[1, .5], [.6, 1]], [[1, np.nan], [np.nan, 1]] ])
def test_invalid_covariance_rejected_at_its_scale(covariance):
    with pytest.raises(ValueError):
        JointGaussian([0, 0], covariance)


def test_copy_and_readonly_contract():
    mean = np.zeros(3)
    covariance = np.eye(3)
    law = JointGaussian(mean, covariance)
    mean[0] = 4
    covariance[0, 0] = 4
    assert law.mean[0] == 0 and law.covariance[0, 0] == 1
    with pytest.raises(ValueError):
        law.covariance[0, 0] = 2


def test_fail_closed_actions_and_noise():
    law = suppressor_law()
    for observed, values in [([1, 1], [0, 0]), ([True], [0]), ([4], [0]), ([1], [np.nan])]:
        with pytest.raises(ValueError):
            law.condition(observed, values)
    with pytest.raises(ValueError):
        law.condition([1], [0]).condition([1], [0])
    with pytest.raises(ValueError):
        law.variance_reduction([0], [0], [1])
    with pytest.raises(ValueError):
        law.variance_reduction([0], [1], [-1])
    with pytest.raises(ValueError):
        shared_control_noise([1], ['unknown'], {'other': 1})
    with pytest.raises(ValueError):
        exact_budget_design(law, [0], [1, 2], [1], [1, 1], 2, max_candidates=1)
