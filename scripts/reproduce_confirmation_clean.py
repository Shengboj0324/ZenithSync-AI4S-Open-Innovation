"""Reproduce expanded confirmation in a fresh local environment and raw cache.

Historical freeze records are copied as inputs. Raw source files, projections,
admission decisions, plans and numerical outputs are regenerated. This is a
reproduction of known evidence, never a new unseen-cohort confirmation.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sys.version_info[:2] != (3,13):
        raise RuntimeError('The pinned reproduction requires Python 3.13')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    log=ROOT/'artifacts/logs/second-half'/stamp
    log.mkdir(parents=True)
    fresh=Path(tempfile.mkdtemp(prefix='zenithsync-confirmation-reproduction-'))
    record={'started_utc':stamp,'fresh_directory':str(fresh),'raw_cache_initially_empty':True,
            'meaning':'Reproduction of known results, not a new independent outcome evaluation',
            'commands':[],'comparisons':{},'status':'running'}
    expected=[]
    for folder,names in {
      'artifacts/kryeziu_design_v1':['design-1.csv','patient-map.csv','patient-map.json','admission.csv',
        'patient-admission.csv','paired_source_rows.json','quality.json'],
      'artifacts/kryeziu_confirmation_v1':['preflight.json','results.csv.gz','exclusions.json','confirmation.json',
        'patient-results.csv','verification.json','diagnostics.json','budget-diagnostics.csv','drug-diagnostics.csv',
        'efficiency-budgets.csv','library_id-diagnostics.csv','overall-diagnostics.csv','paired-comparators.csv','patient-diagnostics.csv'],
      'artifacts/farin_v1':['quality.json','source_rows.csv'],
      'artifacts/well_workflow_v1':['example-response.json'],
      'examples':['farin_wells_request.json','farin_wells_provenance.json'],
      'data/raw/kryeziu':['signals-projection.csv']}.items():
        expected.extend(f'{folder}/{name}' for name in names)
    original_hashes={name:digest(ROOT/name) for name in expected}
    try:
        for folder in ['src','scripts','tests','configs','examples','demo']:
            shutil.copytree(ROOT/folder,fresh/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for name in ['requirements-lock.txt','pyproject.toml']:
            shutil.copy2(ROOT/name,fresh/name)
        (fresh/'data').mkdir()
        for p in (ROOT/'data').glob('*.json'):shutil.copy2(p,fresh/'data'/p.name)
        design=fresh/'artifacts/kryeziu_design_v1';design.mkdir(parents=True)
        for name in ['protocol-freeze.json','extraction.json']:
            shutil.copy2(ROOT/'artifacts/kryeziu_design_v1'/name,design/name)
        record['historical_records_copied']=['protocol-freeze.json','extraction.json']
        assert not (fresh/'data/raw').exists()
        def run(label,args):
            started=datetime.now(timezone.utc)
            destination=log/(label+'.txt')
            with destination.open('w') as handle:
                result=subprocess.run(args,cwd=fresh,stdout=handle,stderr=subprocess.STDOUT)
            item={'label':label,'args':args,'exit_code':result.returncode,
                  'seconds':(datetime.now(timezone.utc)-started).total_seconds(),'log':destination.name}
            record['commands'].append(item)
            print(f'{label}: exit {result.returncode}, {item["seconds"]:.1f}s',flush=True)
            if result.returncode:raise RuntimeError(f'{label} failed; inspect {destination}')
        run('create-environment',[sys.executable,'-m','venv',str(fresh/'.venv')])
        py=str(fresh/'.venv/bin/python')
        run('install-pinned',[py,'-m','pip','install','--disable-pip-version-check','-r','requirements-lock.txt'])
        run('tests',[py,'-m','pytest','-q','-W','error'])
        steps=[('fetch-farin','fetch_farin.py'),('audit-farin','audit_farin.py'),
               ('fetch-project-design','inspect_kryeziu_design.py'),('fetch-project-patients','inspect_kryeziu_patient_map.py'),
               ('admission','audit_kryeziu_design.py'),('preflight','kryeziu_confirmation.py'),
               ('project-outcomes','unblind_kryeziu.py')]
        for label,script in steps:run(label,[py,'-W','error','scripts/'+script])
        run('evaluate',[py,'-W','error','scripts/kryeziu_confirmation.py','--evaluate'])
        for label,script in [('verify','audit_kryeziu_confirmation.py'),('diagnostics','summarize_kryeziu_diagnostics.py'),
                             ('example','build_well_example.py')]:
            run(label,[py,'-W','error','scripts/'+script])
        for name,expected_hash in original_hashes.items():
            actual=digest(fresh/name)
            record['comparisons'][name]={'expected_sha256':expected_hash,'actual_sha256':actual,'identical':actual==expected_hash}
        if not all(r['identical'] for r in record['comparisons'].values()):
            raise AssertionError('Reproduction differs from at least one pinned artifact')
        if any(digest(ROOT/name)!=expected_hash for name,expected_hash in original_hashes.items()):
            raise AssertionError('Original scientific artifacts changed during reproduction')
        record['status']='passed'
        record['deterministic_artifacts_identical']=len(expected)
    except BaseException:
        record['status']='failed'
        record['traceback']=traceback.format_exc()
        raise
    finally:
        record['finished_utc']=datetime.now(timezone.utc).isoformat()
        (log/'record.json').write_text(json.dumps(record,indent=2)+'\n')
        print('Reproduction record:',log/'record.json',flush=True)


if __name__=='__main__':main()
