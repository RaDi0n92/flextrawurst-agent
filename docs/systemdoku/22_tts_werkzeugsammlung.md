---
titel: TTS-Werkzeugsammlung (flextrawurst.de/tts)
typ: system
erstellt: 2026-07-10
autor: claude-code bei Daniels VPS
---

# TTS-Werkzeugsammlung (flextrawurst.de/tts)

[[INDEX|← Index]]

## Zweck

`https://flextrawurst.de/tts` heißt noch "TTS", ist inzwischen aber (Daniels eigene Worte, 2026-07-10) "eine scheiß Benennung für das, was jetzt mittlerweile auf dieser Domain gebastelt wurde" — eine einzige Single-Page-App mit acht Werkzeug-Tabs: **TTS**, **Soundboard**, **Übersetzen**, **OCR**, **Dokumente**, **Webarchiv**, **Formulare**, **Logs**, seit 2026-07-10 zusätzlich **Datei-Wandler**. Der Name bleibt vorerst `/tts` — eine bessere Bezeichnung ist noch nicht gefunden.

Backend: FastAPI-Service `tts_service.py` (systemd `tts-service.service`, Port 8035, WorkingDirectory `/root/werkraum/welt`). Frontend: einzelne Datei `/root/werkraum/welt/tts_ui.html` (wird bei jedem GET `/` frisch von der Platte gelesen — kein Service-Neustart nötig nach Frontend-Änderungen). nginx (`/etc/nginx/sites-available/flextrawurst`) proxyt `/tts/` → `localhost:8035/`.

Diese Datei ist die laufend aktualisierte Referenz für dieses Subsystem — die anderen sieben ursprünglichen Tabs (TTS, Soundboard, Übersetzen, OCR, Dokumente, Webarchiv, Formulare, Logs) sind historisch gewachsen und hier bewusst noch nicht im Detail dokumentiert, das war nicht Teil dieses Bau-Auftrags. Nur der neue Tab und der neue Login-Schutz sind unten beschrieben.

## Tab-Mechanik

Rein clientseitig, generisch: `[data-tab-target]`-Buttons und `[data-tab-panel]`-Sections werden per `querySelectorAll` einmal eingesammelt, ein gemeinsamer Klick-Handler schaltet `.on`-Klassen um (`renderTabState()`/`setTab()` in `tts_ui.html`). Aktiver Tab landet in `localStorage` (`ACTIVE_TAB_KEY`) und im URL-Parameter `?tab=`. **Wichtig für neue Tabs:** der Tab-Name muss zusätzlich in drei fest kodierten Whitelist-Arrays stehen (`renderTabState`, `setTab`, `currentTab` — alle drei identisch: `['tts','soundboard',...]`), sonst fällt die Routing-Logik beim Laden/Persistieren stumm auf `'tts'` zurück, auch wenn der Klick-Handler selbst generisch ist.

## Datei-Wandler-Tab (neu, 2026-07-10)

Umzug auf Daniels Wunsch: der bis dahin eigenständige **Datei-Wandler** (VPS-Pfade/Uploads → Offline-HTML/Markdown/ZIP-Export, Quelle `/root/werkraum/datei_wandler/`, Backend `datei-wandler.service` als `uvicorn datei_wandler.app:app` auf Port 8878, bislang nur erreichbar über `https://217.154.14.29:8449/` mit eigenem Login) ist jetzt zusätzlich als eigener Tab unter `/tts` erreichbar — "mit allem was er kann", so wie er war.

