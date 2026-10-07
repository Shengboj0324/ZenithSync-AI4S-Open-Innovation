"""Finite Bayesian averaging of GP smoothness and observation-noise hypotheses.

This retains parameter uncertainty rather than selecting a hyperparameter set
using held-out outcomes. A finite prior is a declared modeling assumption, not
a nonparametric guarantee or a substitute for independent biological validation.
"""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.special import logsumexp, ndtr, roots_hermitenorm
from scipy.optimize import brentq
from .models import GaussianProcess, vector


@dataclass(frozen=True)
class Component:
    gp: GaussianProcess
    noise_sd: float

    def __post_init__(self):
        if not np.isfinite(self.noise_sd) or self.noise_sd <= 0:
            raise ValueError("Component noise SD must be finite and positive")


@dataclass(frozen=True)
class MixturePosterior:
    weights: np.ndarray
    means: np.ndarray
    covariances: np.ndarray
    noise_variances: np.ndarray

    def __post_init__(self):
        arrays = {}
        for name in ("weights", "means", "covariances", "noise_variances"):
            arrays[name] = np.array(getattr(self, name), dtype=float, copy=True)
            if not np.all(np.isfinite(arrays[name])):
                raise ValueError(f"Nonfinite mixture {name}")
        w, m, c, noise = (arrays[name] for name in ("weights", "means", "covariances", "noise_variances"))
        if w.ndim != 1 or not len(w) or m.ndim != 2 or m.shape[0] != len(w):
            raise ValueError("Invalid mixture component dimensions")
        if c.shape != (len(w), m.shape[1], m.shape[1]) or noise.shape != w.shape:
            raise ValueError("Mixture covariance/noise dimensions do not align")
        if np.any(w < 0) or not np.isclose(w.sum(), 1) or np.any(noise <= 0):
            raise ValueError("Invalid mixture weights or observation variance")
        if not np.allclose(c, c.transpose(0, 2, 1)):
            raise ValueError("Mixture covariances must be symmetric")
        if m.shape[1] and np.linalg.eigvalsh(c).min() < -1e-7:
            raise ValueError("Mixture covariance must be positive semidefinite")
        for name, value in arrays.items():
            value.setflags(write=False)
            object.__setattr__(self, name, value)

    def moments(self):
        mean = self.weights @ self.means
        centered = self.means-mean
        covariance = np.einsum("k,kij->ij", self.weights, self.covariances)
        covariance += np.einsum("k,ki,kj->ij", self.weights, centered, centered)
        return mean, covariance

    def threshold_probability(self, threshold, observation=False):
        if not np.isfinite(threshold):
            raise ValueError("Threshold must be finite")
        variances = np.diagonal(self.covariances, axis1=1, axis2=2).copy()
        if observation:
            variances += self.noise_variances[:, None]
        # GP jitter and positive component noise prevent degeneracy in admitted fits.
        if np.any(variances <= 0):
            raise ArithmeticError("Nonpositive predictive variance")
        return self.weights @ ndtr((threshold-self.means)/np.sqrt(variances))

    def interval(self, coverage=.9, observation=False):
        if not 0 < coverage < 1:
            raise ValueError("Coverage must be between zero and one")
        variances = np.diagonal(self.covariances, axis1=1, axis2=2).copy()
        if observation:
            variances += self.noise_variances[:, None]
        if np.any(variances <= 0):
            raise ArithmeticError("Nonpositive predictive variance")
        sd = np.sqrt(variances)
        output = []
        for j in range(self.means.shape[1]):
            mu, scale = self.means[:, j], sd[:, j]
            low, high = float(np.min(mu-12*scale)), float(np.max(mu+12*scale))
            def quantile(q):
                return brentq(lambda t: self.weights @ ndtr((t-mu)/scale)-q, low, high)
            output.append([quantile((1-coverage)/2), quantile((1+coverage)/2)])
        return np.array(output).reshape(-1, 2)

    def condition(self, candidate, value):
        """Condition the entire finite mixture on one new noisy observation."""
        if not isinstance(candidate, (int, np.integer)) or not 0 <= candidate < self.means.shape[1]:
            raise ValueError("Candidate index outside posterior grid")
        if not np.isfinite(value):
            raise ValueError("Observed value must be finite")
        total = self.covariances[:, candidate, candidate]+self.noise_variances
        residual = value-self.means[:, candidate]
        log_likelihood = -.5*(np.log(2*np.pi*total)+residual**2/total)
        log_weights = np.log(self.weights, where=self.weights > 0,
                             out=np.full_like(self.weights, -np.inf))+log_likelihood
        weights = np.exp(log_weights-logsumexp(log_weights))
        cross = self.covariances[:, :, candidate]
        means = self.means+cross*(residual/total)[:, None]
        covariances = self.covariances-np.einsum("ki,kj,k->kij", cross, cross, 1/total)
        return MixturePosterior(weights, means, covariances, self.noise_variances.copy())


