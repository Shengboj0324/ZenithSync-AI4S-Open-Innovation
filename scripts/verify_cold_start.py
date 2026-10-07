"""Validate a packaged checkout with no existing environment or raw-data cache."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import venv
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    result_names = runpy.run_path(str(ROOT/"scripts/verify_reproduction.py"))["RESULTS"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    logs = ROOT/"artifacts/logs/cold-start"/stamp
    logs.mkdir(parents=True)
    record = {"started_utc": stamp, "archive_sha256": sha256(args.archive.read_bytes()).hexdigest(),
              "commands": [], "raw_cache_initially_absent": False, "success": False}
    with (logs/"transcript.txt").open("w") as transcript:
        try:
            with tempfile.TemporaryDirectory(prefix="zenithsync-cold-start-") as temporary:
                workspace = Path(temporary)/"checkout"
                workspace.mkdir()
                with ZipFile(args.archive) as archive:
                    manifest = json.loads(archive.read("CHECKPOINT-MANIFEST.json"))
                    for name, entry in manifest["files"].items():
                        path = (workspace/name).resolve()
                        if not path.is_relative_to(workspace.resolve()):
                            raise ValueError("Archive member escapes checkout")
                        content = archive.read(name)
                        if sha256(content).hexdigest() != entry["sha256"]:
                            raise ValueError("Archive hash mismatch")
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(content)
                record["raw_cache_initially_absent"] = not (workspace/"data/raw").exists()
                if not record["raw_cache_initially_absent"]:
                    raise ValueError("Cold start must not include raw cache")
                before = {name: sha256((workspace/"artifacts"/name).read_bytes()).hexdigest() for name in result_names}
                venv.create(Path(temporary)/"environment", with_pip=True)
                python = str(Path(temporary)/"environment/bin/python")
                scripts = ["fetch_public_data.py", "fetch_yakavets_repository.py", "benchmark.py",
                           "replay_benchmark.py", "sensitivity_benchmark.py", "mixture_benchmark.py",
                           "mixture_replay.py", "nested_baselines.py", "generation_benchmark.py",
                           "build_workflow_example.py", "linear_policy_benchmark.py", "summarize_linear_policy.py",
                           "uncertainty_audit.py"]
                commands = [[python, "-m", "pip", "install", "-r", "requirements-lock.txt"],
                            [python, "-m", "pytest", "-q", "-W", "error"]]
                commands.extend([python, "scripts/"+script] for script in scripts)
                commands.append([python, "-W", "error", "scripts/research_workflow.py", "examples/ola_ibet_request.json",
                                 "--output", "artifacts/workflow_v1/response.json"])
                for command in commands:
                    transcript.write("\nCOMMAND "+repr(command)+"\n")
                    transcript.flush()
                    run = subprocess.run(command, cwd=workspace, stdout=transcript, stderr=subprocess.STDOUT)
                    record["commands"].append({"argv": command[1:], "returncode": run.returncode})
                    if run.returncode:
                        raise RuntimeError(f"Cold-start command failed: {command[1:]}")
                after = {name: sha256((workspace/"artifacts"/name).read_bytes()).hexdigest() for name in result_names}
                record.update(before=before, after=after, byte_identical=before == after)
                if before != after:
                    raise RuntimeError("Cold-start results differ from packaged results")
                record["success"] = True
        finally:
            record["finished_utc"] = datetime.now(timezone.utc).isoformat()
            (logs/"record.json").write_text(json.dumps(record, indent=2)+"\n")
            (ROOT/"artifacts/logs/latest-cold-start.json").write_text(json.dumps({"record": str(logs.relative_to(ROOT)/"record.json")}, indent=2)+"\n")
    print(f"Cold start passed: {len(result_names)} byte-identical artifacts. Evidence: {logs}")


if __name__ == "__main__":
    main()
