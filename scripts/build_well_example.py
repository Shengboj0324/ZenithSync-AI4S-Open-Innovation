"""First lexicographically admitted Farin curve; reveal exactly three source wells."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.farin import load_farin, SOURCE_HASH
from zenithsync.farin_replay import partition_curves
from zenithsync.well_workflow import plan_wells


def main():
    curves, _ = partition_curves(load_farin(ROOT/'data/raw/farin/Drug_sensitivity_all_lines.txt'))
    curve = curves[0]
    pool = curve.pool
    initial = pool[pool.replicate_label.eq('1') & pool.concentration.isin([0., curve.doses[1], curve.doses[-1]])]
    initial_ids = set(initial.source_row)
    reference = int(initial.loc[initial.is_control, 'source_row'].iloc[0])
    request = {'schema_version': 1, 'assay_context': 'research_single_agent_organoid',
               'experiment_id': curve.curve_id, 'plate_id': 'unreported-source-plate',
               'concentration_unit': str(pool.concentration_unit.iloc[0]),
               'reference_control_id': f'farin:{reference}', 'future_control_count': 1,
               'additional_wells': 3,
               'wells': [{'id': f'farin:{int(row.source_row)}',
                          'kind': 'vehicle_control' if row.is_control else 'treatment',
                          'dose': float(row.concentration),
                          'signal': float(row.raw_luminescence) if row.source_row in initial_ids else None}
                         for row in pool.itertuples()]}
    target = ROOT/'examples/farin_wells_request.json'
    target.write_text(json.dumps(request, indent=2)+'\n')
    provenance = {'source_doi': '10.17632/fypp6xhkjy.1', 'source_sha256': SOURCE_HASH,
                  'source_url': 'https://data.mendeley.com/datasets/fypp6xhkjy/1', 'license': 'CC BY 4.0',
                  'request_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'source_curve': curve.curve_id, 'selection': 'first lexicographic complete admitted development curve',
                  'observed_source_rows': sorted(initial_ids),
                  'plate_limitation': 'No plate ID exists in the source. The example is a within-curve modeling demonstration, not a verified physical-plate instruction.',
                  'outcomes_in_request': 'Only the three declared observed raw signals; all candidates are null.'}
    (ROOT/'examples/farin_wells_provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    output = ROOT/'artifacts/well_workflow_v1'
    output.mkdir(parents=True, exist_ok=True)
    result = plan_wells(request)
    (output/'example-response.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'request': str(target.relative_to(ROOT)), 'observed': result['observed_wells'],
                      'selected_wells': result['selected_wells'], 'variance_reduction': result['variance_reduction'],
                      'optimization': result['optimization']}, indent=2))


if __name__ == '__main__':
    main()
