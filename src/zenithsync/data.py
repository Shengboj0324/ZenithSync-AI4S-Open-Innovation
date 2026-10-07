"""Strict adapter for the pinned Ewart Supplementary Data 8 workbook."""
from hashlib import sha256
from pathlib import Path
import numpy as np
import pandas as pd

EWART_SHA256 = "87cc22d0c1d4508f7e0830df348c52238bdb18d821c8d29cc0751114081509fc"


def load_albumin(path: str | Path):
    path = Path(path)
    if sha256(path.read_bytes()).hexdigest() != EWART_SHA256:
        raise ValueError("Unrecognized workbook version; audit before admission")
    frame = pd.read_excel(path, sheet_name="ALBUMIN", keep_default_na=True)
    expected = ["Compound_Name", "Concentration_Day3", "Normalized_Albumin_Levels"]
    if list(frame.columns) != expected:
        raise ValueError("Unexpected albumin schema")
    frame.columns = ["compound", "dose", "response"]
    frame["source_row"] = np.arange(2, len(frame)+2)
    for field in ["dose", "response"]:
        frame[field] = pd.to_numeric(frame[field], errors="raise")
    if frame.compound.isna().any() or frame.dose.isna().any() or (frame.dose < 0).any():
        raise ValueError("Missing compound or invalid dose")
    if not np.isfinite(frame.dose).all() or not np.isfinite(frame.response.dropna()).all():
        raise ValueError("Infinite values are not missing values")
    frame["exclusion"] = np.where(frame.response.isna(), "missing_response", "")
    # No donor/chip identifiers are inferred from row order or duplicate doses.
    frame["donor_id"] = None
    frame["chip_id"] = None
    frame["dose_unit"] = "source_reported_concentration_coordinate"
    frame["endpoint"] = "normalized_albumin_day3"
    audit = {"rows": len(frame), "missing_response": int(frame.response.isna().sum()),
             "compounds": sorted(frame.compound.unique().tolist()),
             "compound_dose_groups": int(frame.groupby(["compound", "dose"]).ngroups),
             "donor_identity_available": False, "chip_identity_available": False,
             "admission": "exploratory_within_compound_only",
             "dose_unit_status": "workbook has no unit; no conversion or physical-dose recommendation",
             "source_sha256": EWART_SHA256}
    return frame, audit
