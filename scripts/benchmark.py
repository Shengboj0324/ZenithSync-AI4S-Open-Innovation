"""Exploratory leave-one-dose-out benchmark. All replicates of a dose stay together.

This is within-compound reconstruction, not donor/compound generalization. Fixed
GP settings are a declared starting baseline, not validated biological priors.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zenithsync.data import load_albumin
from zenithsync.models import GaussianProcess, dose_coordinate, fit_hill


def main():
    output = ROOT / "artifacts/initial_benchmark"
    output.mkdir(parents=True, exist_ok=True)
    frame, audit = load_albumin(ROOT / "data/raw/ewart_supplement_8.xlsx")
    frame.to_csv(output / "observations.csv", index=False)
    (output / "data_audit.json").write_text(json.dumps(audit, indent=2)+"\n")
    valid = frame[frame.exclusion == ""]
    records, fits = [], []
    for compound, group in valid.groupby("compound", sort=True):
        for held_dose in sorted(group.dose.unique()):
            train, test = group[group.dose != held_dose], group[group.dose == held_dose]
            assert not set(train.source_row) & set(test.source_row)
            x = dose_coordinate(train.dose)
            query = dose_coordinate(test.dose)
            # Fixed 20 response-unit SD. Does not estimate covariance from shared controls.
            gp = GaussianProcess()
            mean, cov = gp.posterior(x, train.response.to_numpy(), np.full(len(train), 400.), query)
            hill_predict, diagnostic = fit_hill(train.dose, train.response)
            fits.append({"compound": compound, "held_dose": held_dose, **diagnostic})
            predictions = {"constant_train_mean": np.full(len(test), train.response.mean()),
                           "hill_decreasing": hill_predict(test.dose), "matern_gp_fixed": mean}
            for model, predictions_for_model in predictions.items():
                for row, prediction in zip(test.itertuples(), predictions_for_model, strict=True):
                    records.append({"compound": compound, "dose": held_dose,
                                    "source_row": row.source_row, "model": model,
                                    "observed": row.response, "predicted": float(prediction),
                                    "train_rows": train.source_row.tolist()})
    predictions = pd.DataFrame(records)
    predictions.to_json(output / "predictions.json", orient="records", indent=2)
    predictions["squared_error"] = (predictions.predicted-predictions.observed)**2
    predictions["absolute_error"] = abs(predictions.predicted-predictions.observed)
    metrics = predictions.groupby(["model", "compound"]).agg(
        mse=("squared_error", "mean"), mae=("absolute_error", "mean"), n=("observed", "size")).reset_index()
    metrics["rmse"] = np.sqrt(metrics.mse)
    metrics.to_csv(output / "metrics_by_compound.csv", index=False)
    summary = metrics.groupby("model")[["rmse", "mae"]].mean().reset_index()
    summary.to_csv(output / "macro_metrics.csv", index=False)
    (output / "hill_diagnostics.json").write_text(json.dumps(fits, indent=2)+"\n")
    metadata = {"created_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
                "protocol": "leave_one_dose_out_all_replicates_together_exploratory",
                "gp": {"amplitude": 50, "length_scale": 1.5, "mean": 100, "noise_sd": 20},
                "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                  for p in sorted((ROOT / "src").rglob("*.py"))},
                "limitations": ["unknown donor/chip identities", "shared-control covariance unavailable",
                                "source concentration units unresolved", "no independent confirmatory cohort",
                                "conditional GP uncertainty; no biological calibration guarantee"]}
    (output / "run_metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(summary.to_string(index=False))
    print("Exploratory reconstruction only; no ranking or assay-savings conclusion.")


if __name__ == "__main__":
    main()
