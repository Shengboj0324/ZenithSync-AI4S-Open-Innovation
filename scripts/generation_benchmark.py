"""Expanding-generation evaluation; no random split of adaptively collected data."""
from dataclasses import asdict
from itertools import product
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from zenithsync.multidimensional import DesignGP, design
from zenithsync.models import vector
from zenithsync.yakavets import load_concurrent


def fit_select(x, y, generation):
    x, y, generation = design(x, "x"), vector(y, "y"), vector(generation, "generation")
    if not len(x) or len(x) != len(y) or len(x) != len(generation):
        raise ValueError("Nonempty training arrays must align")
    if np.any(generation < 0) or np.any(generation != np.floor(generation)):
        raise ValueError("Generation identifiers must be nonnegative integers")
    candidates = [DesignGP(amplitude=a, length_scale=l, noise_sd=s)
                  for a, l, s in product((.2, .5, 1.), (.1, .3, 1.), (.05, .15, .3))]
    generations = np.unique(generation)
    if len(generations) < 2:
        return DesignGP(), {"selection": "prespecified_default_no_inner_generation", "scores": []}
    scores = []
    for candidate in candidates:
        losses = []
        for held in generations[1:]:
            train, test = generation < held, generation == held
            prediction, _ = candidate.posterior(x[train], y[train], x[test])
            losses.append(float(np.mean((prediction-y[test])**2)))
        scores.append({"parameters": asdict(candidate), "inner_generation_mse": losses,
                       "mean_mse": float(np.mean(losses))})
    selected = int(np.argmin([s["mean_mse"] for s in scores]))
    return candidates[selected], {"selection": "minimum_past_generation_macro_mse", "selected": selected, "scores": scores}


def main():
    out = ROOT/"artifacts/generation_benchmark_v1"
    out.mkdir(parents=True, exist_ok=True)
    tables, audits = load_concurrent(ROOT)
    rows, folds = [], []
    for context, frame in tables.items():
        features = audits[context]["features"]
        for generation in sorted(frame.gen.unique())[1:]:
            train, test = frame[frame.gen < generation], frame[frame.gen == generation]
            x, q = train[features].to_numpy(), test[features].to_numpy()
            y = train.cv_exp.to_numpy()
            gp, selection = fit_select(x, y, train.gen.to_numpy())
            tuned, _ = gp.posterior(x, y, q)
            fixed, _ = DesignGP().posterior(x, y, q)
            distance = np.sum((q[:, None, :]-x[None, :, :])**2, axis=2)
            nearest = y[np.argmin(distance, axis=1)]
            # Ridge intercept is unpenalized; features already have declared units.
            design = np.column_stack([np.ones(len(x)), x])
            penalty = np.diag([0.]+[.1]*x.shape[1])
            coefficient = np.linalg.solve(design.T@design+penalty, design.T@y)
            ridge = np.column_stack([np.ones(len(q)), q])@coefficient
            predictions = {"train_mean": np.full(len(q), y.mean()), "nearest": nearest,
                           "ridge_fixed": ridge, "gp_fixed": fixed, "gp_past_tuned": tuned}
            folds.append({"context": context, "test_generation": int(generation),
                          "training_generations": sorted(train.gen.unique().tolist()),
                          "train_rows": train.source_row.tolist(), "test_rows": test.source_row.tolist(), **selection})
            for model, values in predictions.items():
                for record, value in zip(test.itertuples(), values, strict=True):
                    rows.append({"context": context, "generation": int(generation), "source_row": record.source_row,
                                 "model": model, "observed": record.cv_exp, "predicted": float(value),
                                 "squared_error": float((value-record.cv_exp)**2), "absolute_error": float(abs(value-record.cv_exp))})
    table = pd.DataFrame(rows)
    table.to_csv(out/"predictions.csv", index=False)
    metrics = table.groupby(["context", "model", "generation"]).agg(mse=("squared_error", "mean"), mae=("absolute_error", "mean")).reset_index()
    metrics["rmse"] = np.sqrt(metrics.mse)
    metrics.to_csv(out/"by_generation.csv", index=False)
    summary = metrics.groupby(["context", "model"])[["rmse", "mae"]].mean()
    summary.to_csv(out/"summary.csv")
    (out/"folds.json").write_text(json.dumps(folds, indent=2)+"\n")
    (out/"admission.json").write_text(json.dumps(audits, indent=2)+"\n")
    print(summary.to_string())


if __name__ == "__main__":
    main()
