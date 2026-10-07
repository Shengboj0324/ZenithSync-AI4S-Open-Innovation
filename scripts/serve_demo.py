"""Loopback-only, stateless research demo. No uploaded data is written to disk."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from zenithsync.well_workflow import plan_wells
from plan_wells import reject_constant, unique_object

FILES = {'/': ('demo/index.html', 'text/html; charset=utf-8'),
         '/app.js': ('demo/app.js', 'text/javascript; charset=utf-8'),
         '/styles.css': ('demo/styles.css', 'text/css; charset=utf-8'),
         '/example.json': ('examples/farin_wells_request.json', 'application/json'),
         '/provenance.json': ('examples/farin_wells_provenance.json', 'application/json')}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def error(self, status, message):
        self.respond(status, json.dumps({'error': message}).encode())

    def allowed_host(self):
        port = self.server.server_port
        return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

    def do_GET(self):
        if not self.allowed_host():
            return self.error(403, 'Use the local loopback address')
        if self.path == '/evidence.json':
            confirmation = json.loads((ROOT/'artifacts/kryeziu_confirmation_v1/confirmation.json').read_text())
            verification = json.loads((ROOT/'artifacts/kryeziu_confirmation_v1/verification.json').read_text())
            return self.respond(200, json.dumps({'confirmation': confirmation, 'verification': verification}).encode())
        if self.path not in FILES:
            return self.error(404, 'Resource not found')
        name, content_type = FILES[self.path]
        self.respond(200, (ROOT/name).read_bytes(), content_type)

    def do_POST(self):
        if not self.allowed_host():
            return self.error(403, 'Use the local loopback address')
        allowed_origins = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}
        if self.headers.get('Origin') not in {None, *allowed_origins}:
            return self.error(403, 'Cross-origin requests are not accepted')
        if self.path != '/api/plan':
            return self.error(404, 'Resource not found')
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            return self.error(415, 'Send an application/json request')
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.error(400, 'Invalid request length')
        if not 0 < length <= 1048576 or self.headers.get('Transfer-Encoding'):
            return self.error(413, 'Use a nonempty JSON body of at most one MiB')
        try:
            request = json.loads(self.rfile.read(length).decode('utf-8'),
                                 parse_constant=reject_constant, object_pairs_hook=unique_object)
            if self.headers.get('X-Additional-Wells') is not None:
                if not isinstance(request, dict):
                    raise ValueError('Request must be a JSON object')
                request['additional_wells'] = int(self.headers['X-Additional-Wells'])
            result = plan_wells(request)
        except (ValueError, ArithmeticError, UnicodeDecodeError) as error:
            return self.error(422, str(error))
        self.respond(200, json.dumps(result, allow_nan=False).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Research demo: http://127.0.0.1:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
