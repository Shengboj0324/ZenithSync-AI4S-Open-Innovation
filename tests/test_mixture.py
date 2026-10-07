import numpy as np
from scipy.special import ndtr
from zenithsync.models import GaussianProcess
from zenithsync.mixture import Component, FiniteGaussianMixture, default_mixture


def test_identical_components_reduce_to_single_gp():
    gp = GaussianProcess()
    mixture = FiniteGaussianMixture([Component(gp, 20), Component(gp, 20)], [1, 3])
    post = mixture.posterior([0, 1], [100, 80], [0, .5, 2])
    mean, cov = gp.posterior([0, 1], [100, 80], [400, 400], [0, .5, 2])
    np.testing.assert_allclose(post.weights, [.25, .75])
    actual_mean, actual_cov = post.moments()
    np.testing.assert_allclose(actual_mean, mean)
    np.testing.assert_allclose(actual_cov, cov)
    np.testing.assert_allclose(post.threshold_probability(50), ndtr((50-mean)/np.sqrt(np.diag(cov))))


def test_sequential_bayes_equals_batch_conditioning():
    mixture = default_mixture()
    query = np.array([0., 1., 2., 4.])
    prior = mixture.posterior([], [], query)
    sequential = prior.condition(1, 90).condition(3, 25)
    batch = mixture.posterior([1., 4.], [90, 25], query)
    np.testing.assert_allclose(sequential.weights, batch.weights, rtol=1e-8)
    np.testing.assert_allclose(sequential.means, batch.means, rtol=1e-8)
    np.testing.assert_allclose(sequential.covariances, batch.covariances, atol=1e-7)


def test_between_component_uncertainty_is_retained():
    mixture = FiniteGaussianMixture([Component(GaussianProcess(mean=0, amplitude=1), 1),
                                     Component(GaussianProcess(mean=10, amplitude=1), 1)])
    post = mixture.posterior([], [], [0])
    mean, cov = post.moments()
    np.testing.assert_allclose(mean, [5])
    np.testing.assert_allclose(cov, [[26]])
    low, high = post.interval(.9)[0]
    assert low < 0 and high > 10
    # Each bound is an actual mixture quantile, not a moment-matched Gaussian bound.
    np.testing.assert_allclose(post.weights @ ndtr((low-post.means[:, 0])), .05, atol=1e-10)


def test_observation_interval_accounts_for_noise():
    post = default_mixture().posterior([0], [100], [0])
    latent, observation = post.interval(), post.interval(observation=True)
    assert observation[0, 0] < latent[0, 0] < latent[0, 1] < observation[0, 1]


def test_mixture_acquisition_reduces_to_analytic_gp():
    from zenithsync.mixture import mixture_variance_reduction
    from zenithsync.acquisition import integrated_variance_reduction
    mixture = FiniteGaussianMixture([Component(GaussianProcess(), 20)])
    post = mixture.posterior([0], [100], [0, 1, 2])
    mean, covariance = post.moments()
    expected = integrated_variance_reduction(mean, covariance, [400]*3, [1, 2, 3])
    actual = mixture_variance_reduction(post, [1, 2, 3], nodes=32)
    np.testing.assert_allclose(actual, expected, rtol=1e-12)


def test_mixture_acquisition_includes_learning_model_identity():
    from zenithsync.mixture import mixture_variance_reduction
    # Component identity is almost revealed by a measurement. Most uncertainty
    # comes from separated means, not the tiny covariance within either model.
    mixture = FiniteGaussianMixture([Component(GaussianProcess(mean=0, amplitude=.01), .1),
                                     Component(GaussianProcess(mean=10, amplitude=.01), .1)])
    post = mixture.posterior([], [], [0])
    actual = mixture_variance_reduction(post, [1], nodes=32)[0]
    assert 24.99 < actual < 25.01


def test_mixture_acquisition_total_variance_identity_monte_carlo():
    from zenithsync.mixture import mixture_variance_reduction
    post = default_mixture().posterior([0, 1], [100, 70], [0, 1, 3])
    expected = mixture_variance_reduction(post, [1, 1, 1], nodes=256)[2]
    rng = np.random.default_rng(3781)
    labels = rng.choice(len(post.weights), size=5000, p=post.weights)
    total = post.covariances[:, 2, 2]+post.noise_variances
    observed = rng.normal(post.means[labels, 2], np.sqrt(total[labels]))
    _, prior_cov = post.moments()
    reductions = []
    for value in observed:
        _, conditional_cov = post.condition(2, value).moments()
        reductions.append(np.trace(prior_cov-conditional_cov)/3)
    reductions = np.array(reductions)
    assert abs(reductions.mean()-expected) < 5*reductions.std()/np.sqrt(len(reductions))


def test_mixture_replay_audit_outcome_isolation():
    from pathlib import Path
    import runpy
    run_curve = runpy.run_path(str(Path(__file__).parents[1]/"scripts/mixture_replay.py"))["run_curve"]
    x, y = np.arange(6.), np.array([100., 95., 80., 50., 20., 0.])
    first = run_curve(x, y, 2, "mixture_variance", 0)
    y[2] = 1e6
    second = run_curve(x, y, 2, "mixture_variance", 0)
    for a, b in zip(first, second, strict=True):
        assert a["selected_indices"] == b["selected_indices"]
        assert a["prediction"] == b["prediction"]
        assert 2 not in a["selected_indices"]
