"""Exact GP for declared dimensionless experimental coordinates."""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from .models import vector


def design(value, name):
    result = np.asarray(value, dtype=float)
    if result.ndim != 2 or result.shape[1] == 0 or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a finite (observations, features) matrix")
    return result


@dataclass(frozen=True)
class DesignGP:
    amplitude: float = .3
    length_scale: float = .3
    mean: float = 1.
    noise_sd: float = .1
    jitter: float = 1e-10

    def __post_init__(self):
        if not np.isfinite([self.amplitude, self.length_scale, self.mean, self.noise_sd, self.jitter]).all():
            raise ValueError("Nonfinite GP parameter")
        if min(self.amplitude, self.length_scale, self.noise_sd, self.jitter) <= 0:
            raise ValueError("Positive GP scales required")

    def kernel(self, a, b):
        a, b = design(a, "a"), design(b, "b")
        if a.shape[1] != b.shape[1]:
            raise ValueError("Feature dimensions differ")
        distance = np.sqrt(np.sum(((a[:, None, :]-b[None, :, :])/self.length_scale)**2, axis=2))
        scaled = np.sqrt(5)*distance
        return self.amplitude**2*(1+scaled+scaled**2/3)*np.exp(-scaled)

    def posterior(self, x, y, query):
        x, query, y = design(x, "x"), design(query, "query"), vector(y, "y")
        if len(x) != len(y) or x.shape[1] != query.shape[1]:
            raise ValueError("Training/query dimensions do not align")
        mean = np.full(len(query), self.mean)
        covariance = self.kernel(query, query)
        if len(x):
            factor = cho_factor(self.kernel(x, x)+np.eye(len(x))*(self.noise_sd**2+self.jitter), lower=True)
            cross = self.kernel(query, x)
            # Explicit contractions avoid macOS BLAS status-flag warnings seen
            # on these small matrices; finite outputs are checked separately.
            mean += np.einsum("ij,j->i", cross, cho_solve(factor, y-self.mean))
            covariance -= np.einsum("ik,kj->ij", cross, cho_solve(factor, cross.T))
        covariance = (covariance+covariance.T)/2
        if not np.isfinite(mean).all() or not np.isfinite(covariance).all():
            raise ArithmeticError("Nonfinite Gaussian prediction")
        if len(query) and np.linalg.eigvalsh(covariance).min() < -1e-8:
            raise ArithmeticError("Indefinite posterior covariance")
        return mean, covariance
