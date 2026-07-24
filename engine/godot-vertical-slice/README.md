# Flextrawurst · Godot Engine Vertical Slice 001

## Richtiger Arbeitskörper

Dieser Engine-Ring liegt bewusst in `RaDi0n92/flextrawurst-agent`.

- `RaDi0n92/Flextrawurst` = öffentlicher Beschreibungs-, Dokumentations- und Plattformspurenkörper.
- `RaDi0n92/flextrawurst-agent` = Arbeits-, Agenten-, Spiel-, 3D-, 2D-, Screenshot-, MCP- und Enginekörper.

Der zuerst versehentlich im öffentlichen Beschreibungsrepo angelegte Draft wurde geschlossen, nicht gemerged und dessen Branch auf den unveränderten Hauptstand zurückgesetzt.

## Verifizierter Realstatus

Der korrigierte VPS-äquivalente Rundlauf ist mit Godot 4.3 vollständig bestanden:

- Deployment- und MCP-Verträge: **PASS**
- Bash- und Python-Körper: **PASS**
- Godot-Bridge standardmäßig auf `127.0.0.1:18092`: **PASS**
- bewusste Ablehnung der reservierten Ports 8090 und 8091: **PASS**
- GLB direkt aus dem MCP-tauglichen Base64-Textkörper geladen: **PASS**
- GLB-Rekonstruktion und SHA-256: **PASS**
- Godot-4.3-Import: **PASS**
- Struktur und Provenienz: **PASS**
- Godot → Bridge → append-only JSONL → Cursor/Hash: **PASS**
- sichtbarer PNG-Screenshot über Xvfb: **PASS**

Beweisanker:

- Workflow Run: `30134100750`
- Proof Artifact: `8612169203`
- Artifact Digest: `sha256:464ce3f27bfe4eea89e4c27c0e837e1b8d77c4e34317a9fd4a7b3bc1d283fa3b`
- Alleswisser-Asset-ID: `alleswisser.asset.3d.test-cube.001`
- GLB SHA-256: `ca481b86fb41d80f59af4b3714ea34c0798adf2acd9d871d4bf563861e17ca00`

Das ist ein belastbarer VPS-äquivalenter Beweis. Es ist noch keine behauptete tatsächliche Installation auf Daniels VPS, solange der VPS-Werkzeugkörper in der ausführenden Chat-Sitzung nicht als aufrufbarer Tool-Namespace vorliegt und die realen Zielpfade danach nicht zurückgelesen wurden.

## Korrigierter VPS-Fund: Port 8091 war falsch

Die erste Einzugsfassung wollte die Godot-Bridge auf Port 8091 starten. Der reale VPS-Abgleich zeigte:

```text
8090 = bestehende Flextrawurst-3D-MCP-Schicht
8091 = bestehender produktiver 95-Tool-VPS-MCP
18092 = neuer lokaler Godot-Bridge-Standard
```

Der alte CI-Lauf hatte die Kollision nicht gesehen, weil er einen isolierten Ersatzport verwendete. Die Korrektur steckt jetzt unabhängig in:

- Bridge-Server,
- systemd-Unit,
- Root-Shell-Installer,
- VPS-Verifikator,
- ChatGPT-MCP-Ausführungsvertrag,
- CI-Gegenprobe.

Der Bridge-Server beendet sich absichtlich mit Fehler, falls 8090 oder 8091 trotzdem eingetragen werden.

## Zwei getrennte VPS-Einzugswege

### 1. ChatGPT-VPS-MCP

Der reale 95-Tool-MCP kann unter `/root/werkraum` lesen, neue Dateien schreiben und vorhandene gezielt editieren. Er darf nicht stillschweigend als Root-Shell behandelt werden.

Der MCP-Einzug verwendet deshalb:

- `vps.read_file`,
- `vps.file_metadata`,
- `vps.write_file`,
- `vps.edit_file`,
- Asset-Metadaten-, Validierungs-, Vorschau- und Downloadwerkzeuge,
- die getrennte vorhandene 3D-MCP-Schicht für Godot-Import und Szenentest.

Die vollständige Arbeitsfolge steht in:

