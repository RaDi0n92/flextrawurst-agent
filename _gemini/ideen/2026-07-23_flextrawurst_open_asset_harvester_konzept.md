---
datum: 2026-07-23
betrifft: [flextrawurst_open_asset_harvester, github_actions, asset_zip, 3d_pipeline, chatgpt_action]
status: KONZEPT_UND_DOKUMENTIERT
autor: gemini bei Daniels VPS
---

# Konzept: Flextrawurst Open Asset Harvester & Automated Pipeline

## 1. Übersicht

Der **Flextrawurst Open Asset Harvester** ist ein automatisierter CI/CD- und PR-Workflow (GitHub Actions / Self-Hosted Runner), der offene 3D-Assets, Texturen und System-Objekte sammelt, durch die Flextrawurst 3D-Pipeline (Blender 4.0 & Godot 4.3 Headless) leitet, auf Daten-Integrität prüft und als gebündeltes Artefakt bereitstellt.

```text
 ┌──────────────────────────────────────────────────────────┐
 │          WORKFLOW: „Flextrawurst Open Asset Harvester“   │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ 1. CHECKOUT (grün)                                       │
 │    Quellcode & Harvester-Skripte auschecken               │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ 2. ERNTE & SAMMELN (grün)                                │
 │    Offene 3D-Assets / Texturen durchsuchen               │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ 3. HEADLESS VALIDIERUNG (3D-Pipeline Port 8090)          │
 │    - Blender Headless: GLB-Konvertierung & Mesh-Check    │
 │    - Godot 4.3 Headless: Asset-Import & Szenentest       │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ 4. UPLOAD & ARTEFAKT (aktiv)                             │
 │    Vorgesehener Artefaktname: FLEXTRAWURST_OPEN_ASSETS_V1.zip │
 └──────────────────────────────────────────────────────────┘
```

---

## 2. Kern-Kriterien & Qualitätsprinzip

- **Vollständige Überprüfbarkeit:** Der Workflow gilt erst dann als `erfolgreich / fertig`, wenn das ZIP-Artefakt `FLEXTRAWURST_OPEN_ASSETS_V1.zip` grün hochgeladen und wirklich als herunterladbarer Binärkörper vorliegt.
- **Keine Cloud-Dekoration:** Keine leeren Ausführungen oder hängenden YAML-Runner.
- **Symbiose mit ChatGPT & Antigravity:** ChatGPT (via OpenAPI Actions / MCP) oder Antigravity (via 3D-MCP auf Port 8090) lösen den Harvester aus und empfangen das valide ZIP.

---

## 3. Original-Protokoll des Impulses

> ***„Jetzt ja.** Vorher lief er tatsächlich nicht, trotz unseres geduldigen Anstarrens der YAML-Krähe.
> Ich habe den Auslöser repariert und einen beobachtbaren PR-Lauf gestartet. Der aktuelle Stand:
> * Workflow **„Flextrawurst Open Asset Harvester“**: `in_progress`
> * Sammeln und Validieren der offenen Assets: **erfolgreich abgeschlossen**
> * Hochladen des erzeugten Asset-ZIPs: **läuft gerade**
> * vorgesehener Artefaktname: `FLEXTRAWURST_OPEN_ASSETS_V1.zip`
> * Checkout: grün
> * Ernte: grün
> * Upload: aktiv
> Der Sammler hat die Dateien also bereits geholt und geprüft. Jetzt schiebt GitHub den Binärkörper nur noch ins Artefaktlager. **Fertig behaupte ich erst, wenn der Upload grün ist und das ZIP wirklich herunterladbar vorliegt.** Endlich arbeitet das Ding und starrt nicht nur dekorativ in die Cloud. 🔥“*
