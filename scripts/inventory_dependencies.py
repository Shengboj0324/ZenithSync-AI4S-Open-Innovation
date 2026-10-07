"""Inventory installed pinned dependency license metadata without interpreting it."""
from hashlib import sha256
from importlib.metadata import distribution
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    records=[]
    for line in (ROOT/'requirements-lock.txt').read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        name,version=line.strip().split('==')
        dist=distribution(name)
        if dist.version!=version:
            raise ValueError(f'Installed version differs for {name}')
        files=[]
        for item in dist.files or []:
            if any(part.lower().startswith(('license','copying','notice')) for part in item.parts):
                path=Path(dist.locate_file(item))
                if path.is_file():
                    payload=path.read_bytes()
                    files.append({'distribution_path':str(item),'bytes':len(payload),'sha256':sha256(payload).hexdigest()})
        records.append({'name':name,'version':version,
                        'license_expression':dist.metadata.get('License-Expression'),
                        'license_metadata':dist.metadata.get('License'),
                        'classifiers':[v for v in dist.metadata.get_all('Classifier',[]) if v.startswith('License ::')],
                        'license_notice_files':files})
    out=ROOT/'artifacts/release_audit_v1/dependency-inventory.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'scope':'Installed packages pinned in requirements-lock.txt; environments/binaries not redistributed',
        'interpretation':'Metadata inventory, not a license compatibility determination; media-building tools are outside this numerical environment',
        'lock_sha256':sha256((ROOT/'requirements-lock.txt').read_bytes()).hexdigest(),'packages':records},indent=2)+'\n')
    print(json.dumps({'pinned_packages_verified':len(records),'license_files_found':sum(len(r['license_notice_files']) for r in records)}))


if __name__=='__main__':main()
