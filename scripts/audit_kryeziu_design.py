"""Design admission only: never opens the outcome-bearing workbook."""
import json
import hashlib
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.kryeziu_design import load_design, paired_inventory


def main():
    output = ROOT/'artifacts/kryeziu_design_v1'
    frame = load_design(output/'design-1.csv', output/'extraction.json')
    decisions, cohort = paired_inventory(frame)
    decisions.to_csv(output/'admission.csv', index=False)
    (output/'paired_source_rows.json').write_text(json.dumps(cohort, indent=2)+'\n')
    admitted = decisions[decisions.admitted_by_design]
    mapping_path = output/'patient-map.csv'
    mapping_record = json.loads(mapping_path.with_suffix('.json').read_text())
    if hashlib.sha256(mapping_path.read_bytes()).hexdigest() != mapping_record['projection_sha256']:
        raise ValueError('Patient identifier projection hash mismatch')
    mapping = pd.read_csv(mapping_path, dtype=str, keep_default_na=False)
    mapping = mapping[mapping.sample_type.eq('PDO')]
    if mapping.sample_id.duplicated().any() or mapping.patient.eq('').any():
        raise ValueError('PDO sample/patient mapping is not unique and complete')
    patient_admission = admitted.merge(mapping[['sample_id', 'patient']], on='sample_id',
                                      how='left', validate='many_to_one')
    patient_admission['patient_mapping_available'] = patient_admission.patient.notna()
    patient_admission.to_csv(output/'patient-admission.csv', index=False)
    verified = patient_admission[patient_admission.patient_mapping_available]
    controls = frame[frame.compound_type.eq('control_negative')]
    report = {'status': 'outcome-blinded design admission; no confirmation result',
              'source_rows': len(frame), 'samples': frame.sample_id.nunique(),
              'runs': frame.run_id.nunique(), 'compound_types': frame.compound_type.value_counts().to_dict(),
              'single_agent_contexts': len(decisions), 'admitted_contexts': len(admitted),
              'admitted_samples': admitted.sample_id.nunique(), 'admitted_runs': admitted.run_id.nunique(),
              'admitted_drugs': admitted.compound_name.nunique(),
              'paired_dose_counts': admitted.p1_doses.value_counts().to_dict(),
              'rejection_reasons': decisions.loc[~decisions.admitted_by_design, 'reason'].value_counts().to_dict(),
              'control_annotation_counts': controls.groupby(['concentration', 'concentration_unit']).size().reset_index(name='rows').to_dict('records'),
              'patient_mapped_contexts': len(verified), 'patient_mapped_samples': verified.sample_id.nunique(),
              'source_patient_ids': verified.patient.nunique(),
              'unmapped_samples': patient_admission.loc[~patient_admission.patient_mapping_available, 'sample_id'].nunique(),
              'patient_mapping_verified': 'PDO subset linked to explicit Data S1 patient field',
              'outcomes_exposed_or_analyzed': False,
              'proposed_orientation': 'p1 pool and p2 audit; orientation sensitivity to be prespecified',
              'remaining_admission': ['nonpositive or invalid outcomes after protocol freeze',
                                      'background normalization endpoint and control cost assumptions']}
    (output/'quality.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
