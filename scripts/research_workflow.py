"""Run a strict JSON research request and write an auditable JSON response."""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from zenithsync.workflow import run_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        response = run_request(json.loads(args.request.read_text()))
    except (ValueError, ArithmeticError) as exc:
        rejection = {"status": "rejected", "reason": str(exc)}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rejection, indent=2)+"\n")
        print(json.dumps(rejection), file=sys.stderr)
        raise SystemExit(2) from None
    response["implementation_sha256"] = {
        name: sha256((ROOT/"src/zenithsync"/name).read_bytes()).hexdigest()
        for name in ["workflow.py", "linear.py", "acquisition.py", "models.py", "multidimensional.py"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(response, indent=2, allow_nan=False)+"\n")
    print(f"Saved research output for {len(response['candidates'])} candidates to {args.output}")


if __name__ == "__main__":
    main()
