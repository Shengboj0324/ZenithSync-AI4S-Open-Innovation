import numpy as np
import pytest
from zenithsync.acquisition import decision_voi_adaptive


@pytest.mark.parametrize("noise", [1e-6, .01, .7, 1, 100, 1e6])
def test_adaptive_voi_closed_form_over_noise_range(noise):
    exact = .5-np.arccos(1/np.sqrt(1+noise))/np.pi
    scores, errors = decision_voi_adaptive([0], [[1]], [noise], [1], threshold=0)
    assert abs(scores[0]-exact) < max(1e-10, errors[0]*5)


def test_cost_scaling_and_target_weights():
    mean, covariance = [0, 0], np.diag([1., 1.])
    scores, _ = decision_voi_adaptive(mean, covariance, [1, 1], [1, 2], threshold=0, weights=[1, 0])
    np.testing.assert_allclose(scores, [.25, 0], atol=1e-10)
    scores, _ = decision_voi_adaptive(mean, covariance, [1, 1], [1, 2], threshold=0)
    np.testing.assert_allclose(scores, [.125, .0625], atol=1e-10)


def test_negative_correlation_is_informative():
    a, _ = decision_voi_adaptive([0, 0], [[1, .9], [.9, 1]], [1, 1], [1, 1], threshold=0)
    b, _ = decision_voi_adaptive([0, 0], [[1, -.9], [-.9, 1]], [1, 1], [1, 1], threshold=0)
    np.testing.assert_allclose(a, b, atol=1e-10)


def test_asymmetric_loss_against_large_independent_simulation():
    rng = np.random.default_rng(882)
    z = rng.standard_normal(500_000)
    from scipy.special import ndtr
    p = ndtr((.3-z/np.sqrt(2))/np.sqrt(.5))
    initial = min(4*ndtr(.3), 1-ndtr(.3))
    exact_numeric, _ = decision_voi_adaptive([0], [[1]], [1], [1], threshold=.3,
                                            false_positive=1, false_negative=4)
    mc_risk = np.minimum(4*p, 1-p)
    assert abs(exact_numeric[0]-(initial-mc_risk.mean())) < 5*mc_risk.std()/np.sqrt(len(z))
