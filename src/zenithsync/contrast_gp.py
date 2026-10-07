"""Gaussian dose contrasts with an explicitly shared measured denominator.

This is a standard pinned GP and Gaussian conditioning model, not a novelty
claim. Independent homoscedastic raw log errors are a modeling assumption.
"""
from dataclasses import dataclass

import numpy as np
from scipy.linalg import cho_factor, cho_solve

from .joint_design import JointGaussian


@dataclass(frozen=True)
class ContrastGP:
    amplitude: float
    length: float
    noise_sd: float
    slope: float
    correlated: bool = True

    def __post_init__(self):
        if (not np.isfinite([self.amplitude, self.length, self.noise_sd, self.slope]).all()
                or min(self.amplitude, self.length, self.noise_sd) <= 0
                or self.slope < 0 or not isinstance(self.correlated, bool)):
            raise ValueError('Finite positive scales, nonnegative slope and boolean correlation required')

    def kernel(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        if (x.ndim != 1 or y.ndim != 1 or not np.isfinite(x).all()
                or not np.isfinite(y).all() or np.any(x < 0) or np.any(y < 0)):
            raise ValueError('Finite nonnegative coordinate vectors required')
        def base(a, b):
            d = np.sqrt(5.) * np.abs(a[:, None] - b[None, :]) / self.length
            return (1 + d + d*d/3) * np.exp(-d)
        # Covariance of a stationary GP conditional on its value at zero.
        return self.amplitude**2 * (base(x, y) - base(x, np.zeros(1)) * base(np.zeros(1), y))

    def observation_noise(self, n):
        if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 1:
            raise ValueError('Positive observation dimension required')
        return self.noise_sd**2 * (np.eye(n) + np.ones((n, n)) if self.correlated else 2*np.eye(n))

    def joint(self, targets, observations):
        targets, observations = np.asarray(targets, float), np.asarray(observations, float)
        tt = self.kernel(targets, targets)
        to = self.kernel(targets, observations)
        oo = self.kernel(observations, observations) + self.observation_noise(len(observations))
        return JointGaussian(-self.slope*np.concatenate([targets, observations]),
                             np.block([[tt, to], [to.T, oo]]))

    def negative_log_likelihood(self, coordinates, contrasts):
        coordinates, contrasts = np.asarray(coordinates, float), np.asarray(contrasts, float)
        covariance = self.kernel(coordinates, coordinates) + self.observation_noise(len(coordinates))
        if contrasts.shape != coordinates.shape or not np.isfinite(contrasts).all():
            raise ValueError('Finite contrasts must align with coordinates')
        factor = cho_factor(covariance, lower=True)
        centered = contrasts + self.slope*coordinates
        return float(.5 * (np.einsum('i,i->', centered, cho_solve(factor, centered))
                           + 2*np.log(np.diag(factor[0])).sum()
                           + len(centered)*np.log(2*np.pi)))


def contrast_design(design):
    """Return coordinates using doses only and locate the reference-control row."""
    dose = design.concentration.to_numpy(dtype=float)
    if (not np.isfinite(dose).all() or np.any(dose < 0)
            or not np.any(dose > 0) or not np.any(dose == 0)):
        raise ValueError('Design requires finite nonnegative doses and a control')
    reference = np.flatnonzero((dose == 0) & design.replicate_label.eq('1').to_numpy())
    if len(reference) != 1:
        raise ValueError('Exactly one label-1 reference control required')
    scale = np.min(dose[dose > 0])
    x = np.log1p(dose/scale)
    x /= x.max()
    targets = np.unique(x[x > 0])
    return targets, x, int(reference[0])
