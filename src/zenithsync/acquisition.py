"""One-step acquisition on an explicitly supplied Gaussian posterior."""
import numpy as np
from scipy.special import ndtr, roots_hermitenorm
from scipy.special import ndtri
from scipy.integrate import quad
from .models import vector


def validate_posterior(mean, covariance, noise, cost):
    mean, noise, cost = (vector(v, n) for v, n in
                         [(mean, "mean"), (noise, "noise"), (cost, "cost")])
    covariance = np.asarray(covariance, dtype=float)
    n = len(mean)
    if covariance.shape != (n, n) or len(noise) != n or len(cost) != n:
        raise ValueError("Posterior dimensions do not align")
    if not np.all(np.isfinite(covariance)) or not np.allclose(covariance, covariance.T):
        raise ValueError("Covariance must be finite and symmetric")
    if n and np.linalg.eigvalsh(covariance).min() < -1e-8:
        raise ValueError("Covariance must be positive semidefinite")
    if np.any(noise <= 0) or np.any(cost <= 0):
        raise ValueError("Candidate observation noise and cost must be positive")
    return mean, covariance, noise, cost


def integrated_variance_reduction(mean, covariance, noise, cost, weights=None):
    """Expected latent squared-error reduction per cost, over a fixed query grid."""
    mean, covariance, noise, cost = validate_posterior(mean, covariance, noise, cost)
    n = len(mean)
    if n == 0:
        raise ValueError("At least one candidate required")
    weights = np.full(n, 1/n) if weights is None else vector(weights, "weights")
    if len(weights) != n or np.any(weights < 0) or not np.isclose(weights.sum(), 1):
        raise ValueError("Query weights must form a probability vector")
    return (weights @ covariance ** 2) / (np.diag(covariance) + noise) / cost


def threshold_probability(mean, variance, threshold):
    """Probability latent response is below threshold (e.g., reduced albumin)."""
    mean, variance = np.asarray(mean, dtype=float), np.asarray(variance, dtype=float)
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(variance)) or not np.isfinite(threshold):
        raise ValueError("Threshold inputs must be finite")
    if np.any(variance < 0):
        raise ValueError("Predictive variance cannot be negative")
    result = np.zeros(np.broadcast_shapes(mean.shape, variance.shape))
    np.divide(threshold - mean, np.sqrt(variance), out=result, where=variance > 0)
    return np.where(variance > 0, ndtr(result), (mean < threshold).astype(float))


def decision_voi(mean, covariance, noise, cost, threshold=50.0,
                 false_positive=1.0, false_negative=1.0, nodes=96):
    """Gauss-Hermite approximation of expected reduction in grid-average Bayes risk.

    Fixed hyperparameters and Gaussian observation model are required. Compare
    quadrature orders before acting; small negative estimates are returned, not
    silently clipped. This is model-based value, not empirical assay benefit.
    """
    mean, covariance, noise, cost = validate_posterior(mean, covariance, noise, cost)
    if not len(mean) or nodes < 2 or not np.all(np.isfinite([threshold, false_positive, false_negative])):
        raise ValueError("Invalid decision specification")
    if min(false_positive, false_negative) <= 0:
        raise ValueError("Decision costs must be positive")
    def risk(mu, var):
        p = threshold_probability(mu, var, threshold)
        return np.minimum(false_negative * p, false_positive * (1-p))
    diagonal = np.maximum(np.diag(covariance), 0)
    current = risk(mean, diagonal).mean()
    z, weights = roots_hermitenorm(nodes)
    weights = weights / np.sqrt(2*np.pi)
    values = []
    for j in range(len(mean)):
        total = diagonal[j] + noise[j]
        conditional_mean = mean[None, :] + z[:, None] * covariance[:, j] / np.sqrt(total)
        conditional_variance = np.maximum(diagonal - covariance[:, j] ** 2 / total, 0)
        expected = weights @ risk(conditional_mean, conditional_variance).mean(axis=1)
        values.append((current - expected) / cost[j])
    return np.array(values)


