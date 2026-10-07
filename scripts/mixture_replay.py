"""Measured-pool comparison with a finite-mixture predictor and matched policies."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zenithsync.data import load_albumin
from zenithsync.models import dose_coordinate
from zenithsync.mixture import default_mixture, mixture_variance_reduction


def run_curve(x, y, audit, policy, seed):
    pool = np.delete(np.arange(len(x)), audit)
    pool = pool[np.argsort(x[pool])]
    selected = [int(pool[0]), int(pool[-1])]
    model, rng = default_mixture(), np.random.default_rng(seed)
    trace, discrepancy = [], 0.
    while True:
        post = model.posterior(x[selected], y[selected], x)
        mean, _ = post.moments()
        probabilities = post.threshold_probability(50)
        trace.append({"budget": len(selected), "audit_index": audit, "selected_indices": list(selected),
                      "revealed_outcomes": y[selected].tolist(), "posterior_weights": post.weights.tolist(),
                      "prediction": float(mean[audit]), "audit_observation": float(y[audit]),
                      "squared_error": float((mean[audit]-y[audit])**2),
                      "threshold_error": int((probabilities[audit] > .5) != (y[audit] < 50)),
                      "quadrature_difference": discrepancy})
        available = np.array([i for i in pool if i not in selected], dtype=int)
        if not len(available):
            return trace
        if policy == "random":
            choice = int(rng.choice(available))
        elif policy == "space_filling":
            distance = abs(x[available, None]-x[selected][None, :]).min(axis=1)
            choice = int(available[np.argmax(distance)])
        elif policy == "mixture_variance":
            # Same pool-target objective as the fixed-GP comparison. Audit
            # outcomes and coordinates do not direct candidate acquisition.
            weights = np.zeros(len(x))
            weights[pool] = 1/len(pool)
            low = mixture_variance_reduction(post, np.ones(len(x)), weights, nodes=64)
            scores = mixture_variance_reduction(post, np.ones(len(x)), weights, nodes=128)
            discrepancy = float(np.max(abs(scores[available]-low[available])))
            if discrepancy > .01:
                refined = mixture_variance_reduction(post, np.ones(len(x)), weights, nodes=512)
                discrepancy = float(np.max(abs(refined[available]-scores[available])))
                scores = refined
                if discrepancy > .01:
                    raise ArithmeticError("Mixture variance acquisition quadrature has not stabilized")
            choice = int(available[np.argmax(scores[available])])
        else:
            raise ValueError("Unknown mixture policy")
        selected.append(choice)


def main():
    output = ROOT / "artifacts/mixture_replay_v1"
    output.mkdir(parents=True, exist_ok=True)
    frame, _ = load_albumin(ROOT / "data/raw/ewart_supplement_8.xlsx")
    curves = frame[frame.exclusion == ""].groupby(["compound", "dose"]).response.mean().reset_index()
    rows = []
    for compound, group in curves.groupby("compound", sort=True):
        group = group.sort_values("dose")
        x, y = dose_coordinate(group.dose), group.response.to_numpy()
        for audit in range(len(x)):
            for policy in ["random", "space_filling", "mixture_variance"]:
                for seed in (range(20) if policy == "random" else [0]):
                    rows.extend({"compound": compound, "policy": policy, "seed": seed, **step}
                                for step in run_curve(x, y, audit, policy, seed))
        print(f"Completed {compound}", flush=True)
    table = pd.DataFrame(rows)
    table.to_json(output / "traces.jsonl", orient="records", lines=True, double_precision=15)
    by_audit = table.groupby(["compound", "policy", "budget", "audit_index"])[["squared_error", "threshold_error"]].mean()
    by_compound = by_audit.groupby(["compound", "policy", "budget"]).mean().reset_index()
    by_compound["rmse"] = np.sqrt(by_compound.squared_error)
    by_compound.to_csv(output / "by_compound.csv", index=False)
    summary = by_compound.groupby(["policy", "budget"]).agg(
        macro_rmse=("rmse", "mean"), threshold_error=("threshold_error", "mean"),
        n_compounds=("compound", "nunique")).reset_index()
    summary.to_csv(output / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