- **Backend unverändert:** Der Python-Prozess auf Port 8878 wurde nicht angefasst, nicht neugestartet, keine Codeänderung. Neue nginx-Location `location /tts/dateiwandler/ { proxy_pass http://127.0.0.1:8878/; ... }` (gleiche Timeouts/Body-Limits wie die alte Route auf Port 8449) macht ihn zusätzlich unter dem neuen Pfad erreichbar. Die alte Route (217.154.14.29:8449, eigener Login `.htpasswd_datei_wandler`) läuft unverändert weiter.
- **Frontend fast unverändert:** Markup und JavaScript aus `datei_wandler/static/index.html` 1:1 übernommen (gleiche Funktionen: `addFiles`, `render`, `uploadBatches`, `fetchChecked`, `startDownload`, gleiche Batch-Logik für große Uploads). Zwei mechanische Anpassungen, beide von Daniel als Bedingung genannt ("wenn's nicht geht wegen dem Header oder so, dann bau minimal um"):
  1. Element-IDs auf `dw-`-Präfix umbenannt (Konvention der anderen `/tts`-Tabs, z.B. `documents-`, `webarchive-`), um Kollisionen mit der bereits sehr großen bestehenden Seite auszuschließen.
  2. API-Pfade von absolut (`/convert`, `/upload-sessions`) auf `/tts/dateiwandler/convert`, `/tts/dateiwandler/upload-sessions/...` umgeschrieben — sonst wären die Fetch-Aufrufe (absolute Pfade ab Domain-Root) am `/tts`-Root gelandet statt beim Datei-Wandler-Backend.
  - **Farbe/Optik bewusst nicht übernommen:** Daniel erlaubte explizit "Farbe kann auch so bleiben, wess einfacher ist" — eigenes `:root`-Farbschema des Datei-Wandlers (u.a. `--field`, das exakt mit einer bereits von `/tts` selbst verwendeten Variable kollidiert hätte) wurde deshalb komplett verworfen. Der Tab nutzt stattdessen unverändert die vorhandenen `/tts`-Klassen (`.panel`, `.panel-title`, `.inf`, `.row`, `.file-btn`, `button.small`, `.sentence-list`/`.sentence-row`), passt sich also optisch nahtlos ins bestehende Lila-Theme ein statt eine zweite Farbwelt mitzubringen.
- Live end-to-end getestet (Playwright, echter Login): Tab-Wechsel fehlerfrei, echter Export über `/tts/dateiwandler/convert` ausgelöst (`/root/werkraum/_shared/briefkasten/REGELN.md` → 21.883 Byte HTML-Datei heruntergeladen), Test-Export danach wieder gelöscht (landet sonst wie jeder normale Export in `datei_wandler/exports/`, das ist bestehendes, unverändertes Verhalten).

## Login-Schutz (neu, 2026-07-10)

Auf Daniels ausdrücklichen Wunsch ("ich will /tts ab jetzt nur noch per Login haben") ist die komplette `/tts`-Seite jetzt per HTTP-Basic-Auth geschützt — vorher war sie öffentlich ohne jeden Schutz erreichbar.

- `/etc/nginx/.htpasswd_tts` (bcrypt, `htpasswd -iB`, Passwort nie in einer Bash-Kommandozeile oder in einem Log gelandet — per stdin gesetzt), Benutzer `daniel`. Passwort ist absichtlich nirgends in Doku/Notizen/Git festgehalten.
- `auth_basic`/`auth_basic_user_file` auf allen drei betroffenen nginx-Locations gesetzt: `location = /tts`, `location /tts/`, `location /tts/dateiwandler/` (keine automatische Vererbung zwischen Geschwister-Locations in nginx, deshalb dreifach explizit statt einmal zentral).
- Verifiziert: ohne Login → 401, falsches Passwort → 401, korrektes Passwort → 200. Die alte, separate Datei-Wandler-Route (Port 8449, eigener Login) bleibt davon unberührt und weiterhin erreichbar.

## Bekannte offene Punkte

- Die sieben ursprünglichen Tabs (TTS, Soundboard, Übersetzen, OCR, Dokumente, Webarchiv, Formulare, Logs) sind hier noch nicht im Detail dokumentiert — nur ihre gemeinsame Tab-Mechanik.
- `/tts` als Pfadname bleibt vorerst bestehen, obwohl er die Seite längst nicht mehr treffend beschreibt — Daniel hat noch keinen besseren Namen gefunden.
