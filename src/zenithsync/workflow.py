"""Strict research request -> prediction, abstention and candidate ranking."""
from hashlib import sha256
import json
import numpy as np
from scipy.optimize import linprog
from scipy.special import ndtr, ndtri
from .linear import ridge_posterior
from .acquisition import integrated_variance_reduction

SCHEMAS = {"yakavets_fac_concurrent": ["conc0", "conc1", "conc2"],
           "yakavets_ola_ibet_concurrent": ["conc0", "conc1"]}


def require_keys(item, expected, label):
    if not isinstance(item, dict) or set(item) != set(expected):
        raise ValueError(f"{label} requires exactly {sorted(expected)}")


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def in_convex_support(training, query):
    """Convex combinations of observed input coordinates; not biological support."""
    a = np.vstack([training.T, np.ones(len(training))])
    result = linprog(np.zeros(len(training)), A_eq=a, b_eq=np.r_[query, 1.],
                     bounds=(0., None), method="highs")
    if result.status == 2:
        return False
    if not result.success:
        raise ArithmeticError(f"Support solver failed with status {result.status}")
    return bool(np.max(abs(a @ result.x-np.r_[query, 1.])) <= 1e-7)


def run_request(request):
    require_keys(request, ["context", "feature_names", "feature_unit", "endpoint", "observations",
                           "candidates", "threshold", "false_positive_cost", "false_negative_cost",
                           "abstention_cost", "noise_sd", "ridge_penalty"], "request")
    context = request["context"]
    if not isinstance(context, str) or context not in SCHEMAS:
        raise ValueError("Unsupported assay context")
    features = SCHEMAS[context]
    if request["feature_names"] != features or request["feature_unit"] != "author_normalized_concentration":
        raise ValueError("Feature names/order or units do not match admitted context")
    if request["endpoint"] != "cv_exp":
        raise ValueError("Unsupported endpoint")
    noise = positive(request["noise_sd"], "noise_sd")
    penalty = positive(request["ridge_penalty"], "ridge_penalty")
    cfp = positive(request["false_positive_cost"], "false_positive_cost")
    cfn = positive(request["false_negative_cost"], "false_negative_cost")
    abstention = positive(request["abstention_cost"], "abstention_cost")
    threshold = request["threshold"]
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not np.isfinite(threshold):
        raise ValueError("Threshold must be finite")
    observations, candidates = request["observations"], request["candidates"]
    if not isinstance(observations, list) or not observations or not isinstance(candidates, list) or not candidates:
        raise ValueError("Nonempty observation and candidate lists required")
    all_ids, x, y, q, costs = set(), [], [], [], []
    for rows, kind in [(observations, "observation"), (candidates, "candidate")]:
        for row in rows:
            require_keys(row, ["id", "x", "y"] if kind == "observation" else ["id", "x", "cost"], kind)
            if not isinstance(row["id"], str) or not row["id"] or row["id"] in all_ids:
                raise ValueError("Distinct nonempty observation/candidate IDs required")
            all_ids.add(row["id"])
            if not isinstance(row["x"], list) or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in row["x"]):
                raise ValueError("Coordinates must be a list of numeric values")
            coordinate = np.asarray(row["x"], dtype=float)
            if coordinate.shape != (len(features),) or not np.isfinite(coordinate).all() or np.any((coordinate < 0)|(coordinate > 1)):
                raise ValueError("Coordinates must match schema and be in [0,1]")
            if kind == "observation":
                value = row["y"]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value < 0:
                    raise ValueError("Observed response must be finite and nonnegative")
                x.append(coordinate); y.append(value)
            else:
                q.append(coordinate); costs.append(positive(row["cost"], "candidate cost"))
    x, q = np.array(x), np.array(q)
    mean, covariance = ridge_posterior(x, y, q, penalty, noise)
    support = np.array([in_convex_support(x, point) for point in q])
    scores = np.zeros(len(q))
    if support.any():
        weights = support.astype(float)/support.sum()
        scores = integrated_variance_reduction(mean, covariance, np.full(len(q), noise**2), costs, weights)
    records = []
    for i, candidate in enumerate(candidates):
        if not support[i]:
            records.append({"id": candidate["id"], "status": "abstain", "reason": "outside_observed_convex_support",
                            "prediction": None, "acquisition_score": None})
            continue
        latent_sd = np.sqrt(max(0., covariance[i, i]))
        observation_sd = np.sqrt(covariance[i, i]+noise**2)
        probability = float(ndtr((threshold-mean[i])/latent_sd)) if latent_sd > 0 else float(mean[i] < threshold)
        losses = {"provisional_below_threshold": cfp*(1-probability),
                  "provisional_not_below_threshold": cfn*probability}
        decision = min(losses, key=losses.get)
        if abstention <= losses[decision]:
            decision = "abstain"
        records.append({"id": candidate["id"], "status": decision,
                        "reason": "expected_loss_rule_under_uncalibrated_model",
                        "prediction": float(mean[i]), "latent_sd": float(latent_sd),
                        "observation_interval90": [float(mean[i]-ndtri(.95)*observation_sd), float(mean[i]+ndtri(.95)*observation_sd)],
                        "probability_latent_below_threshold": probability,
                        "expected_losses": {**losses, "abstain": abstention},
                        "acquisition_score": float(scores[i])})
    ranked = sorted([r for r in records if r["acquisition_score"] is not None], key=lambda r: (-r["acquisition_score"], r["id"]))
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {"schema_version": 1, "context": context, "research_only": True, "human_review_required": True,
            "request_sha256": sha256(canonical.encode()).hexdigest(), "model": "ridge_conditional_gaussian_v1",
            "assumptions": {"noise_sd": noise, "ridge_penalty": penalty, "threshold": threshold,
                            "false_positive_cost": cfp, "false_negative_cost": cfn, "abstention_cost": abstention},
            "uncertainty": "conditional_on_fixed_noise_and_linear_model_not_empirically_calibrated",
            "support": "observed_input_convex_hull_only_not_biological_validity",
            "acquisition": "integrated_latent_variance_reduction_per_supplied_cost",
            "cost_semantics": "caller_supplied_relative_units_no_validated_laboratory_cost",
            "observation_ids": [r["id"] for r in observations], "candidates": records,
            "ranked_candidate_ids": [r["id"] for r in ranked],
            "next_measurement": ranked[0]["id"] if ranked else None,
            "limitations": ["No physical-dose recommendation", "No clinical treatment recommendation",
                            "No independent biological calibration", "No guaranteed assay savings"]}
