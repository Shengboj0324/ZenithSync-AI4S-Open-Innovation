"""Exact equal-cost Gaussian design modulo verified permutation symmetries."""
from itertools import product
from math import comb, prod

import numpy as np

from .joint_design import _indices


def exact_exchangeable_designs(joint, targets, candidates, weights, exchangeable_groups,
                              *, max_representatives=1000000):
    """Enumerate one representative of each subset orbit, for every cardinality.

    Groups must be disjoint interchangeable observation coordinates under the
    entire joint law. Unit costs and unrestricted subsets are explicit premises.
    Symmetry is checked at floating-point covariance tolerance, not inferred
    from equal labels. The output sets can be non-nested.
    """
    n = len(joint.mean)
    targets = _indices(targets, n, 'targets')
    candidates = _indices(candidates, n, 'candidates')
    if set(targets) & set(candidates):
        raise ValueError('Targets and observation candidates must be distinct')
    groups, used = [], set()
    covariance_tolerance = 100*np.finfo(float).eps*n*max(np.max(np.abs(joint.covariance)), np.finfo(float).tiny)
    mean_tolerance = 100*np.finfo(float).eps*n*max(np.max(np.abs(joint.mean)), 1.)
    for values in exchangeable_groups:
        group = _indices(values, n, 'exchangeable group')
        if len(group) < 2 or not set(group).issubset(candidates) or used.intersection(group):
            raise ValueError('Groups must be disjoint candidate subsets of size at least two')
        # Transpositions with the first member generate every group permutation.
        for member in group[1:]:
            permutation = np.arange(n)
            permutation[group[0]], permutation[member] = member, group[0]
            if (not np.allclose(joint.mean, joint.mean[permutation], rtol=0, atol=mean_tolerance)
                    or not np.allclose(joint.covariance, joint.covariance[np.ix_(permutation, permutation)],
                                       rtol=0, atol=covariance_tolerance)):
                raise ValueError('Declared exchangeability is not a symmetry of the joint law')
        groups.append(group)
        used.update(group)
    groups.extend((candidate,) for candidate in candidates if candidate not in used)
    count = prod(len(group)+1 for group in groups)
    if (isinstance(max_representatives, bool) or not isinstance(max_representatives, int)
            or max_representatives < 1 or count > max_representatives):
        raise ValueError('Explicit representative enumeration bound exceeded')
    joint.variance_reduction(targets, (), weights)  # Validate even the empty design.
    best = [None]*(len(candidates)+1)
    represented = 0
    ordering = {candidate: index for index, candidate in enumerate(candidates)}
    for counts in product(*(range(len(group)+1) for group in groups)):
        actions = tuple(sorted((member for group, k in zip(groups, counts, strict=True)
                                for member in group[:k]), key=ordering.__getitem__))
        gain = joint.variance_reduction(targets, actions, weights)
        represented += prod(comb(len(group), k) for group, k in zip(groups, counts, strict=True))
        previous = best[len(actions)]
        if previous is None or gain > previous['variance_reduction']:
            best[len(actions)] = {'actions': actions, 'variance_reduction': gain}
    if represented != 2**len(candidates) or any(item is None for item in best):
        raise AssertionError('Subset or cardinality coverage failed')
    return {'designs': best, 'representatives_evaluated': count,
            'subsets_represented': represented,
            'assurance': 'exact fixed-Gaussian, unit-cost, unrestricted-subset design up to numerical symmetry tolerance'}
