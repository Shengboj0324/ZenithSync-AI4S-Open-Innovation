import pandas as pd
import pytest

from zenithsync.kryeziu_design import canonical_dose, paired_inventory


def fixture():
    rows = []
    for plate in ['p1', 'p2']:
        for i, dose in enumerate(['1', '10', '100', '1000', '0', 'NA']):
            control = i >= 4
            rows.append({'sample_id': 'sample', 'run_id': 'run', 'library_id': 'library',
                         'plate': plate, 'drow': 'A', 'dcol': str(i+1),
                         'source_row': str(len(rows)+2), 'compound_name': 'DMSO' if control else 'drug',
                         'compound_type': 'control_negative' if control else 'single',
                         'concentration': dose, 'concentration_unit': '' if control else 'nM'})
    return pd.DataFrame(rows)


def test_pairs_physical_plates_without_inventing_control_concentrations():
    decisions, cohort = paired_inventory(fixture())
    assert decisions.admitted_by_design.all() and len(cohort) == 1
    row = cohort[0]
    pool = row['pool_treatment_source_rows']+row['pool_control_source_rows']
    audit = row['audit_treatment_source_rows']+row['audit_control_source_rows']
    assert len(pool) == len(audit) == 6 and set(pool).isdisjoint(audit)


@pytest.mark.parametrize('defect', ['unit', 'missing_plate', 'different_doses', 'missing_control'])
def test_rejects_structurally_unusable_contexts(defect):
    frame = fixture()
    if defect == 'unit':
        frame.loc[0, 'concentration_unit'] = 'NA'
    elif defect == 'missing_plate':
        frame = frame[frame.plate.eq('p1')]
    elif defect == 'different_doses':
        frame.loc[0, 'concentration'] = '2'
    else:
        frame = frame.iloc[:-1]
    decisions, cohort = paired_inventory(frame)
    assert not cohort and not decisions.admitted_by_design.any()
    assert decisions.reason.str.len().gt(0).all()


def test_control_and_treatment_cannot_reuse_physical_well():
    frame = fixture()
    frame.loc[4, 'dcol'] = '1'
    with pytest.raises(ValueError, match='physical well'):
        paired_inventory(frame)


def test_matching_numeric_dose_spelling_does_not_change_support():
    frame = fixture()
    frame.loc[0, 'concentration'] = '1.000'
    assert paired_inventory(frame)[0].admitted_by_design.all()
    for invalid in ['0', '-1', 'NaN', 'Infinity', 'NA']:
        with pytest.raises(ValueError):
            canonical_dose(invalid)
