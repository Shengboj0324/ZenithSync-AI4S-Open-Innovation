"""Run the recorded model/policy sensitivity grid; retain all settings."""
from hashlib import sha256
from pathlib import Path
import json
import sys
import time
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zenithsync.data import load_albumin
from zenithsync.models import GaussianProcess, dose_coordinate
from zenithsync.replay import replay_curve


def main():
    config_path = ROOT / "configs/sensitivity-v1.json"
    config = json.loads(config_path.read_text())
    output = ROOT / "artifacts/sensitivity_v1"
    output.mkdir(parents=True, exist_ok=True)
    frame, _ = load_albumin(ROOT / "data/raw/ewart_supplement_8.xlsx")
    curves = frame[frame.exclusion == ""].groupby(["compound", "dose"]).response.mean().reset_index()
    rows, started = [], time.perf_counter()
    with (output / "traces.jsonl").open("w") as trace_file:
        for noise_sd in config["noise_sd"]:
            for length in config["length_scale"]:
                gp = GaussianProcess(amplitude=config["amplitude"], length_scale=length, mean=config["mean"])
                for compound, group in curves.groupby("compound", sort=True):
                    group = group.sort_values("dose")
                    x, y = dose_coordinate(group.dose), group.response.to_numpy()
                    for audit in range(len(x)):
                        for policy in config["policies"]:
                            seeds = range(config["random_seeds"]) if policy == "random" else [0]
                            for seed in seeds:
                                trace = replay_curve(x, y, audit, policy, seed, noise_sd**2, gp=gp)
                                for step in trace:
                                    row = {"noise_sd": noise_sd, "length_scale": length,
                                           "compound": compound, "policy": policy, "seed": seed, **step}
                                    trace_file.write(json.dumps(row, allow_nan=False)+"\n")
                                    rows.append(row)
                print(f"Completed noise_sd={noise_sd}, length_scale={length}", flush=True)
    table = pd.DataFrame(rows)
    dimensions = ["noise_sd", "length_scale", "compound", "policy", "budget"]
    by_audit = table.groupby(dimensions+["audit_index"])[["squared_error", "threshold_error"]].mean()
    by_compound = by_audit.groupby(dimensions).mean().reset_index()
    by_compound["rmse"] = np.sqrt(by_compound.squared_error)
    by_compound.to_csv(output / "by_compound.csv", index=False)
    summary = by_compound.groupby(["noise_sd", "length_scale", "policy", "budget"]).agg(
        macro_rmse=("rmse", "mean"), threshold_error=("threshold_error", "mean"),
        n_compounds=("compound", "nunique")).reset_index()
    summary.to_csv(output / "summary.csv", index=False)
    metadata = {"config": config, "config_sha256": sha256(config_path.read_bytes()).hexdigest(),
                "elapsed_seconds": time.perf_counter()-started, "trace_rows": len(table),
                "adaptive_error_estimate_max": float(table[table.policy == "decision_voi_adaptive"].quadrature_difference.max()),
                "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                  for p in sorted((ROOT / "src").rglob("*.py"))}}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(summary[summary.budget == config["primary_comparison_budget"]].to_string(index=False))


if __name__ == "__main__":
    main()
