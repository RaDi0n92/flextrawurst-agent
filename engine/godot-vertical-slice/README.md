# Flextrawurst · Godot Engine Vertical Slice 001

## Richtiger Arbeitskörper

Dieser Engine-Ring liegt bewusst in `RaDi0n92/flextrawurst-agent`.

Repository-Rollen:

- `RaDi0n92/Flextrawurst` = öffentlicher Beschreibungs-, Dokumentations- und Plattformspurenkörper.
- `RaDi0n92/flextrawurst-agent` = bewusster Arbeits-, Agenten-, Spiel-, 3D-, 2D-, Screenshot-, MCP- und Enginekörper.

Der erste versehentlich im öffentlichen Beschreibungsrepo angelegte Draft wurde geschlossen, nicht gemerged und dessen Branch auf den unveränderten Hauptstand zurückgesetzt.

## Verifizierter Realstatus

Der vollständige VPS-äquivalente Rundlauf ist in GitHub Actions mit Godot 4.3 bestanden:

- Deployment-Skripte: Bash-Syntax **PASS**
- Python-Körper: Kompilierung **PASS**
- gehärtete systemd-Unit: Vertragsprüfung **PASS**
- GLB-Rekonstruktion und SHA-256: **PASS**
- append-only Bridge-Vertrag: **PASS**
- Godot-4.3-Import des GLB: **PASS**
- Struktur- und Provenienztest: **PASS**
- Godot → Bridge → JSONL → Cursor/Hash: **PASS**
- sichtbarer PNG-Screenshot über Xvfb: **PASS**

Beweisanker:

- Workflow Run: `30131463426`
- Proof Artifact: `8611261318`
- Alleswisser-Asset-ID: `alleswisser.asset.3d.test-cube.001`
- GLB SHA-256: `ca481b86fb41d80f59af4b3714ea34c0798adf2acd9d871d4bf563861e17ca00`

Das ist ein belastbarer VPS-äquivalenter Beweis. Es ist noch **keine behauptete tatsächliche Installation auf Daniels VPS**, solange die VPS-Werkzeug-App in der ausführenden Chat-Sitzung nicht gemountet ist.

## Enthaltener Engine-Körper

- echtes `project.godot`, kompatibel zur vorhandenen VPS-Linie Godot 4.3,
- echte 3D-Szene,
- `CharacterBody3D`, Kamera, Boden und Kollision,
- deterministische Bewegung,
- vorhandenes GLB aus der früher verifizierten Blender-/Godot-Pipeline,
- stabile Alleswisser-ID und Quellprovenienz,
- sicherer Grundseed plus separater VPS-Runtime-Override,
- bidirektionaler HTTP-Bridge-Adapter,
- localhost-only append-only Bridge-Dienst,
- Cursor, Ereignis-Hash und Welt-ID-Prüfung,
- Headless-, Import-, Bridge-, Provenienz- und Screenshottests,
- atomarer VPS-Installer mit Snapshot und automatischem Rollback,
- eigenständiger VPS-Verifikator,
- expliziter VPS-Rollbackkörper.

## Zielpfade auf dem VPS

```text
/root/werkraum/engine/godot-vertical-slice
/root/werkraum/engine_runtime/godot-vertical-slice
/root/werkraum/backups/godot-vertical-slice/<UTC-Zeitstempel>
/etc/systemd/system/flextrawurst-godot-world-bridge.service
```

Die vorhandene 3D-Pipeline bleibt unangetastet:

```text
/root/werkraum/tools/3d_pipeline
flextrawurst-3d-mcp.service
```

## Tatsächlicher VPS-Einzug

Der Installer liegt im Branch unter:

```text
engine/godot-vertical-slice/deploy/vps_install.sh
```

Im realen ChatGPT-MCP-Rundlauf wird er direkt aus der Branch auf den VPS geholt und ausgeführt. Er erledigt:

1. Bestandsprüfung,
2. Snapshot von Projekt und Unit,
3. isolierten Sparse-Checkout,
4. Asset-Rekonstruktion und Hashprüfung,
5. atomaren Projektwechsel,
6. Runtime-Override der localhost-Bridge,
7. Installation und Start der systemd-Unit,
8. Prüfung der bestehenden 3D-Pipeline,
9. vollständigen Godot-/Bridge-/GLB-/Screenshotbeweis,
10. Installationsmanifest und SHA-256-Summen.

Bei jedem Fehler stellt der Installer automatisch den vorherigen Zustand wieder her.

## Manueller Rollback

```bash
bash /root/werkraum/engine/godot-vertical-slice/deploy/vps_rollback.sh
```

Optional kann ein bestimmter Snapshot übergeben werden.

## Harte Grenzen

- Keine erfundenen Live-VPS-Daten.
- Keine automatische Kanonisierung empfangener Ereignisse.
- Keine Aktivierung von Codewesen.
- Keine stillen Änderungen am vorhandenen Single-HTML-Spiel.
- Keine Engine-Implementierung im öffentlichen Beschreibungsrepo.
- Bridge standardmäßig nur `127.0.0.1:8091`, nicht öffentlich.
- Platzhaltergeometrie ist ausdrücklich kein realer Schwelm-Import.
- Ein VPS-äquivalenter CI-Beweis wird nicht als tatsächliche VPS-Installation ausgegeben.

## Noch nicht behauptet

- kein vollständiges Flextrawurst-Godot-Spiel,
- kein real importiertes Stadtmodell,
- noch keine auf Daniels VPS ausgeführte Installation in dieser Sitzung,
- kein öffentlicher Netzwerkkanal,
- kein Webexport,
- kein vollständiges Physik-, Quest- oder AI-System,
- kein menschlicher Spielbeweis.