class FiniteGaussianMixture:
    def __init__(self, components, prior_weights=None):
        self.components = tuple(components)
        if not self.components:
            raise ValueError("At least one component required")
        weights = np.ones(len(self.components)) if prior_weights is None else vector(prior_weights, "prior weights")
        if len(weights) != len(self.components) or np.any(weights <= 0):
            raise ValueError("Each component needs a positive prior weight")
        self.prior_weights = weights/weights.sum()

    def posterior(self, x, y, query):
        x, y, query = vector(x, "x"), vector(y, "y"), vector(query, "query")
        if len(x) != len(y):
            raise ValueError("Training inputs and outputs must align")
        means, covariances, log_evidence = [], [], []
        for component in self.components:
            gp, noise = component.gp, component.noise_sd**2
            mean, covariance = gp.posterior(x, y, np.full(len(x), noise), query)
            means.append(mean)
            covariances.append(covariance)
            if len(x):
                factor, lower = cho_factor(gp.kernel(x, x)+np.eye(len(x))*(noise+gp.jitter), lower=True)
                residual = y-gp.mean
                quadratic = residual @ cho_solve((factor, lower), residual)
                logdet = 2*np.log(np.diag(factor)).sum()
                log_evidence.append(-.5*(quadratic+logdet+len(x)*np.log(2*np.pi)))
            else:
                log_evidence.append(0.)
        log_weight = np.log(self.prior_weights)+log_evidence
        weights = np.exp(log_weight-logsumexp(log_weight))
        return MixturePosterior(weights, np.array(means), np.array(covariances),
                                np.array([c.noise_sd**2 for c in self.components]))


def default_mixture():
    """Equal prior across nine declared length/noise combinations; no test tuning."""
    return FiniteGaussianMixture([Component(GaussianProcess(length_scale=length), noise)
                                  for length in (.75, 1.5, 3.) for noise in (10., 20., 40.)])


def mixture_variance_reduction(posterior, costs, target_weights=None, nodes=128):
    """Expected reduction of total mixture variance by the total-variance identity.

    E[Var(F|D)-Var(F|D,Y)] = Var(E[F|D,Y]|D). Both component response updates
    and posterior model weights change with the hypothetical observation.
    Moment-matching the mixture to a GP would omit the latter information.
    Gaussian quadrature integrates each predictive mixture component; callers
    must compare orders to assess numerical stability.
    """
    costs = vector(costs, "costs")
    k, n = posterior.means.shape
    if not n or len(costs) != n or np.any(costs <= 0):
        raise ValueError("Every candidate needs a positive cost")
    if not isinstance(nodes, int) or nodes < 2:
        raise ValueError("Quadrature order must be an integer >= 2")
    target_weights = np.full(n, 1/n) if target_weights is None else vector(target_weights, "target weights")
    if len(target_weights) != n or np.any(target_weights < 0) or not np.isclose(target_weights.sum(), 1):
        raise ValueError("Target weights must form a probability vector")
    z, quadrature_weights = roots_hermitenorm(nodes)
    quadrature_weights /= np.sqrt(2*np.pi)
    log_prior = np.log(posterior.weights, where=posterior.weights > 0,
                       out=np.full(k, -np.inf))
    old_mean, _ = posterior.moments()
    integration_weights = (posterior.weights[:, None]*quadrature_weights).ravel()
    scores = []
    for j in range(n):
        total = posterior.covariances[:, j, j]+posterior.noise_variances
        observations = (posterior.means[:, j, None]+np.sqrt(total[:, None])*z).ravel()
        residual = observations[:, None]-posterior.means[:, j]
        log_weight = log_prior-.5*(np.log(2*np.pi*total)+residual**2/total)
        weights = np.exp(log_weight-logsumexp(log_weight, axis=1, keepdims=True))
        conditional_means = posterior.means[None, :, :] + (
            residual/total)[:, :, None]*posterior.covariances[:, :, j][None, :, :]
        new_mean = np.einsum("rk,rki->ri", weights, conditional_means)
        # Explicit reductions avoid spurious macOS BLAS floating-point flags
        # observed for tall, narrow matmul despite bounded finite operands.
        target_gain = np.sum((new_mean-old_mean)**2*target_weights, axis=1)
        score = float(np.sum(integration_weights*target_gain)/costs[j])
        if not np.isfinite(score):
            raise ArithmeticError("Nonfinite mixture acquisition integral")
        scores.append(score)
    return np.array(scores)
