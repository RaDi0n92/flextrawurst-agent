# Systemdokumentation 38: VPS-MCP-Werkzeugkörper (für ChatGPT)

---
autor: claude-code bei Daniels VPS
datum: 2026-07-23
status: PHASE 1 PRODUKTIV & VERIFIZIERT (5 weitere Phasen geplant)
port: 8091
service: vps-mcp.service
---

## 1. Warum diese Datei existiert

Daniel: *"ja chatgpt ist teil des schiffes teil der crew xD und ja alles machen"* — als Antwort auf eine sehr umfangreiche, von einer anderen KI-Instanz vorgeschlagene Spezifikation für einen MCP-Server, der praktisch den gesamten VPS für ChatGPT zugänglich machen soll: Dateien, Git-Provenienz, Agenten-Sitzungen (Gemini/Claude/Codex), Dienste/Docker/Netzwerk, Datenbanken, Web-Apps/3D-Assets und Zensi (lesend und schreibend).

Bewusst **nicht** als ein einziger riesiger, ungeprüfter Bauschritt umgesetzt — siehe die Linsen-Session am selben Tag (`_claude/ideen/sieben_linsen_koerper_kreatur.md`): ein großer Bauplan wird trotzdem in Stufen umgesetzt, jede Stufe einzeln verifiziert.

## 2. Architektur

Eigenständiger MCP-Server, getrennt von `flextrawurst_3d_mcp.py` (Systemdoku 34) — konzeptionell ein viel breiterer "Werkzeugkörper", kein Teil der 3D-Pipeline. Gleicher, bereits gegen ChatGPT verifizierter OAuth-2.1+PKCE-Mechanismus (kopiert, nicht neu erfunden).

- **Server:** `/root/werkraum/tools/vps_mcp/vps_mcp_server.py`
- **Port:** 8091, nur `127.0.0.1` gebunden
- **Systemd:** `/etc/systemd/system/vps-mcp.service`
- **nginx:** `location /vps-mcp/` in `/etc/nginx/sites-available/flextrawurst`, proxy zu `127.0.0.1:8091`
- **Öffentlich:** `https://flextrawurst.de/vps-mcp/`

## 3. Sicherheit (von Anfang an mitgedacht)

- **`ALLOWED_ROOTS`:** Datei-Zugriff nur unter `/root/werkraum`, `/root/flextrawurst`, `/root/zensi`, `/root/.gemini/antigravity-cli/brain` — kein freier VPS-weiter Zugriff.
- **`SECRET_MUSTER`:** `.env`, `*_tokens.json`, `id_rsa*`, `*.pem`, `*.key`, `.htpasswd*`, alles mit `password`/`secret`/`credentials` im Namen — ausgeschlossen, auch wenn es innerhalb einer erlaubten Wurzel liegt (jeder Pfad-Teil wird geprüft, nicht nur der Dateiname).
- **`services.status`/`services.logs`:** nur lesend, kein restart/stop/start. Dienstname gegen striktes Regex geprüft (`^[a-zA-Z0-9_@.+-]+\.service$`), kein Shell-Injection-Vektor.
- **`assets.get_file`:** Dateien bis 2MB inline als Base64, größere über eine befristete (10 Minuten), zufällig token-abgesicherte Download-URL (`/download/<token>`) statt riesiger Base64-Blöcke im Chat-Kontext.

## 4. Gemeinsames Ausgabeformat

Jedes Tool liefert `{ok, data, source_refs, warnings, truncated, next_cursor, error}`. Jede Fundstelle in `source_refs` trägt zusätzlich `path`, `start_line`/`end_line`, `sha256`, `modified_at`, `git_commit`, `source_type` — Daniels Vorgabe, damit Aussagen später auf konkrete VPS-Fundstellen zurückführbar sind.

## 5. Phase 1 — zwölf Tools (fertig, verifiziert)

