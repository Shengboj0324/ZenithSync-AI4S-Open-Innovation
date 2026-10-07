"""Initial generation -> measured intervening pool -> untouched final outcomes."""
from pathlib import Path
import json
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from zenithsync.yakavets import load_concurrent
from zenithsync.linear_replay import replay


def main():
    out=ROOT/'artifacts/linear_policy_v1'
    out.mkdir(parents=True,exist_ok=True)
    tables,audits=load_concurrent(ROOT)
    rows,split_records=[],[]
    for context,frame in tables.items():
        first,last=frame.gen.min(),frame.gen.max()
        initial=frame[frame.gen==first]
        pool=frame[(frame.gen>first)&(frame.gen<last)]
        audit=frame[frame.gen==last]
        features=audits[context]['features']
        split_records.append({'context':context,'initial_rows':initial.source_row.tolist(),
                              'pool_rows':pool.source_row.tolist(),'audit_rows':audit.source_row.tolist(),
                              'audit_generation':int(last)})
        for policy in ['random','space_filling','ridge_variance']:
            for seed in (range(50) if policy=='random' else [0]):
                trace=replay(initial[features].to_numpy(),initial.cv_exp.to_numpy(),
                             pool[features].to_numpy(),pool.cv_exp.to_numpy(),
                             audit[features].to_numpy(),audit.cv_exp.to_numpy(),policy,seed,max_budget=15)
                rows.extend({'context':context,'policy':policy,'seed':seed,**step} for step in trace)
    table=pd.DataFrame(rows)
    table.to_json(out/'traces.jsonl',orient='records',lines=True,double_precision=15)
    summary=table.groupby(['context','policy','budget']).agg(mean_rmse=('rmse','mean'),
             mean_mae=('mae','mean'),seed_min_rmse=('rmse','min'),seed_max_rmse=('rmse','max')).reset_index()
    summary.to_csv(out/'summary.csv',index=False)
    (out/'splits.json').write_text(json.dumps(split_records,indent=2)+'\n')
    (out/'protocol.json').write_text(json.dumps({
        'status':'exploratory; final generations were examined in earlier model-comparison work',
        'audit_isolation':'audit outcomes are never passed to acquisition or fitting in this replay',
        'pool':'only actually recorded intermediate-generation experiments',
        'initial_cost':'7 FAC or 10 OLA-IBET rows, additional to displayed budget',
        'unit_cost':'one revealed aggregate record; not a validated chip or laboratory cost',
        'support':'historically measured candidates; no convex-hull restriction in this retrospective experiment',
        'workflow_difference':'the interactive workflow excludes unsupported candidates; this evaluates acquisition on recorded feasible support',
        'noise_sd':.1,'ridge_penalty':.1,'target_grid':'intermediate measured pool',
        'independent_biological_replications':False},indent=2)+'\n')
    print(summary[summary.budget.isin([0,5,10,15])].to_string(index=False))


if __name__=='__main__':main()
