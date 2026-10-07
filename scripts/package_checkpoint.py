"""Package reviewable local work with a content manifest; never publish it.

Exclude raw third-party downloads, virtual environments, IDE files, Git internals
and earlier archives. Source URLs/hashes and fetch scripts preserve acquisition.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    paths = [ROOT/name for name in ["README.md", "pyproject.toml", "requirements-lock.txt", ".gitignore"]]
    for folder in ["src", "scripts", "tests", "configs", "docs", "examples"]:
        paths.extend(p for p in (ROOT/folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    paths.extend((ROOT/"data").glob("*.json"))
    paths.extend(p for p in (ROOT/"artifacts").rglob("*") if p.is_file() and
                 "checkpoints" not in p.parts and p.suffix in {".json", ".jsonl", ".csv", ".txt"})
    paths = sorted(set(paths))
    signatures = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in paths}
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = ROOT/"artifacts/checkpoints"/f"research-checkpoint-{stamp}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"created_utc": stamp, "base_git_commit": head, "includes_uncommitted_work": True,
                "status": "research checkpoint; not a validated winning solution or public submission",
                "excluded": ["raw downloads", "virtual environments", "IDE state", "Git internals", "prior archives"],
                "files": {}}
    try:
        with ZipFile(out, "x", compression=ZIP_DEFLATED) as archive:
            for path in paths:
                content = path.read_bytes()
                relative = str(path.relative_to(ROOT))
                archive.writestr(relative, content)
                manifest["files"][relative] = {"sha256": sha256(content).hexdigest(), "bytes": len(content)}
            if any((p.stat().st_size, p.stat().st_mtime_ns) != signatures[p] for p in paths):
                raise RuntimeError("Workspace changed during packaging; retry a consistent snapshot")
            if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != head:
                raise RuntimeError("Git HEAD changed during packaging")
            archive.writestr("CHECKPOINT-MANIFEST.json", json.dumps(manifest, indent=2)+"\n")
        with ZipFile(out) as archive:
            assert archive.testzip() is None
            for relative, entry in manifest["files"].items():
                if sha256(archive.read(relative)).hexdigest() != entry["sha256"]:
                    raise RuntimeError("Archive content verification failed")
    except BaseException:
        out.unlink(missing_ok=True)
        raise
    digest = sha256(out.read_bytes()).hexdigest()
    out.with_suffix(".sha256").write_text(f"{digest}  {out.name}\n")
    print(json.dumps({"path": str(out), "files": len(manifest["files"]), "bytes": out.stat().st_size, "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
