from pathlib import Path
import runpy
import numpy as np
import pytest
from zenithsync.models import GaussianProcess
from zenithsync.multidimensional import DesignGP


def test_multidimensional_gp_matches_scalar_kernel_and_posterior():
    x, q, y = np.array([0., .4, 1.]), np.array([.2, .8]), np.array([1., .8, .2])
    multi = DesignGP(amplitude=.5, length_scale=.3, mean=1., noise_sd=.1, jitter=1e-8)
    scalar = GaussianProcess(amplitude=.5, length_scale=.3, mean=1., jitter=1e-8)
    a, b = multi.posterior(x[:, None], y, q[:, None])
    c, d = scalar.posterior(x, y, np.full(3, .01), q)
    np.testing.assert_allclose(a, c)
    np.testing.assert_allclose(b, d)


def test_feature_axis_permutation_does_not_change_isotropic_gp():
    x = np.array([[0., .5], [.3, .4], [1., 0.]])
    q = np.array([[.2, .6], [.9, .1]])
    model = DesignGP()
    a, b = model.posterior(x, [1., .8, .3], q)
    c, d = model.posterior(x[:, ::-1], [1., .8, .3], q[:, ::-1])
    np.testing.assert_allclose(a, c)
    np.testing.assert_allclose(b, d)
    assert np.linalg.eigvalsh(b).min() >= 0


def test_generation_tuning_uses_only_earlier_generations():
    from unittest.mock import patch
    fit_select = runpy.run_path(str(Path(__file__).parents[1]/"scripts/generation_benchmark.py"))["fit_select"]
    generation = np.repeat([0, 1, 2], 3)
    x = np.column_stack([generation, np.tile([.1, .2, .3], 3)])
    calls = []
    def posterior(self, train_x, train_y, query):
        assert train_x[:, 0].max() < query[:, 0].min()
        calls.append(len(query))
        return np.full(len(query), train_y.mean()), np.eye(len(query))
    with patch.object(DesignGP, "posterior", posterior):
        _, selection = fit_select(x, np.linspace(.1, 1., 9), generation)
    assert len(calls) == 54
    assert len(selection["scores"]) == 27


def test_single_generation_uses_declared_default():
    fit_select = runpy.run_path(str(Path(__file__).parents[1]/"scripts/generation_benchmark.py"))["fit_select"]
    gp, selection = fit_select(np.array([[0., 0.], [1., 1.]]), np.array([1., .5]), np.array([0, 0]))
    assert gp == DesignGP()
    assert selection["scores"] == []


def test_mismatched_feature_schema_rejected():
    with pytest.raises(ValueError):
        DesignGP().posterior([[0., 1.]], [1.], [[.5]])
