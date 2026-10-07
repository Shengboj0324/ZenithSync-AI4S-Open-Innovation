import numpy as np
import pytest
from zenithsync.models import GaussianProcess, hill, dose_coordinate
from zenithsync.acquisition import integrated_variance_reduction, decision_voi
from zenithsync.uncertainty import conformal_quantile, group_max_scores


def test_hill_limits_and_extreme_doses():
    values = hill([0, 10, 1e300], 100, 0, 10, 2)
    np.testing.assert_allclose(values, [100, 50, 0], atol=1e-10)
    with pytest.raises(ValueError):
        hill([-1], 100, 0, 10, 2)


def test_unit_invariant_coordinate():
    np.testing.assert_allclose(dose_coordinate([0, 1, 100], 1),
                               dose_coordinate([0, 1000, 100000], 1000))


def test_gp_scalar_conjugate_update():
    gp = GaussianProcess(amplitude=2, mean=0, jitter=1e-10)
    mean, cov = gp.posterior([0], [3], [1], [0])
    np.testing.assert_allclose(mean, [12/5], rtol=1e-8)
    np.testing.assert_allclose(cov, [[4/5]], rtol=1e-8)


def test_gp_repeated_locations_and_noise_separation():
    gp = GaussianProcess()
    _, prior = gp.posterior([], [], [], [0, 1, 2])
    _, posterior = gp.posterior([1, 1], [100, 100], [1, 1], [0, 1, 2])
    assert np.linalg.eigvalsh(posterior).min() >= -1e-8
    assert np.all(np.diag(posterior) <= np.diag(prior))


def test_information_does_not_prefer_pure_noise():
    cov = np.eye(2)
    score = integrated_variance_reduction([0, 0], cov, [1, 100], [1, 1])
    assert score[0] > score[1]
    np.testing.assert_allclose(score, [1/4, 1/202])


def test_variance_reduction_matches_direct_conditioning():
    gp = GaussianProcess(amplitude=2, jitter=1e-12)
    x = np.array([0, 1, 3])
    mean, covariance = gp.posterior([], [], [], x)
    scores = integrated_variance_reduction(mean, covariance, [2]*3, [1]*3)
    for j in range(3):
        _, updated = gp.posterior(x[j:j+1], [80], [2], x)
        np.testing.assert_allclose(scores[j], np.trace(covariance-updated)/3, rtol=1e-9)


def test_decision_voi_against_closed_form_gaussian_sign_error():
    # Scalar zero-threshold case: posterior sign error has closed form.
    # Expected error = arccos(corr(latent, observation))/pi.
    noise = 0.7
    exact = 0.5 - np.arccos(1/np.sqrt(1+noise))/np.pi
    result = decision_voi([0], [[1]], [noise], [1], threshold=0, nodes=256)[0]
    assert abs(result-exact) < 0.001
    assert result > 0


def test_conformal_small_sample_is_vacuous():
    assert np.isinf(conformal_quantile([1, 2, 3, 4]))
    assert conformal_quantile(range(1, 10)) == 9
    assert conformal_quantile(range(1, 20)) == 18


def test_calibration_counts_groups_not_rows():
    scores = group_max_scores([0, 2, 3, 1], [0]*4, [1]*4, ["a", "a", "b", "b"])
    np.testing.assert_equal(scores, [2, 3])
    assert np.isinf(conformal_quantile(scores))


@pytest.mark.parametrize("noise,cost", [([-1], [1]), ([1], [0]), ([np.nan], [1])])
def test_invalid_acquisition_inputs_fail(noise, cost):
    with pytest.raises(ValueError):
        integrated_variance_reduction([0], [[1]], noise, cost)


@pytest.mark.parametrize("policy", ["random", "space_filling", "integrated_variance", "decision_voi"])
def test_audit_outcome_cannot_change_acquisition(policy):
    from zenithsync.replay import replay_curve
    x, y = np.arange(6.), np.array([100, 90, 80, 60, 30, 10.])
    original = replay_curve(x, y, 2, policy)
    altered = y.copy()
    altered[2] = 1e6
    counterfactual = replay_curve(x, altered, 2, policy)
    for a, b in zip(original, counterfactual, strict=True):
        assert a["selected_indices"] == b["selected_indices"]
        assert a["prediction"] == b["prediction"]
        assert 2 not in a["selected_indices"]


def test_unrevealed_outcome_cannot_change_first_selection():
    from zenithsync.replay import replay_curve
    x, y = np.arange(6.), np.array([100, 90, 80, 60, 30, 10.])
    a = replay_curve(x, y, 2, "decision_voi")
    y[1:5] = 1e6
    b = replay_curve(x, y, 2, "decision_voi")
    assert a[1]["selected_indices"] == b[1]["selected_indices"]


def test_censoring_likelihood_stays_finite_in_both_tails():
    from zenithsync.likelihoods import gaussian_log_probability
    left = gaussian_log_probability(-41, -40)
    right = gaussian_log_probability(40, 41)
    assert np.isfinite(left) and np.isfinite(right)
    np.testing.assert_allclose(left, right)
    np.testing.assert_allclose(gaussian_log_probability(-np.inf, np.inf), 0)
    np.testing.assert_allclose(gaussian_log_probability(0, np.inf), np.log(.5))


def test_data_adapter_rejects_unreviewed_source(tmp_path):
    from zenithsync.data import load_albumin
    path = tmp_path / "wrong.xlsx"
    path.write_bytes(b"not reviewed")
    with pytest.raises(ValueError, match="Unrecognized"):
        load_albumin(path)
