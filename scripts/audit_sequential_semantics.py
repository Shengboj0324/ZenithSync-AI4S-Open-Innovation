"""Record unresolved sequential timing semantics without guessing conversions."""
from pathlib import Path
from hashlib import sha256
import json
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["OLA-IBET/sequential/GS0/run_gryffin.py", "OLA-IBET/sequential/GS1-GS2/run_gryffin.py",
           "FAC/sequential/GS0-GS1/run_gryffin.py", "FAC/sequential/GS2/run_gryffin.py"]


def main():
    manifest = json.loads((ROOT/"data/yakavets_repository_manifest.json").read_text())
    revision = manifest["revision"]
    evidence = {"revision": revision, "tables": {}, "source_excerpts": [],
                "decision": "sequential physical-time admission remains unresolved; no model fitting",
                "reason": "repository initial and later timing configurations differ; do not infer units or drug-order mapping"}
    for context in ["FAC", "OLA-IBET"]:
        relative = f"{context}/sequential/data/data_{context}_seq.csv"
        path = ROOT/"data/raw/yakavets_repository"/relative
        if sha256(path.read_bytes()).hexdigest() != manifest["files"][relative]["sha256"]:
            raise ValueError("Unreviewed source table")
        frame = pd.read_csv(path)
        evidence["tables"][context] = {
            "rows": len(frame), "sequence_labels": sorted(frame.seq.unique().tolist()),
            "sum_t0_t1_by_generation": {str(g): sorted(set((f.t0+f.t1).tolist())) for g, f in frame.groupby("gen")},
            "response_range": [float(frame.cv.min()), float(frame.cv.max())]}
    for relative in SOURCES:
        url = f"https://raw.githubusercontent.com/yakavetsiv/ml-mf_chemo/{revision}/{relative}"
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read(100_001)
        if len(content) > 100_000:
            raise ValueError("Unexpected source size")
        lines = content.decode().splitlines()
        excerpts = [{"line": i, "text": line.strip()} for i, line in enumerate(lines, 1)
                    if '"name": "t0"' in line or "df_samples['t1']" in line]
        evidence["source_excerpts"].append({"url": url, "sha256": sha256(content).hexdigest(), "lines": excerpts})
    output = ROOT/"artifacts/yakavets_admission/sequential_semantics.json"
    output.write_text(json.dumps(evidence, indent=2)+"\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
