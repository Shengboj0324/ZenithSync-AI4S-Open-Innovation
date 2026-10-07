"""Ridge point estimates with conditional Gaussian parameter uncertainty.

The intercept has a flat prior; slopes have precision penalty/noise_variance.
With at least one row and a positive slope penalty the posterior is proper.
Noise is fixed by the caller, not certified from sparse biological replicates.
"""
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from .models import vector
from .multidimensional import design


def ridge_posterior(x, y, query, penalty=.1, noise_sd=.1):
    x, query, y = design(x, "x"), design(query, "query"), vector(y, "y")
    if not len(x) or len(x) != len(y) or x.shape[1] != query.shape[1]:
        raise ValueError("Nonempty aligned training and query matrices required")
    if not np.isfinite([penalty, noise_sd]).all() or min(penalty, noise_sd) <= 0:
        raise ValueError("Ridge penalty and noise SD must be positive")
    a = np.column_stack([np.ones(len(x)), x])
    b = np.column_stack([np.ones(len(query)), query])
    gram = np.einsum("ni,nj->ij", a, a)+np.diag([0.]+[penalty]*x.shape[1])
    factor = cho_factor(gram, lower=True)
    coefficients = cho_solve(factor, np.einsum("ni,n->i", a, y))
    mean = np.einsum("ij,j->i", b, coefficients)
    covariance = noise_sd**2*np.einsum("ik,kj->ij", b, cho_solve(factor, b.T))
    covariance = (covariance+covariance.T)/2
    if not np.isfinite(mean).all() or not np.isfinite(covariance).all():
        raise ArithmeticError("Nonfinite ridge posterior")
    return mean, covariance
