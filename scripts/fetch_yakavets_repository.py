"""Download author-published data and provenance at a pinned Git commit.

No downloaded code is executed. The first run resolves the public main branch;
subsequent runs reuse that pinned SHA. Repository license is archived alongside
the data; file-specific reuse and scientific admission still need review.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PATHS = ["FAC/concurrent/data/data_FAC_con.csv", "FAC/sequential/data/data_FAC_seq.csv",
         "OLA-IBET/concurrent/data/data_OLA-IBET_con.csv", "OLA-IBET/sequential/data/data_OLA-IBET_seq.csv",
         "README.md", "LICENSE"]


def main():
    manifest_path = ROOT / "data/yakavets_repository_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        with urllib.request.urlopen("https://api.github.com/repos/yakavetsiv/ml-mf_chemo/commits/main", timeout=30) as r:
            revision = json.load(r)["sha"]
        manifest = {"repository": "https://github.com/yakavetsiv/ml-mf_chemo", "revision": revision,
                    "retrieved_utc": datetime.now(timezone.utc).isoformat(), "files": {}}
        manifest_path.write_text(json.dumps(manifest, indent=2)+"\n")
    for relative in PATHS:
        path = ROOT / "data/raw/yakavets_repository" / relative
        url = f"https://raw.githubusercontent.com/yakavetsiv/ml-mf_chemo/{manifest['revision']}/{relative}"
        if not path.exists():
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("Unexpected source size")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        digest = sha256(path.read_bytes()).hexdigest()
        expected = manifest["files"].get(relative)
        if expected and expected["sha256"] != digest:
            raise ValueError(f"Pinned artifact changed: {relative}")
        manifest["files"][relative] = {"url": url, "sha256": digest, "bytes": path.stat().st_size}
        manifest_path.write_text(json.dumps(manifest, indent=2)+"\n")
        print(f"{relative}: {path.stat().st_size} bytes, sha256={digest}")


if __name__ == "__main__":
    main()
