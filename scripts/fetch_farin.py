"""Download and verify the pinned public development table; no authentication."""
from pathlib import Path
import hashlib
import json
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'data/farin_manifest.json').read_text())
    destination = ROOT/'data/raw/farin'/manifest['filename']
    if destination.exists():
        payload = destination.read_bytes()
    else:
        # The public endpoint rejects Python's default user agent with HTTP 403.
        request = Request(manifest['download_url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(request, timeout=60) as response:
            payload = response.read(manifest['bytes']+1)
    digest = hashlib.sha256(payload).hexdigest()
    if len(payload) != manifest['bytes'] or digest != manifest['sha256']:
        raise ValueError('Source size/hash differs from the pinned provider file')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        temporary = destination.with_suffix('.download')
        temporary.write_bytes(payload)
        temporary.replace(destination)
    print(json.dumps({'file': str(destination.relative_to(ROOT)), 'bytes': len(payload),
                      'sha256': digest, 'role': manifest['role']}, sort_keys=True))


if __name__ == '__main__':
    main()
