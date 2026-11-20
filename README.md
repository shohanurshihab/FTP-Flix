# FTP-Flix

A single-file (`index.html`) Netflix-style browser for nginx / h5ai / Apache directory servers.
Live site (after enabling GitHub Pages): https://shohanurshihab.github.io/FTP-Flix/

- Search all servers, merged duplicates with a server picker, continue watching, My List, mark watched, surprise me
- Player: subtitles (SRT/VTT), volume, speed, fit/fill/zoom, skip 85 s, lock, PiP, share, copy link for VLC
- Works on phones and desktop

## CORS
Browsers block reading another site's directory listing unless the server sends CORS headers.
- Desktop: install a "CORS" browser extension and turn it on.
- Anywhere: set a **CORS proxy** in Settings. Example Cloudflare Worker (free):

```js
export default { async fetch(req) {
  const u = new URL(req.url).searchParams.get('url');
  const r = await fetch(u, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const h = new Headers(r.headers); h.set('Access-Control-Allow-Origin', '*');
  return new Response(r.body, { status: r.status, headers: h });
} }
```
Then use `https://YOUR-WORKER.workers.dev/?url={url}` as the proxy. A proxy outside Bangladesh cannot reach servers that only allow local ISPs.
Video files play directly and never need the proxy. MKV/HEVC/AC3 may not play in a browser; use "VLC link".

## Run on your PC (works when servers only allow your local ISP, and gives phones a link)
1. Download `index.html` and `proxy.py` into one folder.
2. Run `python proxy.py` (Python 3, nothing to install; on Windows try `py proxy.py`).
3. PC: open http://localhost:8787. Phone on the same Wi-Fi: open the `http://<PC-IP>:8787` address it prints.
The proxy is set automatically; no extension needed.
