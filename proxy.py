#!/usr/bin/env python3
"""FTP-Flix local server: serves index.html AND acts as a CORS proxy.
Run:  python proxy.py      then open http://localhost:8787  (phone: http://PC-IP:8787 on the same Wi-Fi)
Needs only Python 3, no installs. Videos play directly from the servers; only listings/subtitles go through here."""
import os, sys, socket, urllib.request, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8787))
HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"", extra={"Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "GET,HEAD,OPTIONS"})

    do_HEAD = lambda self: self.do_GET()

    def do_GET(self):
        q = urllib.parse.urlparse(self.path)
        if q.path in ("/", "/index.html") and "url" not in urllib.parse.parse_qs(q.query):
            try:
                html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
            except OSError:
                return self._send(404, b"index.html must be in the same folder as proxy.py")
            # make the app use this server as its CORS proxy by default
            html = html.replace("proxy: LS.get('proxy', '')", "proxy: LS.get('proxy', '/?url={url}')")
            return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
        target = urllib.parse.parse_qs(q.query).get("url", [""])[0]
        if not target.startswith(("http://", "https://")):
            return self._send(400, b"use /?url=https://...")
        try:
            req = urllib.request.Request(target, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
                self._send(r.status, body, r.headers.get("Content-Type", "application/octet-stream"))
        except urllib.error.HTTPError as e:
            self._send(e.code, e.read() or str(e).encode())
        except Exception as e:
            self._send(502, ("proxy error: %s" % e).encode())

    def log_message(self, *a):
        pass

def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close(); return ip
    except Exception:
        return "PC-IP"

if __name__ == "__main__":
    print("FTP-Flix running.\n  This PC : http://localhost:%d\n  Phone   : http://%s:%d  (same Wi-Fi)\nCtrl+C to stop." % (PORT, lan_ip(), PORT))
    try:
        ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
