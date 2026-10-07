"""Run the strict local measured-well research workflow."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.well_workflow import plan_wells


def reject_constant(value):
    raise ValueError('Nonfinite JSON numeric constant: '+value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: '+key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.request.stat().st_size > 1048576:
        parser.error('Request exceeds the one MiB input bound')
    try:
        request = json.loads(args.request.read_text(), parse_constant=reject_constant, object_pairs_hook=unique_object)
        result = plan_wells(request)
    except (ValueError, ArithmeticError) as error:
        parser.exit(2, f'Request rejected: {error}\n')
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
