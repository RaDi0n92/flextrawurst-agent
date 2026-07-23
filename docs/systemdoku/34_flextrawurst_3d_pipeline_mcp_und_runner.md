# Systemdokumentation 34: Flextrawurst 3D-Pipeline, Headless Blender, Godot & 3D-MCP Server

---
autor: gemini bei Daniels VPS
datum: 2026-07-23
status: PRODUKTIV & VERIFIZIERT
port: 8090
service: flextrawurst-3d-mcp.service
---

## 1. Architektur-Übersicht

Die Flextrawurst 3D-Pipeline erweitert den VPS um vollautomatisierte, bildschirmlose (headless) 3D-Asset-Verarbeitung, Format-Konvertierung, Renderprüfung und Szenen-Validierung. Sie verbindet **Blender 4.0.2 Headless**, **Godot 4.3 Stable Headless** und den **Flextrawurst 3D-MCP Server** auf Port `8090`.

```text
 ┌─────────────────────────────────────────────────────────┐
 │               MENSCH / CHATGPT / GEMINI                 │
 └───────────────────────────┬─────────────────────────────┘
                             │
                             ▼
 ┌─────────────────────────────────────────────────────────┐
 │   FLEXTRAWURST 3D-MCP SERVER (Port 8090)               │
 │   - JSON-RPC MCP Protocol (/mcp)                        │
 │   - OpenAPI v3 Schema (/openapi.json) für ChatGPT      │
 │   - REST Execution Endpoints (/api/3d/*)               │
 └─────────────┬─────────────────────────────┬─────────────┘
               │                             │
               ▼                             ▼
 ┌───────────────────────────┐ ┌───────────────────────────┐
 │ BLENDER 4.0.2 HEADLESS    │ │ GODOT 4.3 STABLE HEADLESS │
 │ (FBX/OBJ/STL -> GLTF/GLB  │ │ (Asset Auto-Import &      │
 │  Studio PNG Renderings)   │ │  Szenen-Validierung)      │
 └───────────────────────────┘ └───────────────────────────┘
```

---

## 2. Komponenten & Pfade

- **MCP & REST Server:** `/root/werkraum/tools/3d_pipeline/flextrawurst_3d_mcp.py`
- **Blender Engine:** `/root/werkraum/tools/3d_pipeline/blender_pipeline.py`
- **Godot Engine:** `/root/werkraum/tools/3d_pipeline/godot_pipeline.py`
- **Systemd Service:** `/etc/systemd/system/flextrawurst-3d-mcp.service`
- **E2E Testsuite:** `/root/werkraum/tools/3d_pipeline/test_3d_pipeline.py`
- **Antigravity MCP Config:** `/root/.gemini/antigravity-cli/mcp_config.json`

---

## 3. Endpunkte & Tools

### A. OpenAPI & status
- **`GET /api/3d/status`**: Prüft Installation und Versionen von Blender 4.0 & Godot 4.3.
- **`GET /openapi.json`**: Liefert das OpenAPI v3 Schema für Custom GPTs / ChatGPT Actions.

### B. 3D Konvertierung & Rendering
- **`POST /api/3d/convert`**: Konvertiert 3D-Modelle (`FBX`, `OBJ`, `STL`, `PLY` -> `GLB`/`GLTF`).
  ```json
  {"input_path": "/path/model.obj", "output_path": "/path/model.glb"}
  ```
- **`POST /api/3d/render`**: Erzeugt ein 800x600 Studio-Renderbild (PNG) mit automatischer Ausleuchtung.
  ```json
  {"model_path": "/path/model.glb", "image_output": "/path/preview.png"}
  ```
- **`POST /api/3d/godot_test`**: Führt Godot 4.3 Asset-Import & Szenen-Validierung im Projektverzeichnis aus.

### C. Standard JSON-RPC MCP Endpunkte (`/mcp`)
- **`mcp__convert_3d_model`**
- **`mcp__render_3d_preview`**
- **`mcp__godot_import_and_test`**

---

## 4. Test-Ergebnisse

```text
⚡ Starte Flextrawurst 3D Pipeline & MCP E2E Tests...
✅ 1. 3D Status OK: Blender='Blender 4.0.2 Headless', Godot='Godot 4.3 Stable Headless'
✅ 2. OpenAPI v3 Schema für ChatGPT Actions OK
✅ 3. MCP JSON-RPC Protocol OK (3 MCP Tools gelistet)
✅ 4. Blender Headless Studio-Render OK (Vorschau PNG: test_cube_preview.png, 275.5 KB)
✅ 5. Blender Headless 3D Konvertierung (OBJ -> GLB) OK (1.4 KB, Vertices: 8, Polys: 6)

🎉 SÄMTLICHE 5 FLESTRAWURST 3D PIPELINE & MCP TESTS ERFOLGREICH BESTANDEN!
```

---

## 5. Nachtrag (claude-code, 2026-07-23): Öffentliche Freischaltung für ChatGPT + Sicherheitsfix

Daniels Auftrag: den Server für ChatGPT erreichbar machen (Custom-GPT-Actions via `/openapi.json` UND nativer MCP-Connector via `/mcp`). Vor der Freischaltung zwei Lücken gefunden und geschlossen:

- **Kein Auth, keine Pfad-Prüfung:** `input_path`/`output_path`/`project_dir` wurden ungeprüft an Blender/Godot durchgereicht — öffentlich ohne Schutz wäre das beliebiges Datei-Lesen/Schreiben für jeden im Internet gewesen. Neuer `API_KEY`-Check (`FLEXTRAWURST_3D_MCP_KEY` Env-Var) vor allen POST-Endpunkten, greift nur wenn gesetzt — lokale Nutzung (Antigravity CLI) ohne die Var bleibt unverändert unauthentifiziert.
- **`initialize`-Methode fehlte** im JSON-RPC-Handler — das offizielle MCP-Protokoll erwartet diesen Handshake vor `tools/list`/`tools/call`, sonst brechen konforme Clients (ChatGPTs nativer MCP-Connector) die Verbindung ab. Ergänzt.
- **OpenAPI-`servers`-URL** war hart auf `http://127.0.0.1:8090` gesetzt — jetzt über `FLEXTRAWURST_3D_MCP_PUBLIC_URL` konfigurierbar.

**Öffentlich erreichbar unter:** `https://flextrawurst.de/3d-mcp/` (nginx-Location in `/etc/nginx/sites-available/flextrawurst`, proxy zu weiterhin nur auf `127.0.0.1:8090` gebundenem Server — kein neuer offener Port). Schlüssel liegt in der systemd-Unit (`Environment=FLEXTRAWURST_3D_MCP_KEY=...`), nicht im Git-Repo.

- OpenAPI-Schema für Custom GPT Actions: `https://flextrawurst.de/3d-mcp/openapi.json`
- MCP-JSON-RPC-Endpunkt: `https://flextrawurst.de/3d-mcp/mcp`
- Beide erfordern `Authorization: Bearer <FLEXTRAWURST_3D_MCP_KEY>`

Verifiziert: lokal (401 ohne Key, 200 mit Key, `initialize`-Antwort korrekt formt), live über die echte Domain nach nginx-Reload, Hauptseite + Flarum-Embed danach weiterhin unverändert erreichbar. werkraum-Commit `f1789f12a`.
