"""Fetch explicitly selected public research artifacts; preserve byte provenance.

Raw files are local and ignored by Git pending artifact-level rights review.
Run from the repository root. Existing files are hashed, never overwritten.
"""
from datetime import datetime, timezone
import argparse
from hashlib import sha256
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NATURE = "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs43856-022-00209-1/MediaObjects/"
SOURCES = {
    "ewart_supplement_1.xlsx": NATURE + "43856_2022_209_MOESM1_ESM.xlsx",
    "ewart_supplement_8.xlsx": NATURE + "43856_2022_209_MOESM8_ESM.xlsx",
    "yakavets_data.zip": "https://datadryad.org/downloads/file_stream/4089491",
    "yakavets_README.md": "https://datadryad.org/downloads/file_stream/4089498",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-yakavets", action="store_true", help="Optional secondary source; server may deny downloads")
    args = parser.parse_args()
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "data/source_manifest.json"
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name, url in SOURCES.items():
        if name.startswith("yakavets") and not args.include_yakavets:
            continue
        path = raw / name
        if not path.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "ZenithSync-Research/0.1"})
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read(20_000_001)
            if len(content) > 20_000_000:
                raise ValueError(f"Unexpected artifact size: {name}")
            if name.endswith((".zip", ".xlsx")) and not content.startswith(b"PK"):
                raise ValueError(f"Expected ZIP container: {name}")
            path.write_bytes(content)
        digest = sha256(path.read_bytes()).hexdigest()
        if name in previous:
            if previous[name]["sha256"] != digest or previous[name]["url"] != url:
                raise ValueError(f"Source differs from pinned manifest: {name}")
        else:
            previous[name] = {"url": url, "sha256": digest, "bytes": path.stat().st_size,
                              "retrieved_utc": datetime.now(timezone.utc).isoformat()}
        manifest_path.write_text(json.dumps(previous, indent=2) + "\n")
        print(f"{name}: {path.stat().st_size} bytes sha256={digest}")


if __name__ == "__main__":
    main()
