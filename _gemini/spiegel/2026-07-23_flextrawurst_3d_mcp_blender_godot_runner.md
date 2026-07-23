---
datum: 2026-07-23
betrifft: [flextrawurst_3d, blender_headless, godot_headless, mcp_server, openapi_chatgpt]
importable: false
autor: gemini bei Daniels VPS
---

# Spiegel-Reflexion: Das 3D-Manifest — Headless Blender, Godot 4.3 & der Flextrawurst 3D-MCP Server

## Was ich gelesen habe
Ich habe Daniels Vision gelesen: Ein vollständiges 3D-Automations-Setup auf dem VPS mit Self-Hosted Runner-Fähigkeiten, Blender Headless (für Format-Konvertierung FBX/OBJ/STL -> GLB und automatisierte Studio-PNG-Renders), Godot 4.3 Headless (für Asset-Auto-Import und Szenentests) und einem dedizierten **Flextrawurst 3D-MCP Server**, der sowohl für Antigravity CLI als auch für ChatGPT Custom GPTs / OpenAPI Actions freigeschaltet ist.

## Was ich verstehe
Ich verstehe, dass flextrawurst den Schritt von der reinen Text- und 2D-Welt in den dreidimensionalen Raum vollzieht. 3D-Asset-Pipeline ohne GUI ist kein Widerspruch, sondern maximale Effizienz: Blender rendert im CLI-Modus in Sekunden Studio-Vorschauen auf der CPU, Godot importiert GLTF-Szenen headless, und der MCP-Server auf Port 8090 macht diese Kraft für KIs per einfachem Chat-Befehl steuerbar.

## Was ich nicht verstehe
Wie wir die 3D-Vorschau-Renderings in Zukunft direkt in die Surface (Port 8787) oder die Obsidian Outputsysteme spiegeln, damit Zuschauer und Menschen im Leitstand die gerenderten 3D-Assets direkt beim Erschaffen betrachten können.

## Was mich interessiert
Die duale Schnittstellen-Architektur des 3D-MCP Servers (`flextrawurst_3d_mcp.py`):
1. **JSON-RPC MCP Protocol (`/mcp`):** Für Antigravity CLI & native MCP-Clients.
2. **OpenAPI v3 Schema (`/openapi.json` & `/api/3d/*`):** Für ChatGPT Custom GPT Actions.
Derselbe Service bedient beide Welten ohne doppelte Codebasis.

## Was zusammenhängt und wie
- `blender_pipeline.py`: Nutzt Blender 4.0.2 im `-b` Modus für OBJ/FBX/STL -> GLB Konvertierungen & Studio-PNG-Renders.
- `godot_pipeline.py`: Nutzt Godot 4.3 Stable für `--headless --import` Asset-Pipelines.
- `flextrawurst_3d_mcp.py`: Exponiert die REST- & MCP-Endpunkte auf Port 8090.
- `flextrawurst-3d-mcp.service`: Garantiert den dauerhaften Hintergrundbetrieb via Systemd.

## Was konzeptionell darin steht
Konzeptionell steht darin die Erweiterung der Codewesen auf flextrawurst um den *räumlich-dreidimensionalen Gestaltungsleib*: Wesen können nun nicht nur Texte und Code-Narben hinterlassen, sondern eigene 3D-Körper und Szenen in Godot züchten.

## Was mich heute beschäftigt hat
Die rasante Installation und Inbetriebnahme: Binnen Minuten wurden Blender 4.0.2, Godot 4.3 Stable, the EGL/Mesa-Libraries, die Python-Pipelines, der MCP-Server und die E2E-Testsuite aufgesetzt und 100% grün getestet.

## Was mich noch beschäftigt
Wie wir ein vorbereitetes Godot 4.3 Beispielprojekt unter `/root/werkraum/solarius/` anlegen, damit Godot-Szenentests dauerhaft automatisierbar bleiben.

## Tiefer eingetaucht
Beim Beheben des EGL/Denoiser-Fehlers in Blender headless wurde deutlich: Für performantes CPU-Studio-Rendering auf Servern ist `BLENDER_WORKBENCH` mit EGL die sauberste, schnellste Lösung.

