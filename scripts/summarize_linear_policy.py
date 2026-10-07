"""Descriptive full-budget comparison; uncertainty is algorithmic Monte Carlo only."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'artifacts/linear_policy_v1'
    traces=pd.read_json(out/'traces.jsonl',lines=True)
    curves=[]
    for (context,policy,seed),group in traces.groupby(['context','policy','seed']):
        group=group.sort_values('budget')
        budget=group.budget.to_numpy()
        if len(np.unique(budget))!=len(budget) or not np.array_equal(budget,np.arange(16)):
            raise ValueError('Expected one evaluation at each budget 0 through 15')
        area=float(np.trapezoid(group.rmse.to_numpy(),budget)/(budget[-1]-budget[0]))
        curves.append({'context':context,'policy':policy,'seed':int(seed),'budget_average_rmse':area})
    curve_table=pd.DataFrame(curves)
    curve_table.to_csv(out/'full_budget_metrics.csv',index=False)
    comparisons=[]
    for context,group in curve_table.groupby('context'):
        random=group[group.policy=='random'].budget_average_rmse.to_numpy()
        sem=float(random.std(ddof=1)/np.sqrt(len(random)))
        half=float(t.ppf(.975,len(random)-1)*sem)
        result={'context':context,'random_mean':float(random.mean()),
                'random_mean_mc_interval95':[float(random.mean()-half),float(random.mean()+half)],
                'interval_target':'Monte Carlo mean over random policy seeds conditional on this fixed dataset',
                'not_a_biological_confidence_interval':True,'random_seed_count':len(random),'policies':[]}
        for row in group[group.policy!='random'].itertuples():
            result['policies'].append({'policy':row.policy,'budget_average_rmse':row.budget_average_rmse,
                                       'difference_from_random_mean':float(row.budget_average_rmse-random.mean()),
                                       'fraction_random_seeds_with_lower_error':float(np.mean(random<row.budget_average_rmse))})
        comparisons.append(result)
    (out/'full_budget_comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    print(json.dumps(comparisons,indent=2))


if __name__=='__main__':main()
