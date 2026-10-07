"""Hash-pinned source acquisition and outcome-blinded design projection.

The downloaded workbook contains outcomes. This script never exports, summarizes
or prints signal/viability cells; only explicitly allowlisted design fields pass.
Run with the bundled spreadsheet Python runtime for this read-only extraction.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ['sample_id', 'sample_id_drums', 'run_id', 'assay_no', 'library_id',
          'compound_name', 'compound_fimm', 'compound_drums', 'compound_type',
          'concentration', 'concentration_unit', 'drow', 'dcol', 'plate']


def acquire(source, path):
    """Write only checksum-verified provider bytes to an explicit local path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        payload = path.read_bytes()
    else:
        with urlopen(Request(source['download_url'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as response:
            payload = response.read(source['size']+1)
    if len(payload) != source['size'] or hashlib.sha256(payload).hexdigest() != source['sha256']:
        raise ValueError('Public workbook failed pinned byte/hash verification')
    if not path.exists():
        temporary = path.with_suffix('.download')
        temporary.write_bytes(payload)
        temporary.replace(path)


def main():
    manifest = json.loads((ROOT/'data/kryeziu_candidate_metadata.json').read_text())
    source = next(f for f in manifest['files'] if f['filename'] == 'Data S4.xlsx')
    path = ROOT/'data/raw/kryeziu/Data S4.xlsx'
    acquire(source, path)
    output = ROOT/'artifacts/kryeziu_design_v1'
    output.mkdir(parents=True, exist_ok=True)
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet_records = []
    try:
        for sheet in workbook:
            iterator = sheet.iter_rows(values_only=True)
            header = next(iterator)
            if len(header) != len(set(header)) or not set(DESIGN+['signal', 'viability']).issubset(header):
                raise ValueError('Unexpected worksheet schema; no data rows exposed')
            indices = [header.index(field) for field in DESIGN]
            count = 0
            # Source row IDs remain stable across later outcome evaluation.
            target = output/f'design-{len(sheet_records)+1}.csv'
            with target.open('w', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(['source_sheet', 'source_row', *DESIGN])
                for row_number, row in enumerate(iterator, 2):
                    values = [row[index] for index in indices]
                    if all(value is None for value in values):
                        continue
                    writer.writerow([sheet.title, row_number, *values])
                    count += 1
            sheet_records.append({'sheet': sheet.title, 'rows': count, 'design_file': target.name,
                                  'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    finally:
        workbook.close()
    record = {'created_utc': datetime.now(timezone.utc).isoformat(), 'dataset_doi': manifest['dataset_doi'],
              'source_sha256': source['sha256'], 'source_file_downloaded': True,
              'outcome_values_exposed_or_analyzed': False, 'fields_exported': DESIGN,
              'sheets': sheet_records, 'status': 'design admission only; no model confirmation'}
    record_path = output/'extraction.json'
    if record_path.exists():
        previous = json.loads(record_path.read_text())
        content = lambda item: {key: value for key, value in item.items() if key != 'created_utc'}
        if content(previous) != content(record):
            raise ValueError('Existing design extraction differs; preserve it for review')
        # Preserve the original acquisition timestamp and frozen record hash.
        record = previous
    else:
        record_path.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
