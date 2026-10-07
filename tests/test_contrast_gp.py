import numpy as np
import pytest

from zenithsync.contrast_gp import ContrastGP


def test_pinned_kernel_and_positive_joint_covariance():
    model = ContrastGP(1., .3, .2, 2.)
    x = np.array([0., .1, .5, 1.])
    np.testing.assert_array_equal(model.kernel(x, x)[0], np.zeros(4))
    joint = model.joint(x[1:], x)
    assert np.linalg.eigvalsh(joint.covariance).min() > 0
    np.testing.assert_allclose(joint.covariance[3:, 3:] - model.kernel(x, x),
                               .04*(np.eye(4)+np.ones((4, 4))))


def test_second_control_reduces_normalization_uncertainty_only_after_treatment():
    model = ContrastGP(1., .3, .2, 0.)
    # target f(1), measured treatment contrast, second-control contrast
    joint = model.joint([1.], [1., 0.])
    assert joint.variance_reduction([0], [2], [1.]) == 0
    posterior = joint.condition([1], [-1.])
    assert posterior.variance_reduction([0], [2], [1.]) > 0
    diagonal = ContrastGP(1., .3, .2, 0., correlated=False).joint([1.], [1., 0.])
    assert diagonal.condition([1], [-1.]).variance_reduction([0], [2], [1.]) == 0


def test_contrast_likelihood_matches_direct_gaussian_density():
    from scipy.stats import multivariate_normal
    model = ContrastGP(1.2, .5, .3, 2.)
    x, y = np.array([0., .2, 1.]), np.array([.1, -.3, -2.1])
    covariance = model.kernel(x, x) + model.observation_noise(3)
    expected = -multivariate_normal.logpdf(y, mean=-2*x, cov=covariance)
    assert model.negative_log_likelihood(x, y) == pytest.approx(expected)


def test_raw_control_contrast_agrees_with_flat_baseline_limit():
    # A proper raw-log model with large baseline variance approaches the
    # contrast construction as that variance goes to infinity.
    from zenithsync.joint_design import JointGaussian
    model = ContrastGP(1., .3, .2, 1.)
    x = np.array([0., .4, 1., 0.])
    y = np.array([4.7, 4., 3.3, 4.8])
    cross = model.kernel([.4, 1.], x)
    raw = JointGaussian(np.r_[-np.array([.4, 1.]), -x], np.block([
        [model.kernel([.4, 1.], [.4, 1.]), cross],
        [cross.T, model.kernel(x, x)+1e5*np.ones((4, 4))+.04*np.eye(4)],
    ])).condition([2, 3, 4, 5], y)
    contrast = model.joint([.4, 1.], x[1:]).condition([2, 3, 4], y[1:]-y[0])
    np.testing.assert_allclose(raw.mean[:2], contrast.mean[:2], atol=3e-6)
    np.testing.assert_allclose(raw.covariance[:2, :2], contrast.covariance[:2, :2], atol=3e-7)
