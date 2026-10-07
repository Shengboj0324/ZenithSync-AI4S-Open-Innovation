"""Evaluate conditional ridge uncertainty on later logged generations.

Observed aggregate responses are the interval/event targets. These diagnostics
do not imply latent-response calibration or independent biological coverage.
"""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from zenithsync.yakavets import load_concurrent
from zenithsync.linear import ridge_posterior


def main():
    out=ROOT/'artifacts/uncertainty_audit_v1'
    out.mkdir(parents=True,exist_ok=True)
    tables,audits=load_concurrent(ROOT)
    rows=[]
    for context,frame in tables.items():
        features=audits[context]['features']
        for held in sorted(frame.gen.unique())[1:]:
            train,test=frame[frame.gen<held],frame[frame.gen==held]
            mean,cov=ridge_posterior(train[features].to_numpy(),train.cv_exp.to_numpy(),test[features].to_numpy())
            sd=np.sqrt(np.maximum(np.diag(cov),0)+.01)
            probability=ndtr((.5-mean)/sd)
            reference_probability=float(np.mean(train.cv_exp.to_numpy()<.5))
            low,high=mean-ndtri(.95)*sd,mean+ndtri(.95)*sd
            for index,record in enumerate(test.itertuples()):
                observed=record.cv_exp
                rows.append({'context':context,'generation':int(held),'source_row':record.source_row,
                             'observed':observed,'mean':float(mean[index]),'observation_sd':float(sd[index]),
                             'lower90':float(low[index]),'upper90':float(high[index]),
                             'covered90':bool(low[index]<=observed<=high[index]),
                             'width90':float(high[index]-low[index]),
                             'probability_observed_below_05':float(probability[index]),
                             'observed_below_05':bool(observed<.5),
                             'brier':float((probability[index]-(observed<.5))**2),
                             'training_prevalence_probability':reference_probability,
                             'training_prevalence_brier':float((reference_probability-(observed<.5))**2),
                             'standardized_residual':float((observed-mean[index])/sd[index])})
    table=pd.DataFrame(rows)
    table.to_csv(out/'predictions.csv',index=False)
    per_generation=table.groupby(['context','generation']).agg(n=('observed','size'),
        coverage90=('covered90','mean'),width90=('width90','mean'),brier=('brier','mean'),
        prevalence_brier=('training_prevalence_brier','mean'),
        positives=('observed_below_05','sum')).reset_index()
    per_generation.to_csv(out/'by_generation.csv',index=False)
    summary=per_generation.groupby('context')[['coverage90','width90','brier','prevalence_brier']].mean()
    summary.to_csv(out/'summary.csv')
    selection=[]
    # Diagnostic grid is reported in full; no test-selected operating point.
    for context,group in table.groupby('context'):
        p=group.probability_observed_below_05.to_numpy()
        truth=group.observed_below_05.to_numpy()
        for abstention_cost in (.01,.05,.1,.2,.3,.5):
            risk=np.minimum(p,1-p)
            accepted=risk<abstention_cost
            errors=(p>.5)!=truth
            selection.append({'context':context,'abstention_cost':abstention_cost,
                              'observations':len(group),'accepted':int(accepted.sum()),
                              'coverage_fraction':float(accepted.mean()),
                              'accepted_errors':int(errors[accepted].sum()),
                              'accepted_error_rate':float(errors[accepted].mean()) if accepted.any() else None,
                              'total_realized_loss':float(np.mean(np.where(accepted,errors.astype(float),abstention_cost)))})
    (out/'selective_risk.json').write_text(json.dumps(selection,indent=2,allow_nan=False)+'\n')
    (out/'protocol.json').write_text(json.dumps({
        'evaluation':'each generation predicted from strictly earlier generations',
        'model':'ridge penalty 0.1; fixed noise SD 0.1; no recalibration on evaluated responses',
        'target':'new observed aggregate cv_exp response, not latent biological mean',
        'threshold':.5,'threshold_status':'exploratory; not independently justified',
        'uncertainty_scope':'empirical diagnostics on adaptively collected logged records',
        'independent_biological_coverage_claim':False,'conformal_claim':False,
        'operating_point_selected_from_test':False},indent=2)+'\n')
    print(summary.to_string())
    print(per_generation.to_string(index=False))
    print(pd.DataFrame(selection).to_string(index=False))


if __name__=='__main__':main()
