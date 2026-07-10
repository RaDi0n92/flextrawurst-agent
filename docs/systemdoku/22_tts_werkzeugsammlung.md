---
titel: TTS-Werkzeugsammlung (flextrawurst.de/tts)
typ: system
erstellt: 2026-07-10
autor: claude-code bei Daniels VPS
---

# TTS-Werkzeugsammlung (flextrawurst.de/tts)

[[INDEX|← Index]]

## Zweck

`https://flextrawurst.de/tts` heißt noch "TTS", ist inzwischen aber (Daniels eigene Worte, 2026-07-10) "eine scheiß Benennung für das, was jetzt mittlerweile auf dieser Domain gebastelt wurde" — eine einzige Single-Page-App mit Werkzeug-Tabs: **TTS**, **Soundboard**, **Übersetzen**, **OCR**, **Dokumente**, **Webarchiv**, seit 2026-07-10 zusätzlich **Datei-Wandler**. Der Name bleibt vorerst `/tts` — eine bessere Bezeichnung ist noch nicht gefunden. **Logs** und **Formulare** existierten bis 2026-07-10, wurden auf Daniels Wunsch ("kann beides weg is müll") komplett entfernt — Frontend UND ungenutzte Backend-Routen blieben unangetastet im Server bestehen, nur der UI-Zugang ist weg.

Backend: FastAPI-Service `tts_service.py` (systemd `tts-service.service`, Port 8035, WorkingDirectory `/root/werkraum/welt`). Frontend: einzelne Datei `/root/werkraum/welt/tts_ui.html` (wird bei jedem GET `/` frisch von der Platte gelesen — kein Service-Neustart nötig nach reinen Frontend-Änderungen, nur bei Python-Änderungen in `tts_service.py`). nginx (`/etc/nginx/sites-available/flextrawurst`) proxyt `/tts/` → `localhost:8035/`.

Diese Datei ist die laufend aktualisierte Referenz für dieses Subsystem — die verbliebenen sechs ursprünglichen Tabs (TTS, Soundboard, Übersetzen, OCR, Dokumente, Webarchiv) sind historisch gewachsen und hier bewusst noch nicht im Detail dokumentiert, das war nicht Teil dieses Bau-Auftrags. Nur der neue Tab, der Login-Schutz, der Crawler-Zugangsschlüssel und die Tab-Entfernung sind unten beschrieben.

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

## Crawler-Zugangsschlüssel (neu, 2026-07-10)

Zielkonflikt, den Daniel selbst benannt hat: er will `/tts` sowohl login-geschützt UND von externen LLM-Crawl-Tools (ChatGPT-Browsing, WebFetch usw.) frei lesbar haben, damit er die URL einem LLM geben und mit vollem Seiteninhalt darüber sprechen kann. Basic-Auth allein schließt Crawler grundsätzlich aus (die meisten Tools können keine Zugangsdaten mitschicken). Lösung: ein zweiter, vom Login-Passwort unabhängiger Geheim-Schlüssel als URL-Parameter.

- **Zugang:** `https://flextrawurst.de/tts/?key=<TOKEN>` umgeht die Basic-Auth komplett — nginx prüft den Parameter über einen `map $arg_key $tts_key_ok {...}`-Block (`/etc/nginx/conf.d/tts-crawl-key.conf`) und setzt `auth_basic` in allen drei `/tts`-Locations dynamisch auf `off`, wenn der Schlüssel passt (`if ($tts_key_ok = 1) { set $tts_auth off; }`). Falscher/fehlender Schlüssel → weiterhin 401.
- **Token-Speicher:** `/root/werkraum/welt/.env.tts_crawl_key` (chmod 600, `.env.*` bereits global gitignored) — von `tts_service.py`s `/`-Route bei jedem Request frisch gelesen und in die ausgelieferte Seite eingesetzt (`window.TTS_CRAWL_KEY = "...";`), damit eine Rotation ohne Codeänderung/Neustart des Frontends wirkt (nur die eigentliche nginx-`map`-Datei UND `.env.tts_crawl_key` müssen bei einer Rotation gemeinsam aktualisiert werden — zwei Stellen, nicht automatisch synchron).
- **UI:** tab-übergreifender Button `🔑 Crawler-Zugang` (amberfarben, bewusst anders als die pinken Tab-Buttons) direkt neben der Tab-Leiste, immer sichtbar unabhängig vom aktiven Tab. Öffnet ein Popup mit der fertigen, kopierbaren URL.
- **Sicherheitsabwägung, mit Daniel besprochen bevor gebaut:** dieser Schlüssel ist faktisch ein zweiter Generalschlüssel zum Datei-Wandler (beliebiger Lesezugriff auf `/root/werkraum`, `/root/visionen`) — sobald er einem LLM-Tool gegeben wird, kann er in dessen Logs landen. Kein technischer Kompromiss dagegen, nur Daniels bewusste Entscheidung dass er das für den Anwendungsfall in Kauf nimmt. Jederzeit rotierbar (neuer Token in beiden Dateien, `systemctl reload nginx`).
- **Live-Bug gefunden und gefixt (im selben Zug):** die erste Implementierung nutzte `content.replace("__TTS_CRAWL_KEY__", crawl_key)` blind global in Python — das hat nicht nur die eine Zuweisungszeile getroffen, sondern auch einen JS-Fallback-Check weiter unten im selben Dokument (`key.indexOf('__TTS_CRAWL_KEY__')`), der DAMIT ebenfalls zu `key.indexOf(<dergleichewert>)` wurde — das findet sich selbst an Position 0, der Check hielt sich also fälschlich immer für "nicht konfiguriert". Popup zeigte deshalb nie den echten Link. Gefunden durch systematisches Debuggen (Konsole-Logs Schritt für Schritt), behoben durch gezielten `.replace(...)` nur der einen bekannten Zeile mit `count=1` statt blindem globalem Ersatz. Zusätzlich: der zuerst generierte Testschlüssel wurde beim Debuggen einmal versehentlich vollständig in ein Kommandozeilen-Log ausgegeben (eigener Fehler, per Grep ohne Bedacht) — danach sofort rotiert (neuer Token, alte Datei überschrieben, nginx neu geladen), bevor der Schlüssel an Daniel ausgegeben wurde.
- Verifiziert (Playwright + curl): korrekter Schlüssel ohne jedes Login → 200, falscher Schlüssel → 401, kein Schlüssel → 401, Popup zeigt exakt den aktuell gültigen (rotierten) Schlüssel, bestehender Basic-Auth-Login funktioniert unverändert weiter.

## Bekannte offene Punkte

- Die sechs verbliebenen ursprünglichen Tabs (TTS, Soundboard, Übersetzen, OCR, Dokumente, Webarchiv) sind hier noch nicht im Detail dokumentiert — nur ihre gemeinsame Tab-Mechanik.
- `/tts` als Pfadname bleibt vorerst bestehen, obwohl er die Seite längst nicht mehr treffend beschreibt — Daniel hat noch keinen besseren Namen gefunden.
- Ungenutzte Backend-Routen für Logs/Formulare (`/logs/*`, `/forms/*` in `tts_service.py`) sind noch nicht entfernt — nur der UI-Zugang. Kein Auftrag dafür bisher, kein Sicherheits- oder Funktionsrisiko (nichts verlinkt mehr dorthin), aber echtes totes Gewicht im Server-Code.
- Crawler-Schlüssel-Rotation ist ein manueller Zwei-Dateien-Vorgang (`.env.tts_crawl_key` + `conf.d/tts-crawl-key.conf`), kein automatisiertes Tooling dafür.
