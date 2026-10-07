"""Build an actual-data generation-zero -> generation-one research request."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from zenithsync.yakavets import load_concurrent


def main():
    tables,audits=load_concurrent(ROOT)
    context='OLA-IBET'
    frame=tables[context]
    features=audits[context]['features']
    observations=[]
    candidates=[]
    for _,row in frame.iterrows():
        identity=f"source-row-{int(row.source_row)}"
        if row.gen==0:
            observations.append({'id':identity,'x':row[features].tolist(),'y':float(row.cv_exp)})
        elif row.gen==1:
            candidates.append({'id':identity,'x':row[features].tolist(),'cost':1.})
    request={'context':'yakavets_ola_ibet_concurrent','feature_names':features,
             'feature_unit':'author_normalized_concentration','endpoint':'cv_exp',
             'observations':observations,'candidates':candidates,'threshold':.5,
             'false_positive_cost':1.,'false_negative_cost':1.,'abstention_cost':.1,
             'noise_sd':.1,'ridge_penalty':.1}
    out=ROOT/'examples';out.mkdir(exist_ok=True)
    (out/'ola_ibet_request.json').write_text(json.dumps(request,indent=2)+'\n')
    print('Saved 10 observed responses and 10 candidate inputs; candidate outcomes omitted.')


if __name__=='__main__':main()
