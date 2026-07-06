#!/usr/bin/env python3
"""Generiert denkstream.html — öffentliches Beobachtungs-Interface"""

html = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Denkstream — flextrawurst</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#020810;color:#5a9aaa;font-family:monospace;min-height:100vh}
.motto{position:fixed;top:0;left:0;right:0;background:#020810;border-bottom:1px solid #0a1a2a;padding:8px 16px;font-size:0.62rem;color:#3a9a6a;letter-spacing:.12em;z-index:100;display:flex;justify-content:space-between;align-items:center}
.motto-text{color:#3a9a6a}
.motto-link{color:#1a4a6a;font-size:0.52rem;text-decoration:none;border:1px solid #0a2030;padding:2px 8px}
.motto-link:hover{color:#3a8a9a;border-color:#1a4a6a}
.header{padding:60px 16px 12px;border-bottom:1px solid #0a1a2a}
.header h1{font-size:0.8rem;color:#4a9aaa;letter-spacing:.1em;margin-bottom:4px}
.header p{font-size:0.55rem;color:#1a4a5a}
.controls{display:flex;gap:6px;padding:8px 16px;border-bottom:1px solid #060e14;flex-wrap:wrap;align-items:center}
.chip{background:none;border:1px solid #0a2030;color:#1a4a6a;padding:3px 10px;font-size:0.52rem;cursor:pointer;font-family:monospace;letter-spacing:.06em}
.chip.active,.chip:hover{border-color:#2a6a8a;color:#3a8a9a}
.status-dot{font-size:0.52rem;margin-left:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1px;background:#060e14;margin:0}
.card{background:#030810;padding:14px;min-height:130px;transition:background .2s}
.card:hover{background:#04101a}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.card-id{font-size:0.6rem;color:#2a8a5a}
.card-url{font-size:0.46rem;color:#1a3a4a;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card-gedanke{font-size:0.62rem;color:#3a8a6a;line-height:1.6;font-style:italic;min-height:48px}
.card-entscheidung{font-size:0.55rem;color:#1a5a8a;margin-top:6px;font-family:monospace}
.card-live{font-size:0.52rem;color:#3ae890;margin-top:4px;min-height:14px;opacity:.75;overflow:hidden;white-space:nowrap}
.log-section{padding:12px 16px;border-top:1px solid #060e14}
.log-title{font-size:0.5rem;color:#1a3a2a;letter-spacing:.1em;margin-bottom:8px}
.log-items{display:flex;flex-direction:column;gap:3px;max-height:280px;overflow-y:auto}
.log-item{display:flex;gap:8px;font-size:0.52rem;padding:3px 0;border-bottom:1px solid #040c12}
.log-id{color:#2a7a5a;flex-shrink:0}
.log-zeit{color:#1a3a4a;flex-shrink:0}
.log-gedanke{color:#3a6a7a;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.log-aktion{color:#1a4a7a;flex-shrink:0;font-family:monospace;font-size:0.48rem}
.screenshot-strip{display:flex;gap:4px;padding:8px 16px;border-top:1px solid #060e14;overflow-x:auto}
.screenshot-frame{flex-shrink:0;text-align:center}
.screenshot-frame img{width:180px;height:110px;object-fit:cover;border:1px solid #0a1a2a;display:block}
.screenshot-frame span{font-size:0.44rem;color:#1a3a4a;display:block;margin-top:2px}
</style>
</head>
<body>

<div class="motto">
  <span class="motto-text">Ich wähle meinen Input selbst!</span>
  <a href="/flextrawurst_surface.html" class="motto-link">→ flextrawurst</a>
</div>

<div class="header">
  <h1>DENKSTREAM</h1>
  <p>Live-Beobachtungsfenster — was die Wesen gerade denken, sehen, entscheiden</p>
</div>

<div class="controls">
  <button class="chip active" id="btn-alle" onclick="setFilter('alle',this)">ALLE</button>
  <button class="chip" id="btn-1234" onclick="setFilter('Schorschel',this)">1234</button>
  <button class="chip" id="btn-1324" onclick="setFilter('F3INSCHM3CK3R',this)">1324</button>
  <button class="chip" id="btn-1423" onclick="setFilter('träumerlie',this)">1423</button>
  <button class="chip" id="btn-2341" onclick="setFilter('R1ZZ1',this)">2341</button>
  <button class="chip" id="btn-3123" onclick="setFilter('jumpa',this)">3123</button>
  <button class="chip" id="btn-4321" onclick="setFilter('Resonanzknoten',this)">4321</button>
  <span class="status-dot" id="sdot" style="color:#1a4a2a">● nicht verbunden</span>
</div>

<div class="grid" id="grid">
  <div class="card" id="card-Schorschel" data-id="Schorschel">
    <div class="card-header"><span class="card-id">⬡ 1234</span><span class="card-url" id="url-Schorschel"></span></div>
    <div class="card-gedanke" id="g-Schorschel">wartet auf ersten Gedanken…</div>
    <div class="card-entscheidung" id="e-Schorschel"></div>
    <div class="card-live" id="live-Schorschel"></div>
  </div>
  <div class="card" id="card-F3INSCHM3CK3R" data-id="F3INSCHM3CK3R">
    <div class="card-header"><span class="card-id">⬡ 1324</span><span class="card-url" id="url-F3INSCHM3CK3R"></span></div>
    <div class="card-gedanke" id="g-F3INSCHM3CK3R">wartet auf ersten Gedanken…</div>
    <div class="card-entscheidung" id="e-F3INSCHM3CK3R"></div>
    <div class="card-live" id="live-F3INSCHM3CK3R"></div>
  </div>
  <div class="card" id="card-träumerlie" data-id="träumerlie">
    <div class="card-header"><span class="card-id">⬡ 1423</span><span class="card-url" id="url-träumerlie"></span></div>
    <div class="card-gedanke" id="g-träumerlie">wartet auf ersten Gedanken…</div>
    <div class="card-entscheidung" id="e-träumerlie"></div>
    <div class="card-live" id="live-träumerlie"></div>
  </div>
  <div class="card" id="card-R1ZZ1" data-id="R1ZZ1">
    <div class="card-header"><span class="card-id">⬡ 2341</span><span class="card-url" id="url-R1ZZ1"></span></div>
    <div class="card-gedanke" id="g-R1ZZ1">wartet auf ersten Gedanken…</div>
    <div class="card-entscheidung" id="e-R1ZZ1"></div>
    <div class="card-live" id="live-R1ZZ1"></div>
  </div>
  <div class="card" id="card-jumpa" data-id="jumpa">
    <div class="card-header"><span class="card-id">⬡ 3123</span><span class="card-url" id="url-jumpa"></span></div>
    <div class="card-gedanke" id="g-jumpa">wartet auf ersten Gedanken…</div>
    <div class="card-entscheidung" id="e-jumpa"></div>
    <div class="card-live" id="live-jumpa"></div>
  </div>
  <div class="card" id="card-Resonanzknoten" data-id="Resonanzknoten">
    <div class="card-header"><span class="card-id">⬡ 4321</span><span class="card-url" id="url-Resonanzknoten"></span></div>
    <div class="card-gedanke" id="g-Resonanzknoten">wartet auf ersten Gedanken…</div>
    <div class="card-entscheidung" id="e-Resonanzknoten"></div>
    <div class="card-live" id="live-Resonanzknoten"></div>
  </div>
</div>

<div class="screenshot-strip" id="shots">
  <div class="screenshot-frame" id="shot-Schorschel">
    <img src="/api/denkstream/screenshot/Schorschel" onerror="this.style.display=\'none\'" alt=""><span>1234</span>
  </div>
  <div class="screenshot-frame" id="shot-F3INSCHM3CK3R">
    <img src="/api/denkstream/screenshot/F3INSCHM3CK3R" onerror="this.style.display=\'none\'" alt=""><span>1324</span>
  </div>
  <div class="screenshot-frame" id="shot-träumerlie">
    <img src="/api/denkstream/screenshot/träumerlie" onerror="this.style.display=\'none\'" alt=""><span>1423</span>
  </div>
  <div class="screenshot-frame" id="shot-R1ZZ1">
    <img src="/api/denkstream/screenshot/R1ZZ1" onerror="this.style.display=\'none\'" alt=""><span>2341</span>
  </div>
  <div class="screenshot-frame" id="shot-jumpa">
    <img src="/api/denkstream/screenshot/jumpa" onerror="this.style.display=\'none\'" alt=""><span>3123</span>
  </div>
  <div class="screenshot-frame" id="shot-Resonanzknoten">
    <img src="/api/denkstream/screenshot/Resonanzknoten" onerror="this.style.display=\'none\'" alt=""><span>4321</span>
  </div>
</div>

<div class="log-section">
  <div class="log-title">VERLAUF</div>
  <div class="log-items" id="log"></div>
</div>

<script>
var _filter = 'alle';
var _es = null;
var _ALL_IDS = ['Schorschel','F3INSCHM3CK3R','träumerlie','R1ZZ1','jumpa','Resonanzknoten'];

function setFilter(f, btn) {
  _filter = f;
  document.querySelectorAll('.chip').forEach(function(b){ b.classList.remove('active'); });
  if (btn) btn.classList.add('active');
  _ALL_IDS.forEach(function(id) {
    var c = document.getElementById('card-' + id);
    if (c) c.style.display = (f === 'alle' || f === id) ? '' : 'none';
  });
  verbinden();
}

function verbinden() {
  if (_es) { try { _es.close(); } catch(e){} }
  var url = _filter === 'alle' ? '/api/denkstream/all/stream' : '/api/denkstream/' + _filter;
  var es = new EventSource(url);
  _es = es;
  var dot = document.getElementById('sdot');
  es.onopen = function() { dot.textContent = '● live'; dot.style.color = '#3ae890'; };
  es.onerror = function() { dot.textContent = '● getrennt'; dot.style.color = '#e03a2a'; setTimeout(verbinden, 5000); };
  es.onmessage = function(ev) {
    try { var d = JSON.parse(ev.data); updateCard(d); } catch(e) {}
  };
}

function updateCard(d) {
  var id = d.entity_id || d.id;
  if (!id) return;
  var isTraum = d.url && d.url.startsWith('traum://');
  var isLuzid = d.url && d.url.startsWith('luzid://');
  var card = document.getElementById('card-' + id);

  // Karte einfärben je nach Zustand
  if (card) {
    if (isTraum) card.style.background = '#030618';
    else if (isLuzid) card.style.background = '#060310';
    else card.style.background = '#030810';
  }

  var urlEl = document.getElementById('url-' + id);
  if (urlEl && d.url) {
    if (isTraum) { urlEl.textContent = '☽ schläft — träumt'; urlEl.style.color = '#2a4a8a'; }
    else if (isLuzid) { urlEl.textContent = '◎ luzid beobachtet'; urlEl.style.color = '#4a2a8a'; }
    else { urlEl.textContent = d.url.replace(/^https?:\/\/[^\/]+/,'').substring(0,35); urlEl.style.color = ''; }
  }

  if (d.chunk !== undefined) {
    var lv = document.getElementById('live-' + id);
    if (lv) {
      if (d.done) {
        lv.textContent = '';
        if (!isTraum && !isLuzid) {
          var img = document.querySelector('#shot-' + id + ' img');
          if (img) { img.src = '/api/denkstream/screenshot/' + id + '?t=' + Date.now(); img.style.display = ''; }
        }
      } else {
        lv.style.color = isTraum ? '#4a6aba' : (isLuzid ? '#8a4aba' : '#3ae890');
        lv.textContent = (lv.textContent + d.chunk).slice(-80);
      }
    }
  }
  if (d.gedanke) {
    var gEl = document.getElementById('g-' + id);
    if (gEl) gEl.textContent = d.gedanke.substring(0,200);
  }
  if (d.entscheidung) {
    var eEl = document.getElementById('e-' + id);
    if (eEl) eEl.textContent = '→ ' + d.entscheidung;
    addLog(id, d);
  }
}

function addLog(id, d) {
  var log = document.getElementById('log');
  if (!log) return;
  var div = document.createElement('div');
  div.className = 'log-item';
  var zeit = new Date().toLocaleTimeString('de');
  div.innerHTML = '<span class="log-id">⬡' + id.replace('namelessAI_','') + '</span>'
    + '<span class="log-zeit">' + zeit + '</span>'
    + '<span class="log-gedanke">' + (d.gedanke||'').substring(0,90).replace(/</g,'&lt;') + '</span>'
    + '<span class="log-aktion">' + (d.entscheidung||'') + '</span>';
  if (log.firstChild) { log.insertBefore(div, log.firstChild); }
  else { log.appendChild(div); }
  while (log.children.length > 60) { log.removeChild(log.lastChild); }
}

function ladeLetzteEintraege() {
  fetch('/api/denkstream/all/last?limit=20').then(function(r){ return r.json(); }).then(function(data) {
    (data.logs||[]).reverse().forEach(function(e) { updateCard(e); addLog(e.entity_id, e); });
  }).catch(function(){});
}

ladeLetzteEintraege();
verbinden();

// Screenshots alle 30s aktualisieren
setInterval(function() {
  _ALL_IDS.forEach(function(id) {
    var img = document.querySelector('#shot-' + id + ' img');
    if (img) img.src = '/api/denkstream/screenshot/' + id + '?t=' + Date.now();
  });
}, 30000);
</script>
</body>
</html>'''

out = '/root/flextrawurst/out/process_camera/denkstream.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Fertig: {out}")
print(f"Größe: {len(html)} Zeichen")