```text
engine/godot-vertical-slice/deploy/MCP_DEPLOYMENT_PLAN.json
```

Der GLB-Körper muss dabei nicht binär übertragen oder per Shell dekodiert werden. `assets/test_cube.glb.b64` bleibt eine normale Textdatei; Godot 4.3 lädt die dekodierten Bytes zur Laufzeit über `GLTFDocument`.

Ein erfolgreicher MCP-Datei- und Godot-Einzug bedeutet noch nicht automatisch, dass ein persistenter Bridge-Dienst läuft. Dafür braucht es einen real gestarteten Prozess oder den zweiten Einzugsweg.

### 2. Root-Shell-Installer

Der Root-Shell-Installer liegt unter:

```text
engine/godot-vertical-slice/deploy/vps_install.sh
```

Er erledigt:

1. Bestandsprüfung und Snapshot,
2. isolierten Sparse-Checkout,
3. Asset- und Hashprüfung,
4. atomaren Projektwechsel,
5. Runtime-Override auf `127.0.0.1:18092`,
6. Installation der gehärteten systemd-Unit,
7. Prüfung der vorhandenen 3D-Pipeline,
8. Godot-/Bridge-/GLB-/Screenshotbeweis,
9. Installationsmanifest und SHA-256-Summen,
10. automatischen Rollback bei Fehlern.

Dieser Weg setzt echte Root-Shell- und systemd-Rechte voraus. Der normale ChatGPT-VPS-MCP besitzt sie nicht und behauptet sie deshalb auch nicht.

## Zielpfade auf dem VPS

```text
/root/werkraum/engine/godot-vertical-slice
/root/werkraum/engine_runtime/godot-vertical-slice
/root/werkraum/backups/godot-vertical-slice/<UTC-Zeitstempel>
/etc/systemd/system/flextrawurst-godot-world-bridge.service   # nur Root-Shell-Weg
```

Unberührt bleiben:

```text
/root/werkraum/tools/3d_pipeline
flextrawurst-3d-mcp.service
vps-mcp.service
Port 8090
Port 8091
Single-HTML-Spielkörper
```

## Enthaltener Engine-Körper

- echtes `project.godot`, kompatibel zur VPS-Linie Godot 4.3,
- echte 3D-Szene,
- `CharacterBody3D`, Kamera, Boden und Kollision,
- deterministische Bewegung,
- GLB mit stabiler Alleswisser-ID und Quellprovenienz,
- binärer Importweg und MCP-tauglicher Text-only-Ladeweg,
- sicherer Grundseed plus separater Runtime-Override,
- bidirektionaler HTTP-Bridge-Adapter,
- localhost-only append-only Bridge,
- Cursor, Ereignis-Hash und Welt-ID-Prüfung,
- Headless-, Import-, Bridge-, Provenienz-, Text-only- und Screenshottests,
- atomarer Root-Shell-Installer mit Snapshot und Rollback,
- eigenständiger VPS-Verifikator,
- exakter MCP-Einzugsplan.

## Harte Grenzen

- Keine erfundenen Live-VPS-Daten.
- Keine automatische Kanonisierung empfangener Ereignisse.
- Keine Aktivierung von Codewesen.
- Keine Änderung am bestehenden Single-HTML-Spiel.
- Keine Engine-Implementierung im öffentlichen Beschreibungsrepo.
- Keine Belegung der Ports 8090 oder 8091.
- Keine öffentliche Bridge ohne späteren eigenen Authentifizierungsring.
- Platzhaltergeometrie ist kein realer Schwelm-Import.
- CI-Beweis, MCP-Dateiübertragung, Godot-Prüfung und systemd-Aktivierung bleiben getrennte Wahrheitszustände.

## Noch nicht behauptet

- kein vollständiges Flextrawurst-Godot-Spiel,
- kein real importiertes Stadtmodell,
- noch keine in dieser Sitzung auf Daniels VPS zurückgelesene Installation,
- noch kein real bestätigter persistenter Bridge-Prozess auf Daniels VPS,
- kein öffentlicher Netzwerkkanal,
- kein Webexport,
- kein vollständiges Physik-, Quest- oder AI-System,
- kein menschlicher Spielbeweis.