def decision_voi_adaptive(mean, covariance, noise, cost, threshold=50.0,
                          false_positive=1.0, false_negative=1.0, weights=None,
                          absolute_tolerance=1e-9):
    """One-step Gaussian decision VOI with integration split at each action switch.

    Each target's conditional class probability is Phi((a-b*z)/s), z~N(0,1).
    Its optimal action changes at z=(a-s*Phi^-1(p*))/b. Supplying this point to
    adaptive quadrature avoids the nonsmooth kink missed by fixed Hermite nodes.
    Integration uses [-10,10]; the omitted risk is bounded by
    2*Phi(-10)*max(false_positive,false_negative). Returned error estimates add
    that tail bound to QUADPACK's estimated integration error, not a formal
    floating-point certificate. Negative VOI beyond this estimate raises.

    Targets and candidates share a supplied latent grid. Weights specify the
    scientific target distribution and need not be uniform. Candidate noise is
    observation variance; target risk concerns the latent endpoint threshold.
    """
    mean, covariance, noise, cost = validate_posterior(mean, covariance, noise, cost)
    n = len(mean)
    if n == 0 or not np.all(np.isfinite([threshold, false_positive, false_negative, absolute_tolerance])):
        raise ValueError("Invalid decision specification")
    if min(false_positive, false_negative, absolute_tolerance) <= 0:
        raise ValueError("Costs and tolerance must be positive")
    weights = np.full(n, 1/n) if weights is None else vector(weights, "weights")
    if len(weights) != n or np.any(weights < 0) or not np.isclose(weights.sum(), 1):
        raise ValueError("Target weights must form a probability vector")
    variance = np.maximum(np.diag(covariance), 0)
    p = threshold_probability(mean, variance, threshold)
    initial_risk = np.minimum(false_negative*p, false_positive*(1-p))
    switch_probability = false_positive/(false_positive+false_negative)
    switch_quantile = ndtri(switch_probability)
    tail_bound = 2*ndtr(-10)*max(false_positive, false_negative)
    scores, errors = np.zeros(n), np.zeros(n)
    for j in range(n):
        total_variance = variance[j]+noise[j]
        for i in np.flatnonzero(weights):
            b = covariance[i, j]/np.sqrt(total_variance)
            if b == 0 or variance[i] == 0:
                continue
            conditional_variance = max(0., variance[i]-b*b)
            if conditional_variance == 0:
                # Perfect revelation of this latent threshold makes its risk zero.
                scores[j] += weights[i]*initial_risk[i]/cost[j]
                continue
            s = np.sqrt(conditional_variance)
            a = threshold-mean[i]
            switch = (a-s*switch_quantile)/b

            def integrand(z):
                standardized = (a-b*z)/s
                risk = min(false_negative*ndtr(standardized),
                           false_positive*ndtr(-standardized))
                return risk*np.exp(-z*z/2)/np.sqrt(2*np.pi)

            # In nearly noiseless cases the risk occupies a very narrow region.
            # A switch alone can let adaptive quadrature miss the entire peak.
            # Bracket the conditional-probability transition on its own scale.
            width = s/abs(b)
            center = a/b
            breakpoints = [switch, *[center+k*width for k in (-8, -4, -1, 0, 1, 4, 8)]]
            points = sorted({float(point) for point in breakpoints if -10 < point < 10}) or None
            expected, error = quad(integrand, -10, 10, points=points,
                                   epsabs=absolute_tolerance, epsrel=1e-10, limit=200)
            scores[j] += weights[i]*(initial_risk[i]-expected)/cost[j]
            errors[j] += weights[i]*(error+tail_bound)/cost[j]
        if scores[j] < -errors[j]-1e-12:
            raise ArithmeticError("Negative VOI exceeds quadrature error estimate")
    return scores, errors
