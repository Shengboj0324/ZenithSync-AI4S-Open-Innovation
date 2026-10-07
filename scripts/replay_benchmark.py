"""Run deterministic measured-pool replays and save every acquisition decision."""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zenithsync.data import load_albumin
from zenithsync.models import dose_coordinate
from zenithsync.replay import replay_curve


def main():
    output = ROOT / "artifacts/measured_pool_replay"
    output.mkdir(parents=True, exist_ok=True)
    observations, _ = load_albumin(ROOT / "data/raw/ewart_supplement_8.xlsx")
    curves = observations[observations.exclusion == ""].groupby(["compound", "dose"]).response.mean().reset_index()
    traces = []
    for compound, group in curves.groupby("compound", sort=True):
        group = group.sort_values("dose")
        x, y = dose_coordinate(group.dose), group.response.to_numpy()
        for audit_index in range(len(group)):
            for policy in ["random", "space_filling", "integrated_variance", "decision_voi"]:
                for seed in (range(20) if policy == "random" else [0]):
                    for record in replay_curve(x, y, audit_index, policy, seed):
                        traces.append({"compound": compound, "policy": policy, "seed": seed,
                                       "dose_grid": group.dose.tolist(), **record})
    (output / "traces.json").write_text(json.dumps(traces, indent=2, allow_nan=False)+"\n")
    frame = pd.DataFrame(traces)
    # Average seeds, then audit doses, then compounds: seeds do not inflate biological N.
    per_audit = frame.groupby(["compound", "policy", "budget", "audit_index"])[["squared_error", "threshold_error"]].mean()
    per_compound = per_audit.groupby(["compound", "policy", "budget"]).mean().reset_index()
    per_compound["rmse"] = np.sqrt(per_compound.squared_error)
    per_compound.to_csv(output / "metrics_by_compound.csv", index=False)
    summary = per_compound.groupby(["policy", "budget"]).agg(
        macro_rmse=("rmse", "mean"), macro_threshold_error=("threshold_error", "mean"),
        compound_count=("compound", "nunique")).reset_index()
    summary.to_csv(output / "macro_metrics.csv", index=False)
    print(summary.to_string(index=False))
    print("Budget is a revealed dose-group mean, not a chip or validated experimental cost.")
    print("Later budgets have fewer eligible compounds; compare policies within a budget.")


if __name__ == "__main__":
    main()
