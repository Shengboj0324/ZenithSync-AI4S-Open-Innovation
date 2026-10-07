import numpy as np
import pytest
from zenithsync.models import GaussianProcess
from zenithsync.tuning import tune_gp, interpolate_curve


def test_tuning_removes_all_replicates_of_held_dose():
    seen = []
    class RecordingGP:
        def posterior(self, x, y, noise, query):
            assert not set(x) & set(query)
            seen.append((len(x), len(query)))
            return np.full(len(query), np.mean(y)), np.eye(len(query))
    # Use actual dataclass instance so diagnostics retain parameter metadata.
    from unittest.mock import patch
    with patch.object(GaussianProcess, "posterior", RecordingGP.posterior):
        _, _, report = tune_gp([0, 0, 1, 1, 2, 2], [1, 2, 3, 4, 5, 6], [(GaussianProcess(), 20)])
    assert seen == [(4, 2)]*3
    assert report["inner_group_count"] == 3


def test_tuning_is_permutation_invariant():
    x, y = np.array([0., 0., 1., 2., 3.]), np.array([100., 105., 80., 70., 30.])
    a, noise_a, _ = tune_gp(x, y)
    p = np.array([3, 0, 4, 2, 1])
    b, noise_b, _ = tune_gp(x[p], y[p])
    assert a == b and noise_a == noise_b


@pytest.mark.parametrize("method", ["linear", "pchip"])
def test_interpolation_means_and_constant_extension(method):
    result = interpolate_curve([0, 0, 1, 2], [90, 110, 70, 30], [-1, 0, 1, 2, 3], method)
    np.testing.assert_allclose(result, [100, 100, 70, 30, 30])
