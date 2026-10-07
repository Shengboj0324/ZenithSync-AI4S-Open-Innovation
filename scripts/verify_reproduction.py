"""Install the locked environment afresh and compare deterministic result bytes.

Creates a temporary environment outside the checkout and removes it on exit.
The full subprocess transcript is saved even on failure. This tests dependency
reproduction on the current machine, not independent scientific replication.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ["initial_benchmark/predictions.json", "initial_benchmark/macro_metrics.csv",
           "initial_benchmark/data_audit.json", "initial_benchmark/hill_diagnostics.json",
           "measured_pool_replay/traces.json", "measured_pool_replay/macro_metrics.csv",
           "sensitivity_v1/summary.csv", "sensitivity_v1/traces.jsonl",
           "mixture_v1/summary.csv", "mixture_v1/predictions.csv", "mixture_v1/folds.json",
           "mixture_replay_v1/summary.csv", "mixture_replay_v1/traces.jsonl",
           "nested_baselines_v1/summary.csv", "nested_baselines_v1/selections.json",
           "nested_baselines_v1/predictions.csv",
           "generation_benchmark_v1/summary.csv", "generation_benchmark_v1/predictions.csv",
           "generation_benchmark_v1/folds.json", "generation_benchmark_v1/admission.json",
           "workflow_v1/response.json"]


def hashes():
    return {name: sha256((ROOT / "artifacts" / name).read_bytes()).hexdigest() for name in RESULTS}


def main():
    logs = ROOT / "artifacts/logs"
    logs.mkdir(parents=True, exist_ok=True)
    before = hashes()
    record = {"started_utc": datetime.now(timezone.utc).isoformat(), "commands": [], "before": before}
    with (logs / "fresh-environment.txt").open("w") as transcript:
        try:
            with tempfile.TemporaryDirectory(prefix="zenithsync-reproduce-") as folder:
                venv.create(folder, with_pip=True)
                python = str(Path(folder) / "bin/python")
                commands = [[python, "-m", "pip", "install", "-r", "requirements-lock.txt"],
                            [python, "-m", "pytest", "-q", "-W", "error"],
                            [python, "scripts/benchmark.py"],
                            [python, "scripts/replay_benchmark.py"],
                            [python, "scripts/sensitivity_benchmark.py"],
                            [python, "scripts/mixture_benchmark.py"],
                            [python, "scripts/mixture_replay.py"],
                            [python, "scripts/nested_baselines.py"],
                            [python, "-W", "error", "scripts/generation_benchmark.py"],
                            [python, "scripts/build_workflow_example.py"],
                            [python, "-W", "error", "scripts/research_workflow.py", "examples/ola_ibet_request.json",
                             "--output", "artifacts/workflow_v1/response.json"]]
                for command in commands:
                    transcript.write("\nCOMMAND " + repr(command) + "\n")
                    transcript.flush()
                    result = subprocess.run(command, cwd=ROOT, stdout=transcript, stderr=subprocess.STDOUT)
                    record["commands"].append({"argv": command, "returncode": result.returncode})
                    if result.returncode:
                        raise RuntimeError(f"Reproduction subprocess failed: {command[1:]}")
                record["after"] = hashes()
                record["byte_identical"] = record["after"] == before
                if not record["byte_identical"]:
                    raise RuntimeError("Deterministic artifacts changed during clean reproduction")
        finally:
            record["finished_utc"] = datetime.now(timezone.utc).isoformat()
            (logs / "reproduction.json").write_text(json.dumps(record, indent=2)+"\n")
    print(f"Clean environment passed; {len(RESULTS)} key result artifacts reproduced byte for byte.")


if __name__ == "__main__":
    main()
