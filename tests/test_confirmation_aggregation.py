import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/kryeziu_confirmation.py'
SPEC = importlib.util.spec_from_file_location('confirmation_runner', SCRIPT)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def test_patient_aggregation_does_not_weight_patients_by_context_count(tmp_path, monkeypatch):
    monkeypatch.setattr(RUNNER, 'OUT', tmp_path)
    rows = []
    # Patient A has three contexts in one sample; B has only one. Their equal
    # patient reference mean is (1+9)/2=5, not (1+1+1+9)/4=3.
    for orientation in ['p1_to_p2', 'p2_to_p1']:
        for patient, contexts, loss in [('A', 3, 1.), ('B', 1, 9.)]:
            for context in range(contexts):
                for method, factor in [('random_joint', 1.), ('exact_joint', .8)]:
                    for budget in range(3, 9):
                        rows.append(dict(orientation=orientation, patient=patient, sample_id=patient,
                                         context=patient+str(context), method=method, budget=budget,
                                         full_pool_size=8, mse=loss*factor))
    result = RUNNER.summarize(pd.DataFrame(rows))['orientations']['p1_to_p2']
    assert result['mean_budget_mse']['random_joint'] == pytest.approx(5.)
    assert result['mean_budget_mse']['exact_joint'] == pytest.approx(4.)
    assert result['relative_reduction'] == pytest.approx(.2)
    assert result['efficiency_secondary']['mse_ratio'] == pytest.approx(.8)
    assert result['primary_criteria_met']
