import numpy as np
import pytest

from zenithsync.contrast_gp import ContrastGP
from zenithsync.joint_design import JointGaussian, exact_cardinality_designs
from zenithsync.symmetric_design import exact_exchangeable_designs


def test_orbit_design_equals_exhaustive_at_every_cardinality():
    model = ContrastGP(1., .5, .3, 2.)
    law = model.joint([.2, .5, 1.], [.2, .5, 1., 0., 0., 0., 0.])
    law = law.condition([3, 5], [-.4, -1.5])
    candidates = [4, 6, 7, 8, 9]
    reduced = exact_exchangeable_designs(law, [0, 1, 2], candidates, [1/3]*3, [[6, 7, 8, 9]])
    full = exact_cardinality_designs(law, [0, 1, 2], candidates, [1/3]*3)
    assert reduced['representatives_evaluated'] == 10
    assert reduced['subsets_represented'] == 32
    for count, (a, b) in enumerate(zip(reduced['designs'], full, strict=True)):
        assert len(a['actions']) == count
        assert a['variance_reduction'] == pytest.approx(b['variance_reduction'], abs=1e-12)


def test_false_symmetry_and_overlapping_groups_rejected():
    law = JointGaussian([0, 0, 0], [[1, .2, .3], [.2, 1, 0], [.3, 0, 1]])
    with pytest.raises(ValueError, match='symmetry'):
        exact_exchangeable_designs(law, [0], [1, 2], [1], [[1, 2]])
    symmetric = JointGaussian(np.zeros(4), np.eye(4))
    with pytest.raises(ValueError, match='disjoint'):
        exact_exchangeable_designs(symmetric, [0], [1, 2, 3], [1], [[1, 2], [2, 3]])
    with pytest.raises(ValueError, match='bound'):
        exact_exchangeable_designs(symmetric, [0], [1, 2, 3], [1], [], max_representatives=7)


def test_multiple_symmetry_groups_cover_all_subsets():
    law = JointGaussian(np.zeros(6), np.eye(6))
    result = exact_exchangeable_designs(law, [0], [1, 2, 3, 4, 5], [1], [[1, 2], [3, 4, 5]])
    assert result['representatives_evaluated'] == 12
    assert result['subsets_represented'] == 32
