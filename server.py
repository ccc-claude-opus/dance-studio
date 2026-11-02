#!/usr/bin/env python3
"""Optional local server: serves web/ and stores camera recordings (video + skeleton) on disk.

The page works without it (e.g. on GitHub Pages); with it, recordings can be saved and reopened.

    python3 server.py                 # http://localhost:8000
    python3 server.py --port 9000 --data /path/to/recordings

Recordings live in <data>/<id>/meta.json, skeleton.json and video.<ext>. Only Python's standard library is used.
"""
import argparse, json, os, re, secrets, shutil, time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

ROOT = os.path.dirname(os.path.abspath(__file__))
ID_RE = re.compile(r'^[A-Za-z0-9_-]{1,64}$')
VIDEO_EXT = {'video/webm': 'webm', 'video/mp4': 'mp4', 'video/quicktime': 'mov'}
MAX_JSON = 64 * 1024 * 1024
MAX_VIDEO = 1024 * 1024 * 1024
META_KEYS = ('name', 'created', 'duration', 'aspect', 'people', 'mirror', 'videoType')


class Handler(SimpleHTTPRequestHandler):
    data_dir = None

    # ---------- helpers ----------
    def send_json(self, obj, status=HTTPStatus.OK):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def fail(self, status, msg):
        self.send_json({'error': msg}, status)

    def read_body(self, limit):
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0 or n > limit:
            return None
        return self.rfile.read(n)

    def rec_dir(self, rid):
        return os.path.join(self.data_dir, rid) if ID_RE.match(rid or '') else None

    def api_path(self):
        """('recordings', id, 'video') style parts after /api/, or None for normal files."""
        path = unquote(urlparse(self.path).path)
        i = path.find('/api/')
        if i < 0:
            return None
        return [p for p in path[i + 5:].split('/') if p]

    @staticmethod
    def load_meta(d):
        with open(os.path.join(d, 'meta.json'), encoding='utf-8') as f:
            return json.load(f)

    # ---------- routes ----------
    def do_GET(self):
        parts = self.api_path()
        if parts is None:
            return super().do_GET()
        if parts == ['ping']:
            return self.send_json({'ok': True, 'app': 'dance-studio'})
        if parts == ['recordings']:
            out = []
            for rid in sorted(os.listdir(self.data_dir), reverse=True):
                d = self.rec_dir(rid)
                if d and os.path.isfile(os.path.join(d, 'meta.json')):
                    try:
                        out.append({'id': rid, **self.load_meta(d)})
                    except (OSError, ValueError):
                        pass
            return self.send_json(out)
        if len(parts) in (2, 3) and parts[0] == 'recordings':
            d = self.rec_dir(parts[1])
            if not d or not os.path.isdir(d):
                return self.fail(HTTPStatus.NOT_FOUND, 'not found')
            if len(parts) == 2:
                meta = self.load_meta(d)
                with open(os.path.join(d, 'skeleton.json'), encoding='utf-8') as f:
                    meta['samples'] = json.load(f)
                return self.send_json({'id': parts[1], **meta})
            if parts[2] == 'video':
                return self.send_video(d)
        self.fail(HTTPStatus.NOT_FOUND, 'not found')

    def send_video(self, d):
        """Serve the video with HTTP Range support so the browser can seek."""
        meta = self.load_meta(d)
        path = os.path.join(d, 'video.' + VIDEO_EXT.get(meta.get('videoType'), 'webm'))
        if not os.path.isfile(path):
            return self.fail(HTTPStatus.NOT_FOUND, 'no video')
        size = os.path.getsize(path)
        start, end = 0, size - 1
        m = re.match(r'bytes=(\d*)-(\d*)', self.headers.get('Range') or '')
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            if start > end:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header('Content-Range', f'bytes */{size}')
                self.end_headers()
                return
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        else:
            self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', meta.get('videoType') or 'video/webm')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        with open(path, 'rb') as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(left, 1 << 16))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def do_POST(self):
        if self.api_path() != ['recordings']:
            return self.fail(HTTPStatus.NOT_FOUND, 'not found')
        raw = self.read_body(MAX_JSON)
        try:
            rec = json.loads(raw or b'')
            samples = rec['samples']
            assert isinstance(samples, list)
        except (ValueError, KeyError, AssertionError):
            return self.fail(HTTPStatus.BAD_REQUEST, 'bad recording')
        rid = time.strftime('%Y%m%d-%H%M%S') + '-' + secrets.token_hex(3)
        d = os.path.join(self.data_dir, rid)
        os.makedirs(d)
        meta = {k: rec.get(k) for k in META_KEYS}
        meta['name'] = str(meta.get('name') or rid)[:80]
        with open(os.path.join(d, 'skeleton.json'), 'w', encoding='utf-8') as f:
            json.dump(samples, f, separators=(',', ':'))
        with open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        self.send_json({'id': rid}, HTTPStatus.CREATED)

    def do_PUT(self):
        parts = self.api_path()
        if not parts or len(parts) != 3 or parts[0] != 'recordings' or parts[2] != 'video':
            return self.fail(HTTPStatus.NOT_FOUND, 'not found')
        d = self.rec_dir(parts[1])
        if not d or not os.path.isdir(d):
            return self.fail(HTTPStatus.NOT_FOUND, 'not found')
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0 or n > MAX_VIDEO:
            return self.fail(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, 'bad size')
        meta = self.load_meta(d)
        ctype = (self.headers.get('Content-Type') or meta.get('videoType') or 'video/webm').split(';')[0]
        meta['videoType'] = ctype if ctype in VIDEO_EXT else 'video/webm'
        path = os.path.join(d, 'video.' + VIDEO_EXT[meta['videoType']])
        with open(path, 'wb') as f:
            left = n
            while left > 0:
                chunk = self.rfile.read(min(left, 1 << 16))
                if not chunk:
                    break
                f.write(chunk)
                left -= len(chunk)
        meta['size'] = os.path.getsize(path)
        with open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        self.send_json({'ok': True})

    def do_PATCH(self):
        parts = self.api_path()
        d = self.rec_dir(parts[1]) if parts and len(parts) == 2 and parts[0] == 'recordings' else None
        if not d or not os.path.isdir(d):
            return self.fail(HTTPStatus.NOT_FOUND, 'not found')
        try:
            name = str(json.loads(self.read_body(64 * 1024) or b'')['name']).strip()[:80]
        except (ValueError, KeyError, TypeError):
            return self.fail(HTTPStatus.BAD_REQUEST, 'bad name')
        meta = self.load_meta(d)
        meta['name'] = name or meta.get('name')
        with open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        self.send_json({'ok': True})

    def do_DELETE(self):
        parts = self.api_path()
        d = self.rec_dir(parts[1]) if parts and len(parts) == 2 and parts[0] == 'recordings' else None
        if not d or not os.path.isdir(d):
            return self.fail(HTTPStatus.NOT_FOUND, 'not found')
        shutil.rmtree(d)
        self.send_json({'ok': True})


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--port', type=int, default=8000)
    ap.add_argument('--host', default='127.0.0.1', help='use 0.0.0.0 to reach it from a phone on the same network')
    ap.add_argument('--data', default=os.path.join(ROOT, 'recordings'), help='where recordings are stored')
    a = ap.parse_args()
    os.makedirs(a.data, exist_ok=True)
    Handler.data_dir = os.path.abspath(a.data)
    Handler.extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.mjs': 'text/javascript', '.wasm': 'application/wasm'}

    def handler(*args, **kw):
        return Handler(*args, directory=os.path.join(ROOT, 'web'), **kw)

    srv = ThreadingHTTPServer((a.host, a.port), handler)
    print(f'Dance studio: http://{"localhost" if a.host in ("127.0.0.1", "0.0.0.0") else a.host}:{a.port}/  (recordings in {Handler.data_dir})')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
