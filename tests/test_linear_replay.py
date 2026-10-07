import numpy as np
import pytest
from zenithsync.linear_replay import replay


@pytest.mark.parametrize('policy',['random','space_filling','ridge_variance'])
def test_final_audit_outcomes_do_not_change_policy_or_prediction(policy):
    initial=np.array([[0.,0.],[1.,0.],[0.,1.]])
    pool=np.array([[.2,.2],[.3,.8],[.7,.4],[.9,.9]])
    audit=np.array([[.4,.4],[.6,.6]])
    args=(initial,np.array([1.,.7,.5]),pool,np.array([.8,.5,.4,.1]),audit)
    a=replay(*args,np.array([.6,.3]),policy,max_budget=3)
    b=replay(*args,np.array([1e4,-1e4]),policy,max_budget=3)
    for left,right in zip(a,b,strict=True):
        assert left['selected_pool_indices']==right['selected_pool_indices']
        assert left['audit_predictions']==right['audit_predictions']


def test_unrevealed_pool_outcomes_cannot_change_first_choice():
    initial=np.array([[0.,0.],[1.,0.],[0.,1.]])
    pool=np.array([[.2,.2],[.3,.8],[.7,.4],[.9,.9]])
    a=replay(initial,[1.,.7,.5],pool,[.8,.5,.4,.1],[[.5,.5]],[.5],'ridge_variance',max_budget=1)
    b=replay(initial,[1.,.7,.5],pool,[20.,30.,40.,50.],[[.5,.5]],[.5],'ridge_variance',max_budget=1)
    assert a[1]['selected_pool_indices']==b[1]['selected_pool_indices']
