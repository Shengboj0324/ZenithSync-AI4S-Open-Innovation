"""Write a repeatable source/identity/exclusion audit for the development cohort."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.farin import load_farin, profile_farin


def main():
    rows = load_farin(ROOT/'data/raw/farin/Drug_sensitivity_all_lines.txt')
    profile = profile_farin(rows)
    output = ROOT/'artifacts/farin_v1'
    output.mkdir(parents=True, exist_ok=True)
    rows.to_csv(output/'source_rows.csv', index=False)
    (output/'quality.json').write_text(json.dumps(profile, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key: value for key, value in profile.items()
                      if key != 'curve_inventory'}, indent=2))


if __name__ == '__main__':
    main()
