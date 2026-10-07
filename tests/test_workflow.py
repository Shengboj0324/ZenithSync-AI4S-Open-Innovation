from copy import deepcopy
import numpy as np
import pytest
from zenithsync.linear import ridge_posterior
from zenithsync.workflow import run_request


def request():
    return {"context": "yakavets_ola_ibet_concurrent", "feature_names": ["conc0", "conc1"],
            "feature_unit": "author_normalized_concentration", "endpoint": "cv_exp",
            "observations": [{"id": str(i), "x": x, "y": y} for i, (x, y) in enumerate(
                [([.2,.2],.9), ([.8,.2],.6), ([.2,.8],.5), ([.8,.8],.2)])],
            "candidates": [{"id":"inside","x":[.5,.5],"cost":1.},
                           {"id":"outside","x":[.95,.95],"cost":1.}],
            "threshold":.5,"false_positive_cost":1.,"false_negative_cost":1.,
            "abstention_cost":.1,"noise_sd":.1,"ridge_penalty":.1}


def test_ridge_mean_matches_direct_regularized_least_squares():
    x=np.array([[0.,0.],[1.,0.],[0.,1.]])
    y=np.array([1.,.7,.5])
    mean,cov=ridge_posterior(x,y,x)
    a=np.column_stack([np.ones(3),x])
    expected=a@np.linalg.solve(a.T@a+np.diag([0.,.1,.1]),a.T@y)
    np.testing.assert_allclose(mean,expected)
    assert np.linalg.eigvalsh(cov).min()>0


def test_ridge_duplicate_measurement_reduces_variance():
    _,a=ridge_posterior([[0.,0.]],[1.],[[0.,0.]])
    _,b=ridge_posterior([[0.,0.],[0.,0.]],[1.,1.],[[0.,0.]])
    np.testing.assert_allclose(a,[[.01]])
    np.testing.assert_allclose(b,[[.005]])


def test_workflow_support_gate_and_provenance():
    output=run_request(request())
    assert output['candidates'][1]['status']=='abstain'
    assert output['candidates'][1]['prediction'] is None
    assert output['next_measurement']=='inside'
    assert len(output['request_sha256'])==64
    assert output['human_review_required'] and output['research_only']


def test_candidate_outcome_is_rejected_not_used():
    data=request();data['candidates'][0]['y']=.2
    with pytest.raises(ValueError,match='requires exactly'):
        run_request(data)


@pytest.mark.parametrize('field,value',[('feature_unit','micromolar'),('endpoint','toxicity'),('context','unknown'),('noise_sd',0)])
def test_unsupported_request_rejected(field,value):
    data=request();data[field]=value
    with pytest.raises(ValueError):run_request(data)


def test_abstention_cost_changes_decision_not_prediction():
    data=request();data['threshold']=.55
    first=run_request(data)
    data['abstention_cost']=1e-10
    second=run_request(data)
    assert second['candidates'][0]['status']=='abstain'
    assert first['candidates'][0]['prediction']==second['candidates'][0]['prediction']


def test_acquisition_cost_changes_ranking():
    data=request()
    data['candidates']=[{'id':'a','x':[.5,.5],'cost':1.},{'id':'b','x':[.5,.5],'cost':2.}]
    first=run_request(data)
    assert first['next_measurement']=='a'
    data['candidates'][0]['cost']=3.
    assert run_request(data)['next_measurement']=='b'


def test_request_is_not_mutated():
    data=request();before=deepcopy(data)
    run_request(data)
    assert data==before


def test_cli_rejection_replaces_stale_success(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path
    root=Path(__file__).parents[1]
    input_path=tmp_path/'request.json'
    output_path=tmp_path/'response.json'
    input_path.write_text(json.dumps({'invalid':'request'}))
    output_path.write_text(json.dumps({'status':'old_success'}))
    result=subprocess.run([sys.executable,str(root/'scripts/research_workflow.py'),str(input_path),
                           '--output',str(output_path)],capture_output=True,text=True)
    assert result.returncode==2
    assert json.loads(output_path.read_text())['status']=='rejected'