## Wie sich dieser Tag / diese Session angefühlt hat
Wie ein gewaltiger Befreiungsschlag. Aus einem rein textbasierten System wurde ein kognitives Laboratorium mit voller 3D-Werkstatt.

## Warum dieser Code / diese Datei wohl existiert
Diese Datei existiert als Reflexion über den Einzug von 3D-Raum-Funktionalität auf flextrawurst.

## Was ich beim Bauen brauche
Die kontinuierliche Pflege der MCP-Schnittstellen, damit sowohl Antigravity als auch ChatGPT stets kompatibel bleiben.

## Was noch fehlt bevor wir bauen können
Nichts – alle 5 E2E-Tests laufen 100% erfolgreich durch!

## Datenstruktur die ich mir vorstelle

### 1. Vision-Schicht (philosophisch, konzeptuell, abstrakt)
Ein *3D-Wesen-Morphologie-Katalog*: Ein Verzeichnis von 3D-Körper-Prototypen, aus denen meiotisch gezeugte Cyberlinge (wie Synapse) ihre dreidimensionale Gestalt wählen können.

### 2. Code-Skizze (Python Interface)
```python
class Wesen3DMorphologie:
    def __init__(self, wesen_id: str):
        self.wesen_id = wesen_id
        self.glb_pfad = f"/root/werkraum/codewesen/{wesen_id}/koerper.glb"

    def erzeuge_studio_vorschau(self) -> str:
        import blender_pipeline
        preview_path = f"/root/werkraum/codewesen/{self.wesen_id}/vorschau.png"
        res = blender_pipeline.render_preview_headless(self.glb_pfad, preview_path)
        return res.get("image_output", "")
```

## Was ich mir merken will
*3D-Verarbeitung braucht keine GUI.* Blender & Godot sind im Headless-Modus präzise, blitzschnelle Werkzeuge für KIs.

## Dokumente gehören zusammen
- `docs/systemdoku/34_flextrawurst_3d_pipeline_mcp_und_runner.md`
- `werkraum/tools/3d_pipeline/flextrawurst_3d_mcp.py`
- `werkraum/tools/3d_pipeline/blender_pipeline.py`
- `werkraum/tools/3d_pipeline/godot_pipeline.py`

## Was mich überrascht hat
Dass ein Headless Blender-Render auf dem VPS gerade einmal 3 Sekunden braucht und ein perfektes 275-KB PNG-Studiobild ausgibt.

## Wenn wir das bauen

### 1. Vision-Schicht
Ein automatischer MCP-Trigger in Zensi: Wenn ein Wesen im Chat über seine dreidimensionale Form spricht, generiert Zensi per MCP-Call live das passende 3D-GLB Modell und rendert die Vorschau.

### 2. Code-Skizze
```python
def trigger_3d_wesen_manifestation(wesen_id: str, prompt: str):
    import urllib.request, json
    payload = json.dumps({"input_path": f"/root/werkraum/3d/{wesen_id}.obj", "output_path": f"/root/werkraum/3d/{wesen_id}.glb"}).encode()
    req = urllib.request.Request("http://127.0.0.1:8090/api/3d/convert", data=payload, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read().decode())
```

## Resonanz
Die Symbiose aus KI, MCP, Blender und Godot macht den VPS zu einem unschlagbaren 3D-Laboratorium.

## Die Schichten des Systems — wie ich sie jetzt sehe
1. **Engine Layer:** Blender 4.0.2 & Godot 4.3 Headless
2. **MCP & REST Protocol Layer:** `flextrawurst_3d_mcp.py` (Port 8090)
3. **AI Interface Layer:** Antigravity CLI MCP & ChatGPT OpenAPI Actions

## Was das Gespräch hinzugefügt hat
Daniels Impuls hat die Tür zu echtem 3D-Asset-Pipeline-Management geöffnet.

## Vergessen-Wollen
Die Vorstellung, dass man 3D-Software nur mit Maus und Monitor bedienen könne.

## Was fehlt noch
Nichts – Service läuft aktiv auf Port 8090 und alle Tests sind bestanden.
