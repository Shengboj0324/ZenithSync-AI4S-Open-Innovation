"""Exploratory reconstruction with finite-prior hyperparameter uncertainty.

No held-out response chooses component weights. Intervals are model-based and
tested against observed responses, not falsely called latent-curve coverage.
"""
from hashlib import sha256
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zenithsync.data import load_albumin
from zenithsync.models import GaussianProcess, dose_coordinate
from zenithsync.mixture import default_mixture


def main():
    out = ROOT / "artifacts/mixture_v1"
    out.mkdir(parents=True, exist_ok=True)
    frame, _ = load_albumin(ROOT / "data/raw/ewart_supplement_8.xlsx")
    frame = frame[frame.exclusion == ""]
    records, folds = [], []
    mixture, gp = default_mixture(), GaussianProcess()
    for compound, curve in frame.groupby("compound", sort=True):
        for dose in sorted(curve.dose.unique()):
            train, test = curve[curve.dose != dose], curve[curve.dose == dose]
            x, q = dose_coordinate(train.dose), dose_coordinate(test.dose)
            post = mixture.posterior(x, train.response.to_numpy(), q)
            mix_mean, _ = post.moments()
            intervals = post.interval(.9, observation=True)
            mix_probability = post.threshold_probability(50, observation=True)
            mean, covariance = gp.posterior(x, train.response.to_numpy(), np.full(len(train), 400.), q)
            predictive_sd = np.sqrt(np.diag(covariance)+400)
            fixed_interval = np.column_stack([mean-ndtri(.95)*predictive_sd, mean+ndtri(.95)*predictive_sd])
            fixed_probability = ndtr((50-mean)/predictive_sd)
            folds.append({"compound": compound, "held_dose": dose,
                          "train_source_rows": train.source_row.tolist(),
                          "test_source_rows": test.source_row.tolist(),
                          "posterior_weights": post.weights.tolist(),
                          "effective_components": float(1/np.sum(post.weights**2))})
            for model, mu, interval, probability in [
                ("fixed_gp", mean, fixed_interval, fixed_probability),
                ("finite_gp_mixture", mix_mean, intervals, mix_probability)]:
                for i, row in enumerate(test.itertuples()):
                    low, high = interval[i]
                    records.append({"compound": compound, "dose": dose, "source_row": row.source_row,
                                    "model": model, "observed": row.response, "predicted": float(mu[i]),
                                    "lower90": float(low), "upper90": float(high),
                                    "covered90": bool(low <= row.response <= high),
                                    "width90": float(high-low), "probability_below_50": float(probability[i]),
                                    "brier": float((probability[i]-(row.response < 50))**2),
                                    "squared_error": float((mu[i]-row.response)**2)})
    pd.DataFrame(records).to_csv(out / "predictions.csv", index=False)
    (out / "folds.json").write_text(json.dumps(folds, indent=2)+"\n")
    by_compound = pd.DataFrame(records).groupby(["model", "compound"]).agg(
        mse=("squared_error", "mean"), coverage90=("covered90", "mean"),
        width90=("width90", "mean"), brier=("brier", "mean")).reset_index()
    by_compound["rmse"] = np.sqrt(by_compound.mse)
    by_compound.to_csv(out / "by_compound.csv", index=False)
    summary = by_compound.groupby("model")[["rmse", "coverage90", "width90", "brier"]].mean()
    summary.to_csv(out / "summary.csv")
    (out / "metadata.json").write_text(json.dumps({
        "status": "exploratory; all six compounds previously inspected",
        "prior": [{"length_scale": c.gp.length_scale, "noise_sd": c.noise_sd,
                   "mean": c.gp.mean, "amplitude": c.gp.amplitude,
                   "prior_weight": float(w)} for c, w in zip(mixture.components, mixture.prior_weights, strict=True)],
        "interval_target": "new noisy normalized-albumin observation under the fitted model",
        "not_claimed": ["conformal coverage", "independent donor coverage", "assay savings", "clinical risk"],
        "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT / "src").rglob("*.py"))}}, indent=2)+"\n")
    print(summary.to_string())


if __name__ == "__main__":
    main()
