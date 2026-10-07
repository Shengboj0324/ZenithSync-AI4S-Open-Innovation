"""Admit concurrent tables for retrospective prediction within logged support.

Use authors' dimensionless concentration coordinates and measured cv_exp only.
Neither derived synergy nor theoretical viability is an admissible predictor.
This adapter does not claim independent donor replication or physical units.
"""
from hashlib import sha256
from pathlib import Path
import json
import numpy as np
import pandas as pd


def load_concurrent(root):
    root = Path(root)
    manifest = json.loads((root/"data/yakavets_repository_manifest.json").read_text())
    tables, audits = {}, {}
    for context, dimensions in [("FAC", 3), ("OLA-IBET", 2)]:
        relative = f"{context}/concurrent/data/data_{context}_con.csv"
        path = root/"data/raw/yakavets_repository"/relative
        expected = manifest["files"][relative]["sha256"]
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Source hash mismatch")
        raw = pd.read_csv(path)
        features = [f"conc{i}" for i in range(dimensions)]
        required = features+["cv_exp", "gen", "number"]
        if not set(required).issubset(raw):
            raise ValueError("Concurrent table schema mismatch")
        frame = raw[required].copy()
        for column in required:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
        if not np.isfinite(frame.to_numpy()).all():
            raise ValueError("Nonfinite admitted fields")
        if ((frame[features] < 0) | (frame[features] > 1)).any().any():
            raise ValueError("Normalized concentration outside [0,1]")
        if (frame.cv_exp < 0).any():
            raise ValueError("Negative viability coordinate")
        for column in ["gen", "number"]:
            if (frame[column] < 0).any() or not (frame[column] == np.floor(frame[column])).all():
                raise ValueError("Generation and sample identifiers must be nonnegative integers")
            frame[column] = frame[column].astype(int)
        if frame.duplicated(["gen", "number"]).any():
            raise ValueError("Duplicate sample identity")
        frame["source_row"] = np.arange(2, len(frame)+2)
        tables[context] = frame
        audits[context] = {"rows": len(frame), "features": features, "target": "cv_exp",
                           "feature_scale": "author dimensionless normalized concentration",
                           "response_scale": "author concurrent normalized viability coordinate",
                           "source_sha256": expected, "excluded_predictors": sorted(set(raw)-set(required)),
                           "duplicate_feature_rows": int(frame.duplicated(features).sum()),
                           "admitted_claim": "predict next logged generation within this assay context",
                           "not_admitted": ["unmeasured action outcomes", "independent donor generalization",
                                            "physical dose recommendation", "prospective assay savings"]}
    return tables, audits
