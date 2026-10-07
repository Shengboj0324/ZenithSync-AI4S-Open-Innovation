"""Profile pinned author tables without guessing units or repairing malformed data."""
from hashlib import sha256
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    raw = ROOT / "data/raw/yakavets_repository"
    manifest = json.loads((ROOT / "data/yakavets_repository_manifest.json").read_text())
    output = {}
    for relative, source in sorted(manifest["files"].items()):
        if not relative.endswith(".csv"):
            continue
        path = raw / relative
        if sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Unreviewed source bytes: {relative}")
        frame = pd.read_csv(path)
        if not {"gen", "number"}.issubset(frame.columns):
            raise ValueError("Missing generation/sample identifiers")
        fields = {}
        for name in frame:
            numeric = pd.to_numeric(frame[name], errors="coerce")
            bad = numeric.isna() & frame[name].notna()
            fields[name] = {"missing": int(frame[name].isna().sum()), "numeric_count": int(numeric.notna().sum()),
                            "numeric_min": float(numeric.min()) if numeric.notna().any() else None,
                            "numeric_max": float(numeric.max()) if numeric.notna().any() else None,
                            "nonnumeric_values": frame.loc[bad, name].astype(str).unique().tolist()}
        output[relative] = {"rows": len(frame), "columns": list(frame),
                            "generation_counts": frame.gen.value_counts().sort_index().to_dict(),
                            "duplicate_generation_number": int(frame.duplicated(["gen", "number"]).sum()),
                            "fields": fields}
    out = ROOT / "artifacts/yakavets_admission"
    out.mkdir(parents=True, exist_ok=True)
    (out / "initial_quality_audit.json").write_text(json.dumps(output, indent=2, allow_nan=False)+"\n")
    print(f"Audited {sum(o['rows'] for o in output.values())} rows across {len(output)} tables; no biological modeling admission yet.")


if __name__ == "__main__":
    main()
