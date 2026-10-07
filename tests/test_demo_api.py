from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import sys
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
SPEC = importlib.util.spec_from_file_location('demo_server', ROOT/'scripts/serve_demo.py')
SERVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SERVER)


@pytest.fixture(scope='module')
def url():
    server = ThreadingHTTPServer(('127.0.0.1', 0), SERVER.Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_http_plan_and_budget_override_match_request_contract(url):
    body = (ROOT/'examples/farin_wells_request.json').read_bytes()
    request = Request(url+'/api/plan', data=body,
                      headers={'Content-Type':'application/json', 'X-Additional-Wells':'0'})
    with urlopen(request, timeout=10) as response:
        result = json.load(response)
        assert response.headers['Cache-Control'] == 'no-store'
    assert result['additional_wells'] == 0 and result['selected_wells'] == []


@pytest.mark.parametrize('path,body,headers,status', [
    ('/api/plan', b'{"x":1,"x":2}', {'Content-Type':'application/json'}, 422),
    ('/api/plan', b'{}', {'Content-Type':'text/plain'}, 415),
    ('/api/plan', b'{}', {'Content-Type':'application/json','Origin':'https://outside.example'}, 403),
    ('/api/plan', b'{}', {'Content-Type':'application/json','Host':'outside.example'}, 403),
    ('/../pyproject.toml', None, {}, 404),
])
def test_rejected_requests_do_not_leak_files_or_silently_normalize_json(url, path, body, headers, status):
    with pytest.raises(HTTPError) as error:
        urlopen(Request(url+path, data=body, headers=headers), timeout=10)
    assert error.value.code == status
    assert 'error' in json.load(error.value)
