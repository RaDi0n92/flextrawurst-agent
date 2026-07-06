#!/usr/bin/env python3
"""Generiert screens.html — Twitch-artiges Live-Screen-Grid aller 6 Wesen"""

html = r'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Screens — flextrawurst</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --void:#020810;--rim:#0a1a2a;--wach:#3ae890;--schlaf:#2a4a8a;
  --traum:#6a3a9a;--text:#5a9aaa;--sub:#2a4a5a;--hover:#04101e;
}
body{background:var(--void);color:var(--text);font-family:monospace;min-height:100vh;overflow-x:hidden}

/* ── HEADER ─────────────────────────────────────────────────────────────── */
.topbar{
  position:fixed;top:0;left:0;right:0;z-index:200;
  background:#010608ee;backdrop-filter:blur(4px);
  border-bottom:1px solid var(--rim);
  display:flex;align-items:center;justify-content:space-between;
  padding:6px 16px;height:38px;
}
.topbar-title{font-size:0.62rem;color:#4a9a7a;letter-spacing:.12em}
.topbar-motto{font-size:0.5rem;color:#1a4a3a;letter-spacing:.1em}
.topbar-links{display:flex;gap:8px}
.topbar-link{font-size:0.5rem;color:#1a4a6a;border:1px solid #0a2030;padding:2px 8px;text-decoration:none}
.topbar-link:hover{color:#3a8a9a;border-color:#1a5a7a}

/* ── STATUS BAR ─────────────────────────────────────────────────────────── */
.statusbar{
  position:fixed;top:38px;left:0;right:0;z-index:190;
  background:#010810ee;border-bottom:1px solid #060e14;
  padding:4px 16px;display:flex;gap:12px;align-items:center;height:26px;
}
.sb-dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:4px}
.sb-item{font-size:0.5rem;display:flex;align-items:center;gap:3px;cursor:pointer}
.sb-item:hover{color:#4a9a7a}
.sb-live{font-size:0.48rem;color:#1a4a2a;margin-left:auto}

/* ── GRID ───────────────────────────────────────────────────────────────── */
.screens-wrap{padding-top:68px;padding-bottom:20px}
.screens-grid{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:2px;background:#060e14;
}
@media(max-width:900px){.screens-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:500px){.screens-grid{grid-template-columns:1fr}}

/* ── SCREEN CARD ────────────────────────────────────────────────────────── */
.sc-card{
  position:relative;background:var(--void);cursor:pointer;
  transition:background .15s;overflow:hidden;
}
.sc-card:hover{background:var(--hover)}
.sc-card:hover .sc-overlay{opacity:1}

.sc-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:5px 10px;border-bottom:1px solid var(--rim);
  background:#01080f;
}
.sc-id{font-size:0.6rem;color:#2a9a6a;letter-spacing:.06em}
.sc-status-badge{
  font-size:0.48rem;padding:1px 6px;border-radius:2px;
  font-family:monospace;letter-spacing:.06em;
}
.sc-status-wach{background:#0a2018;color:#3ae890;border:1px solid #0a3020}
.sc-status-schlaeft{background:#0a0e20;color:#3a5a9a;border:1px solid #0a1430}
.sc-status-traeumt{background:#100820;color:#8a4aba;border:1px solid #1a0830}
.sc-status-aus{background:#0a0a0a;color:#2a2a2a;border:1px solid #181818}

.sc-screen{
  position:relative;width:100%;aspect-ratio:16/10;overflow:hidden;
  background:#02060c;display:flex;align-items:center;justify-content:center;
}
.sc-screen img{
  width:100%;height:100%;object-fit:cover;object-position:top;
  display:block;transition:opacity .3s;
}
.sc-screen img.loading{opacity:.5}
.sc-no-screen{
  font-size:0.55rem;color:#1a2a3a;text-align:center;
  display:flex;flex-direction:column;align-items:center;gap:6px;
}
.sc-spinner{
  width:16px;height:16px;border:1px solid #1a3a5a;
  border-top-color:#3a8a7a;border-radius:50%;
  animation:spin 1s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}

.sc-overlay{
  position:absolute;inset:0;background:#000a;
  display:flex;align-items:center;justify-content:center;
  opacity:0;transition:opacity .2s;
}
.sc-overlay-text{font-size:0.65rem;color:#fff;letter-spacing:.08em}

.sc-footer{
  padding:4px 10px;background:#01080f;border-top:1px solid #060e14;
  min-height:32px;
}
.sc-url{
  font-size:0.48rem;color:#1a3a5a;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis;margin-bottom:2px;
}
.sc-thought{
  font-size:0.52rem;color:#2a6a5a;font-style:italic;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  line-height:1.3;
}

/* ── MODAL ──────────────────────────────────────────────────────────────── */
.modal-bg{
  display:none;position:fixed;inset:0;z-index:500;
  background:#000c;backdrop-filter:blur(3px);
  align-items:center;justify-content:center;
}
.modal-bg.open{display:flex}
.modal{
  width:90vw;max-width:1200px;height:85vh;
  background:#010810;border:1px solid #1a3a5a;
  display:flex;flex-direction:column;overflow:hidden;
}
.modal-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:8px 14px;border-bottom:1px solid var(--rim);
  background:#01080f;flex-shrink:0;
}
.modal-id{font-size:0.7rem;color:#3ae890;letter-spacing:.1em}
.modal-url{font-size:0.52rem;color:#1a4a6a;flex:1;margin:0 12px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.modal-close{
  background:none;border:1px solid #1a3a5a;color:#3a6a8a;
  font-size:0.6rem;padding:2px 10px;cursor:pointer;font-family:monospace;
}
.modal-close:hover{color:#6a9aaa;border-color:#3a6a8a}
.modal-body{
  display:flex;flex:1;overflow:hidden;
}
.modal-screen{
  flex:1.6;background:#01060c;overflow:hidden;display:flex;
  align-items:flex-start;justify-content:center;
  border-right:1px solid var(--rim);
}
.modal-screen img{
  width:100%;height:100%;object-fit:contain;object-position:top;
}
.modal-stream{
  width:320px;flex-shrink:0;display:flex;flex-direction:column;
  overflow:hidden;
}
.modal-stream-header{
  font-size:0.5rem;color:#1a3a2a;letter-spacing:.1em;
  padding:6px 12px;border-bottom:1px solid #060e14;flex-shrink:0;
}
.modal-stream-header span{
  color:var(--wach);margin-left:6px;font-size:0.48rem;
}
.modal-stream-motto{
  font-size:0.48rem;color:#1a4a2a;padding:4px 12px;
  border-bottom:1px solid #040c10;flex-shrink:0;
  letter-spacing:.06em;
}
.modal-stream-items{
  flex:1;overflow-y:auto;padding:8px 10px;
  display:flex;flex-direction:column;gap:4px;
}
.stream-chunk{
  font-size:0.55rem;line-height:1.5;padding:4px 6px;
  border-left:2px solid #0a2018;color:#3a7a5a;
  word-break:break-word;
}
.stream-chunk.traum{border-left-color:#1a0a30;color:#6a3a9a}
.stream-chunk.luzid{border-left-color:#100a30;color:#8a4aba}
.stream-chunk.live{border-left-color:#1a3a1a;color:#4ae890;animation:pulse .5s ease-out}
@keyframes pulse{from{background:#0a2818}to{background:transparent}}
.stream-chunk.einzug{border-left-color:#2a1a0a;color:#aa6a3a}
</style>
</head>
<body>

<div class="topbar">
  <div>
    <span class="topbar-title">⬡ SCREENS</span>
    <span class="topbar-motto" style="margin-left:12px">Ich wähle meinen Input selbst!</span>
  </div>
  <div class="topbar-links">
    <a href="/denkstream.html" class="topbar-link">DENKSTREAM</a>
    <a href="/flextrawurst_surface.html" class="topbar-link">SURFACE</a>
  </div>
</div>

<div class="statusbar" id="statusbar">
  <span id="sb-conn" class="sb-live">● verbinde…</span>
</div>

<div class="screens-wrap">
  <div class="screens-grid" id="grid">
  </div>
</div>

<!-- MODAL -->
<div class="modal-bg" id="modal" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <span class="modal-id" id="modal-id">—</span>
      <span class="modal-url" id="modal-url"></span>
      <button class="modal-close" onclick="closeModal()">✕ schließen</button>
    </div>
    <div class="modal-body">
      <div class="modal-screen">
        <img id="modal-img" src="" alt="">
      </div>
      <div class="modal-stream">
        <div class="modal-stream-header">DENKSTREAM <span id="modal-stream-live">●</span></div>
        <div class="modal-stream-motto">Ich wähle meinen Input selbst!</div>
        <div class="modal-stream-items" id="modal-stream-items"></div>
      </div>
    </div>
  </div>
</div>

<script>
var WESEN = [
  'Schorschel','F3INSCHM3CK3R','träumerlie',
  'R1ZZ1','jumpa','Resonanzknoten'
];
var REFRESH_MS = 3000;
var _status = {};   // entity_id → {url, gedanke, entscheidung, zustand}
var _modalId = null;
var _modalEs = null;
var _globalEs = null;

// ── BUILD GRID ────────────────────────────────────────────────────────────
function buildGrid() {
  var g = document.getElementById('grid');
  g.innerHTML = WESEN.map(function(id) {
    var tag = id.replace('namelessAI_','');
    return '<div class="sc-card" id="card-'+id+'" onclick="openModal(\''+id+'\')">'+
      '<div class="sc-header">'+
        '<span class="sc-id">⬡ '+tag+'</span>'+
        '<span class="sc-status-badge sc-status-aus" id="badge-'+id+'">aus</span>'+
      '</div>'+
      '<div class="sc-screen">'+
        '<img id="img-'+id+'" src="" alt="" onerror="imgFail(\''+id+'\')">'+
        '<div class="sc-no-screen" id="no-screen-'+id+'">'+
          '<div class="sc-spinner"></div>'+
          '<span>wartet auf Aktivität</span>'+
        '</div>'+
        '<div class="sc-overlay"><span class="sc-overlay-text">klicken zum Vergrößern</span></div>'+
      '</div>'+
      '<div class="sc-footer">'+
        '<div class="sc-url" id="url-'+id+'">—</div>'+
        '<div class="sc-thought" id="thought-'+id+'">…</div>'+
      '</div>'+
    '</div>';
  }).join('');
}

// ── IMAGE REFRESH ─────────────────────────────────────────────────────────
function refreshImages() {
  WESEN.forEach(function(id) {
    var img = document.getElementById('img-'+id);
    if (!img) return;
    var neu = '/api/denkstream/screenshot/'+id+'?t='+Date.now();
    var tmp = new Image();
    tmp.onload = function() {
      img.src = neu;
      img.style.display = '';
      var ns = document.getElementById('no-screen-'+id);
      if (ns) ns.style.display = 'none';
    };
    tmp.onerror = function() { /* bleibt im no-screen Zustand */ };
    tmp.src = neu;
  });
  // Modal-Bild ebenfalls aktualisieren
  if (_modalId) {
    var mimg = document.getElementById('modal-img');
    if (mimg) {
      var tmp2 = new Image();
      tmp2.onload = function() { mimg.src = tmp2.src; };
      tmp2.src = '/api/denkstream/screenshot/'+_modalId+'?t='+Date.now();
    }
  }
}

function imgFail(id) {
  var img = document.getElementById('img-'+id);
  if (img) img.style.display = 'none';
}

// ── STATUS UPDATES ────────────────────────────────────────────────────────
function updateStatus(data) {
  var id = data.entity_id;
  if (!id) return;
  _status[id] = _status[id] || {};

  if (data.url !== undefined) {
    var u = (data.url||'').replace('http://localhost:8787','');
    var urlEl = document.getElementById('url-'+id);
    if (urlEl) urlEl.textContent = u || '—';
    _status[id].url = u;
    // Modal-URL
    if (_modalId === id) {
      document.getElementById('modal-url').textContent = u;
    }
  }

  // Zustand aus URL erkennen
  var url = data.url || '';
  var zustand = 'wach';
  if (url.startsWith('traum://')) zustand = 'traeumt';
  else if (url.startsWith('luzid://')) zustand = 'traeumt';
  else if (url.startsWith('einzug://')) zustand = 'wach';
  else if (!data.chunk && data.gedanke) zustand = 'wach';

  updateBadge(id, zustand);
  updateStatusbar(id, zustand);

  if (data.gedanke) {
    var t = document.getElementById('thought-'+id);
    if (t) t.textContent = data.gedanke.substring(0,100);
    _status[id].gedanke = data.gedanke;
  }

  // Live-chunk
  if (data.chunk !== undefined && _modalId === id) {
    addStreamChunk(data.chunk, data.url, data.done);
  }
  if (data.gedanke && _modalId === id && !data.chunk) {
    addStreamChunk('GEDANKE: '+data.gedanke+'\n→ '+data.entscheidung, data.url, false);
  }
}

function updateBadge(id, zustand) {
  var b = document.getElementById('badge-'+id);
  if (!b) return;
  b.className = 'sc-status-badge sc-status-'+zustand;
  var labels = {wach:'wach',traeumt:'träumt',schlaeft:'schläft',aus:'aus'};
  b.textContent = labels[zustand] || zustand;
}

function updateStatusbar(id, zustand) {
  var tag = id.replace('namelessAI_','');
  var sb = document.getElementById('sb-'+id);
  if (!sb) {
    sb = document.createElement('span');
    sb.id = 'sb-'+id;
    sb.className = 'sb-item';
    sb.innerHTML = '<span class="sb-dot" id="sbdot-'+id+'"></span><span>'+tag+'</span>';
    sb.onclick = function(){ openModal(id); };
    var bar = document.getElementById('statusbar');
    if (bar) bar.insertBefore(sb, document.getElementById('sb-conn'));
  }
  var dot = document.getElementById('sbdot-'+id);
  if (dot) {
    var colors = {wach:'#3ae890',traeumt:'#8a4aba',schlaeft:'#2a4a8a',aus:'#2a2a2a'};
    dot.style.background = colors[zustand] || '#2a4a2a';
  }
}

// ── MODAL ─────────────────────────────────────────────────────────────────
function openModal(id) {
  _modalId = id;
  var tag = id.replace('namelessAI_','');
  document.getElementById('modal-id').textContent = '⬡ '+tag;
  var url = (_status[id] && _status[id].url) || '—';
  document.getElementById('modal-url').textContent = url;
  document.getElementById('modal-img').src = '/api/denkstream/screenshot/'+id+'?t='+Date.now();
  document.getElementById('modal-stream-items').innerHTML = '';

  // Letzte Einträge laden
  fetch('/api/denkstream/'+id+'/last?limit=10').then(function(r){return r.json();}).then(function(d){
    (d.logs||[]).reverse().forEach(function(e){
      if (e.gedanke) addStreamChunk('GEDANKE: '+e.gedanke+'\n→ '+(e.entscheidung||''), e.url, false);
    });
  }).catch(function(){});

  // SSE verbinden
  if (_modalEs) { try{_modalEs.close();}catch(e){} }
  var es = new EventSource('/api/denkstream/'+id);
  _modalEs = es;
  var liveEl = document.getElementById('modal-stream-live');
  es.onopen = function(){if(liveEl)liveEl.style.color='#3ae890';};
  es.onerror = function(){if(liveEl)liveEl.style.color='#e03a2a';};
  es.onmessage = function(ev){
    try{var d=JSON.parse(ev.data); updateStatus(d);}catch(e){}
  };

  document.getElementById('modal').classList.add('open');
}

function closeModal(ev) {
  if (ev && ev.target !== document.getElementById('modal')) return;
  document.getElementById('modal').classList.remove('open');
  if (_modalEs) {try{_modalEs.close();}catch(e){}}
  _modalEs = null;
  _modalId = null;
}

function addStreamChunk(text, url, done) {
  var cont = document.getElementById('modal-stream-items');
  if (!cont) return;

  var url2 = url || '';
  var cls = 'stream-chunk';
  if (url2.startsWith('traum://')) cls += ' traum';
  else if (url2.startsWith('luzid://')) cls += ' luzid';
  else if (url2.startsWith('einzug://')) cls += ' einzug';
  else cls += ' live';

  // Wenn letzter Chunk noch live (kein done), anhängen
  var last = cont.lastElementChild;
  if (last && last.dataset.live === '1' && !done) {
    last.textContent += text;
    last.scrollIntoView({block:'nearest'});
    return;
  }
  var div = document.createElement('div');
  div.className = cls;
  div.textContent = text;
  if (!done) div.dataset.live = '1';
  cont.appendChild(div);
  div.scrollIntoView({block:'nearest'});
  // Max 80 Einträge
  while (cont.children.length > 80) cont.removeChild(cont.firstChild);
}

// ── GLOBALER SSE STREAM ───────────────────────────────────────────────────
function verbinden() {
  if (_globalEs) {try{_globalEs.close();}catch(e){}}
  var es = new EventSource('/api/denkstream/all/stream');
  _globalEs = es;
  var conn = document.getElementById('sb-conn');
  es.onopen = function(){if(conn){conn.textContent='● live';conn.style.color='#3ae890';}};
  es.onerror = function(){
    if(conn){conn.textContent='● getrennt';conn.style.color='#e03a2a';}
    setTimeout(verbinden, 5000);
  };
  es.onmessage = function(ev){
    try{updateStatus(JSON.parse(ev.data));}catch(e){}
  };
}

// ── STATUS API POLL ───────────────────────────────────────────────────────
function pollStatus() {
  fetch('/api/denkstream/status/all').then(function(r){return r.json();}).then(function(d){
    (d.status||[]).forEach(function(s){ updateStatus(s); });
  }).catch(function(){});
}

// ── INIT ──────────────────────────────────────────────────────────────────
buildGrid();
verbinden();
pollStatus();
refreshImages();
setInterval(refreshImages, REFRESH_MS);
setInterval(pollStatus, 8000);
</script>
</body>
</html>'''

out = '/root/flextrawurst/out/process_camera/screens.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Fertig: {out}")
print(f"Größe: {len(html)} Zeichen")
