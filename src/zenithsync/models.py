"""Exact Gaussian conditioning and a numerically stable Hill baseline.

Variances are in squared response units. Hyperparameters are explicit and fixed
during acquisition; posterior uncertainty is conditional on these parameters.
"""
from dataclasses import dataclass
import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import least_squares
from scipy.special import expit


def vector(value: ArrayLike, name: str) -> NDArray[np.float64]:
    result = np.asarray(value, dtype=float)
    if result.ndim != 1 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite one-dimensional array")
    return result


def dose_coordinate(dose: ArrayLike, reference: float = 1.0):
    dose = vector(dose, "dose")
    if np.any(dose < 0) or not np.isfinite(reference) or reference <= 0:
        raise ValueError("Dose must be nonnegative and reference positive")
    return np.log1p(dose / reference)


def hill(dose: ArrayLike, baseline: float, asymptote: float, ec50: float, slope: float):
    dose = vector(dose, "dose")
    if np.any(dose < 0) or not np.all(np.isfinite([baseline, asymptote, ec50, slope])):
        raise ValueError("Invalid Hill parameters or doses")
    if ec50 <= 0 or slope <= 0:
        raise ValueError("EC50 and slope must be positive")
    fraction = np.zeros_like(dose)
    positive = dose > 0
    fraction[positive] = expit(slope * (np.log(dose[positive]) - np.log(ec50)))
    return baseline + (asymptote - baseline) * fraction


def fit_hill(dose: ArrayLike, response: ArrayLike):
    """Exploratory decreasing curve; fitted EC50 is not evidence of identification."""
    dose, response = vector(dose, "dose"), vector(response, "response")
    if len(dose) != len(response) or len(np.unique(dose)) < 4 or np.any(dose < 0):
        raise ValueError("Hill fitting needs at least four distinct nonnegative doses")
    positive = dose[dose > 0]
    if len(positive) == 0:
        raise ValueError("Positive doses required")
    # Parameterization: asymptote >= 0, baseline = asymptote + positive amplitude.
    def predict(parameters, d):
        bottom, amplitude, log_ec50, log_slope = parameters
        return hill(d, bottom + amplitude, bottom, np.exp(log_ec50), np.exp(log_slope))
    bounds = ([0, 0, np.log(positive.min()) - 7, -3],
              [500, 500, np.log(positive.max()) + 7, 3])
    starts = [np.quantile(positive, q) for q in (0.25, 0.5, 0.75)]
    fits = [least_squares(lambda p: predict(p, dose) - response,
                         [max(0, response.min()), max(1, np.ptp(response)), np.log(e), 0],
                         bounds=bounds, max_nfev=3000) for e in starts]
    valid = [fit for fit in fits if fit.success and np.all(np.isfinite(fit.x))]
    if not valid:
        raise RuntimeError("Hill optimization failed")
    best = min(valid, key=lambda fit: np.sum(fit.fun ** 2))
    return lambda d: predict(best.x, d), {
        "parameters": best.x.tolist(), "jacobian_rank": int(np.linalg.matrix_rank(best.jac)),
        "bound_active": bool(np.any(best.active_mask)), "identified_ec50": False,
    }


@dataclass(frozen=True)
class GaussianProcess:
    amplitude: float = 50.0
    length_scale: float = 1.5
    mean: float = 100.0
    jitter: float = 1e-8

    def __post_init__(self):
        if not np.all(np.isfinite([self.amplitude, self.length_scale, self.mean, self.jitter])):
            raise ValueError("GP parameters must be finite")
        if min(self.amplitude, self.length_scale, self.jitter) <= 0:
            raise ValueError("GP amplitude, length scale and jitter must be positive")

    def kernel(self, a, b):
        a, b = vector(a, "a"), vector(b, "b")
        distance = np.abs(a[:, None] - b[None, :]) / self.length_scale
        scaled = np.sqrt(5.0) * distance
        return self.amplitude ** 2 * (1 + scaled + scaled ** 2 / 3) * np.exp(-scaled)

    def posterior(self, x, y, noise_variance, query):
        x, y, query = vector(x, "x"), vector(y, "y"), vector(query, "query")
        noise = vector(noise_variance, "noise variance")
        if len(x) != len(y) or len(x) != len(noise) or np.any(noise < 0):
            raise ValueError("Training arrays must align; noise variance cannot be negative")
        covariance = self.kernel(query, query)
        mean = np.full(len(query), self.mean, dtype=float)
        if len(x):
            cross = self.kernel(query, x)
            factor = cho_factor(self.kernel(x, x) + np.diag(noise + self.jitter), lower=True)
            mean += cross @ cho_solve(factor, y - self.mean)
            covariance -= cross @ cho_solve(factor, cross.T)
        covariance = (covariance + covariance.T) / 2
        if len(query) and np.linalg.eigvalsh(covariance).min() < -1e-7 * self.amplitude ** 2:
            raise ArithmeticError("Posterior covariance is materially indefinite")
        return mean, covariance
