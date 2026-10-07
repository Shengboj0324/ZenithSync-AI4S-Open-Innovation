"""Outer held-dose evaluation of training-only GP selection and simple curves."""
from pathlib import Path
from hashlib import sha256
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zenithsync.data import load_albumin
from zenithsync.models import dose_coordinate, fit_hill, GaussianProcess
from zenithsync.mixture import default_mixture
from zenithsync.tuning import tune_gp, interpolate_curve


def main():
    out = ROOT / "artifacts/nested_baselines_v1"
    out.mkdir(parents=True, exist_ok=True)
    data, _ = load_albumin(ROOT / "data/raw/ewart_supplement_8.xlsx")
    data = data[data.exclusion == ""]
    records, selections = [], []
    for compound, group in data.groupby("compound", sort=True):
        for held in sorted(group.dose.unique()):
            train, test = group[group.dose != held], group[group.dose == held]
            x, q, y = dose_coordinate(train.dose), dose_coordinate(test.dose), train.response.to_numpy()
            gp, noise_sd, diagnostics = tune_gp(x, y)
            tuned, _ = gp.posterior(x, y, np.full(len(x), noise_sd**2), q)
            fixed, _ = GaussianProcess().posterior(x, y, np.full(len(x), 400.), q)
            mixture, _ = default_mixture().posterior(x, y, q).moments()
            hill, _ = fit_hill(train.dose, y)
            predictions = {"nested_gp": tuned, "fixed_gp": fixed, "finite_gp_mixture": mixture,
                           "hill": hill(test.dose), "linear": interpolate_curve(x, y, q),
                           "pchip": interpolate_curve(x, y, q, "pchip"),
                           "constant": np.full(len(q), y.mean())}
            selections.append({"compound": compound, "held_dose": float(held),
                               "train_rows": train.source_row.tolist(), "test_rows": test.source_row.tolist(),
                               **diagnostics})
            for model, values in predictions.items():
                for row, value in zip(test.itertuples(), values, strict=True):
                    records.append({"compound": compound, "held_dose": float(held),
                                    "source_row": row.source_row, "model": model,
                                    "observed": row.response, "predicted": float(value),
                                    "squared_error": float((row.response-value)**2),
                                    "absolute_error": float(abs(row.response-value)),
                                    "position": "interpolation" if train.dose.min() < held < train.dose.max() else "edge_extrapolation"})
        print(f"Completed {compound}", flush=True)
    table = pd.DataFrame(records)
    table.to_csv(out / "predictions.csv", index=False)
    (out / "selections.json").write_text(json.dumps(selections, indent=2)+"\n")
    by_compound = table.groupby(["model", "compound"]).agg(mse=("squared_error", "mean"), mae=("absolute_error", "mean")).reset_index()
    by_compound["rmse"] = np.sqrt(by_compound.mse)
    by_compound.to_csv(out / "by_compound.csv", index=False)
    summary = by_compound.groupby("model")[["rmse", "mae"]].mean().sort_values("rmse")
    summary.to_csv(out / "summary.csv")
    by_position = table.groupby(["model", "compound", "position"]).squared_error.mean().pow(.5).reset_index(name="rmse")
    by_position.groupby(["model", "position"]).rmse.mean().to_csv(out / "by_position.csv")
    (out / "metadata.json").write_text(json.dumps({
        "protocol": "outer held dose; inner held dose selection; all dose replicates grouped",
        "status": "exploratory nested evaluation; not independent biological confirmation",
        "candidate_count": len(selections[0]["candidates"]),
        "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT / "src").rglob("*.py"))}}, indent=2)+"\n")
    print(summary.to_string())


if __name__ == "__main__":
    main()
