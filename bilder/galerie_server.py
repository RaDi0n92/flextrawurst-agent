#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os, urllib.parse, mimetypes

BILDER_DIR = '/root/werkraum/bilder'
EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.avif'}
PORT = 7777

HTML_TMPL = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Bilder-Galerie</title>
<style>
  body {{ background:#111; color:#eee; font-family:sans-serif; margin:0; padding:20px; }}
  h1 {{ font-size:1.2rem; margin-bottom:16px; }}
  .grid {{ display:flex; flex-wrap:wrap; gap:12px; }}
  .grid img {{ max-width:220px; max-height:220px; object-fit:cover; border-radius:6px; cursor:pointer; transition:transform 0.15s; }}
  .grid img:hover {{ transform:scale(1.04); }}
  #lightbox {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.92); justify-content:center; align-items:center; z-index:100; }}
  #lightbox.active {{ display:flex; }}
  #lightbox img {{ max-width:90vw; max-height:90vh; border-radius:8px; }}
  #lb-close {{ position:fixed; top:18px; right:24px; font-size:2rem; cursor:pointer; color:#fff; }}
</style>
</head>
<body>
<h1>Bilder-Galerie</h1>
<div class="grid">{items}</div>
<div id="lightbox">
  <span id="lb-close" onclick="closeLB()">&#x2715;</span>
  <img id="lb-img" src="" alt="">
</div>
<script>
function openLB(src) {{
  document.getElementById('lb-img').src = src;
  document.getElementById('lightbox').classList.add('active');
}}
function closeLB() {{
  document.getElementById('lightbox').classList.remove('active');
  document.getElementById('lb-img').src = '';
}}
document.getElementById('lightbox').addEventListener('click', e => {{ if (e.target === e.currentTarget) closeLB(); }});
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeLB(); }});
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.unquote(self.path.split('?')[0])
        if path in ('/', '/index.html', ''):
            self.serve_gallery()
        else:
            self.serve_file(path.lstrip('/'))

    def serve_gallery(self):
        images = sorted(
            f for f in os.listdir(BILDER_DIR)
            if os.path.splitext(f)[1].lower() in EXTS
        )
        items = ''
        for img in images:
            enc = urllib.parse.quote(img)
            items += f'<img src="{enc}" alt="{img}" onclick="openLB(\'{enc}\')">\n'
        html = HTML_TMPL.format(items=items or '<p style="color:#888">Keine Bilder gefunden.</p>')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_file(self, fname):
        # Path-Traversal-Schutz: aufgeloester Pfad muss innerhalb BILDER_DIR bleiben
        base = os.path.realpath(BILDER_DIR)
        fpath = os.path.realpath(os.path.join(base, fname))
        if not (fpath == base or fpath.startswith(base + os.sep)):
            self.send_error(403)
            return
        # nur erlaubte Bild-Endungen ausliefern
        if os.path.splitext(fpath)[1].lower() not in EXTS:
            self.send_error(403)
            return
        if not os.path.isfile(fpath):
            self.send_error(404)
            return
        ct, _ = mimetypes.guess_type(fpath)
        with open(fpath, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ct or 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Galerie läuft auf Port {PORT}')
    server.serve_forever()