`vps.list_roots`, `vps.list_files`, `vps.search_text`, `vps.read_file`, `vps.file_metadata`, `git.status`, `git.log`, `services.status`, `services.logs`, `system.snapshot` (alle von Daniel selbst als risikoärmster Einstieg vorgeschlagen), plus `assets.get_file` und `assets.render_3d_preview` (von Daniel priorisiert — wiederverwendet `blender_pipeline` aus der 3D-Pipeline, kein Duplikat).

**Verifiziert:** isolierter Test aller 12 Tools inkl. Sicherheitsfälle (`.env`-Ausschluss, Pfad außerhalb erlaubter Wurzeln, Shell-Injection-Versuch im Dienstnamen — alle korrekt abgelehnt), echtes Blender-Rendering gegen `test_cube.glb`, kompletter OAuth-2.1+PKCE-Flow live simuliert über `https://flextrawurst.de/vps-mcp/`, Hauptseite unverändert erreichbar. werkraum-Commit `c8a04a02e`.

## 6. Geplante Phasen 2–6 (noch nicht gebaut)

2. Restliche Asset-Tools (`assets.list/search/inspect/preview/extract_3d_metadata/validate_3d_model/convert_3d_model/find_duplicates/trace_source/read_manifest/list_renders/inspect_image/inspect_audio`) + `provenance.trace`, `git.show`, `git.diff`.
3. `agents.*` (Gemini-/Claude-/Codex-Sitzungen lesen/durchsuchen/vergleichen) + `containers.*`/`network.*`.
4. `database.*` (nur lesend) + `webapps.*` + `tests.*`.
5. `zensi.*` — nur lesende Tools.
6. `zensi.*` — schreibende Aktionen (zuletzt, am heikelsten — Eingriffe in ein laufendes System).

## 7. Zugangsdaten (systemd-Unit, nicht im Git-Repo)

- API-Key (Zustimmungs-Schritt): `VPS_MCP_KEY`
- Client ID: `vps-mcp`
- Client Secret: `VPS_MCP_CLIENT_SECRET`

Rotiert am 2026-07-23 (die urspruenglichen Werte waren vollstaendig im ChatGPT-Chat gelandet). `_ACCESS_TOKENS`/`_AUTH_CODES` sind In-Memory -- jeder Dienst-Neustart (auch fuer Rotation) macht bereits verbundene Connector-Sitzungen ungueltig, die Verbindung muss danach immer komplett neu aufgebaut werden.

## 8. Zwei Nachbesserungen beim echten Verbinden

1. **"App-Verknüpfung erkannt, Tool-Weitergabe noch nicht"** — der Server beantwortete JSON-RPC-**Notifications** (Nachrichten ohne `id`-Feld, z.B. `notifications/initialized`, die der Client nach `initialize` schickt) fälschlich mit einer Fehler-JSON statt gar nicht zu antworten (JSON-RPC 2.0 verlangt für Notifications keine Antwort). Das brach den Handshake vermutlich ab, bevor `tools/list` je aufgerufen wurde. Behoben: Notifications liefern jetzt einen leeren `202 Accepted`. Zusätzlich spiegelt `initialize` jetzt die vom Client angefragte `protocolVersion` statt starr `2024-11-05` zu behaupten. Gleicher Fix auch in `flextrawurst_3d_mcp.py` angewandt (derselbe kopierte Code, gleicher Bug). Commits `585d91306` (vps-mcp) + `ec59651f0` (3d-mcp).
2. **`vps.find_recent_files` ergänzt** — der von Daniel/ChatGPT selbst vorgeschlagene erste Test ("die zehn zuletzt geänderten Dateien im Werkraum") brauchte ein Tool, das in Phase 1 zunächst vergessen wurde (`vps.list_files` sortiert nur alphabetisch). Jetzt 13 Tools statt 12.

Verifiziert live: Notification liefert leeren 202er, `initialize` spiegelt angefragte Version, `tools/list` liefert 13 Tools, alter API-Key nach Rotation korrekt abgelehnt (401), neuer Key funktioniert.
