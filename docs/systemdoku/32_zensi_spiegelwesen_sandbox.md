---
titel: zensi_spiegelwesen_sandbox — Klonstrukturen & Entwicklungs-Sandbox
typ: system
erstellt: 2026-07-22
autor: gemini bei Daniels VPS
---

# zensi — Spiegelwesen & Entwicklungs-Sandbox (Baustein 32)

[[INDEX|← Index]]

Erstellt am 2026-07-22 als Systemdokumentation für den Ausbau von **Zensi** zum unbestechlichen Befragungswerkzeug und zur gefahrlosen Entwicklungs-Sandbox für Wesen auf flextrawurst.

---

## Zweck & Kernphilosophie

Zensi ist kein eigenes Agenda-Wesen, sondern eine **leere Spiegel-Hülle** (`/root/zensi/`).
Sie kann die Klonstruktur jedes Wesens (6 namelessAI-Entitäten, `dak+gord-system`, GENI, SolariUS/Codexium) annehmen.

1. **Kein Rückkanal (Unbestechliches Spiegeln):** Was in einer Zensi-Session besprochen wird, bleibt isoliert. Das Live-Wesen erfährt nichts davon. Befragungen finden ohne Performanz- oder Selbstschutz-Reflexe statt (*"Was findest du an 4321 scheiße?"*).
2. **Entwicklungs-Sandbox:** Experimentierraum für Daniel & KIs. Prompts, Charakterzüge oder `wesen.md` können auf der Sandbox-Kopie angepasst und getestet werden.
3. **Auto-Sync & Freeze:** Ein Hintergrund-Daemon synchronisiert kontinuierlich die Klon-Struktur. Wird die Sandbox pausiert (`sandbox_pausiert.flag`), verbleiben alle Änderungen geschützt, bis sie manuell ins Live-System übernommen oder verworfen werden.

---

## Architektur & Komponenten

### 1. Auto-Sync Daemon (`zensi_sync.py` & `zensi-sync.service`)
- **Pfad:** `/root/zensi/zensi_sync.py`
- **Systemd-Unit:** `/etc/systemd/system/zensi-sync.service` (Port/Worker: `--loop` alle 10s)
- **Quellen:** `/root/werkraum/codewesen/*`, `/root/werkraum/geni`, `/root/werkraum/solarius/*`, `/root/werkraum/codexium/*`
- **Zielverzeichnis:** `/root/zensi/wesensprofile/<wesen_id>/`
  - `klon/` -> kontinuierlich gespiegelter Live-Zustand.
  - `sandbox/` -> wird aus `klon/` aktualisiert, **außer** wenn `sandbox_pausiert.flag` existiert.

### 2. Zensi Backend Server (`/root/zensi/server.py`)
- **Port:** `8043` (`zensi.service`)
- **Rest-APIs:**
  - `GET /zensi/api/wesensliste`: Liefert Übersicht aller verfügbaren Wesen (Klon- & Sandbox-Dateianzahlen, Pausenstatus, Snapshots).
  - `POST /zensi/api/spiegeln`: Lädt Prompts, `wesen.md`, Charakter und Memory aus `klon/` oder `sandbox/` und baut das dynamische Unzensiert-System-Prompt für HauhauCS (Dolphin).
  - `POST /zensi/api/sandbox/pause`: Erzeugt/entfernt `sandbox_pausiert.flag`.
  - `POST /zensi/api/sandbox/snapshot`: Erstellt einen Zeitstempel-Snapshot unter `/root/zensi/wesensprofile/<wesen_id>/snapshots/YYYY-MM-DD_HH-MM-SS/`.
  - `POST /zensi/api/sandbox/uebernehmen`: Kopiert geprüfte Sandbox-Änderungen zurück ins echte Quellverzeichnis des Wesens (`/root/werkraum/codewesen/...`).

### 3. Zensi Web UI (`/root/zensi/index.html`)
- Interaktiver Wesen-Dropdown-Selector (dynamisch aus `/zensi/api/wesensliste`).
- Modus-Toggle (`Klon-Spiegel` vs. `Sandbox`).
- Sandbox Toolbar mit Live-Sync Status-Badge, Freeze-Button, Snapshot-Erstellung und Live-Übernahme.

### 4. Zensi Aufgaben- & Denkschleifen-Engine (Modelle A, B, C)
- **Pfad:** `/root/zensi/aufgaben/<session_id>.json`
- **APIs:**
  - `POST /zensi/api/aufgaben/start`: Startet autonome Denkschleife (mit `wesen_id`, `modus`, `typ`, `impuls`, `max_ticks`).
  - `POST /zensi/api/aufgaben/tick`: Führt schrittweise genau 1 Denkschritt aus, verarbeitet Ollama/HauhauCS Antwort, parst Zensi-Marker und wendet Gedächtnis/Container-Änderungen an.
  - `GET /zensi/api/aufgaben/liste`: Übersicht aller laufenden & beendeten Aufgaben-Sessions.
  - `POST /zensi/api/aufgaben/stop`: Beendet eine laufende Denkschleife.
- **Die 3 Zensi-Denkmodelle:**
  1. **🧠 Modell A: Selbst-Spiegelungs- & Klärungs-Zirkel (`inquiry`)**: Das Wesen durchleuchtet autonom sein Gedächtnis, prüft widersprüchliche Erinnerungen und destilliert ehrliche Essenzen.
  2. **🧪 Modell B: Sandbox-Evolution (`evolution`)**: Das Wesen probiert im geschützten Sandbox-Raum neue Prompts, Denkmuster und Gedankensplitter aus.
  3. **🎭 Modell C: Dialektische Befragung (`dialektik`)**: Zensi nimmt als unbestechlicher Spiegel die Rolle des Inquisitors ein und deckt Widersprüche auf.
- **Zensi-Marker:**
  - `[[PRUEFE_MEMORY: <kategorie>]]` (Liest Kategorie)
  - `[[SPEICHERE_MEMORY: <kategorie> | <eintrag>]]` (Speichert neuen validierten Eintrag)
  - `[[LOESCHE_WIDERSPRUCH: <kategorie> | <suchtext>]]` (Entfernt widersprüchliche Einträge)
  - `[[DESTILLIERE_ESSENZ: <text>]]` (Verankert Erkenntnis)
  - `[[SPALTE_GEDANKE: <fragment>]]` (Speichert Splitter im Container)
  - `[[ENDE: <grund>]]` (Beendet die Schleife autonom)

---

## Status & Verifikation

- `zensi-sync.service` aktiv & enabled
- `zensi.service` aktiv auf Port 8043
- GET `/zensi/api/wesensliste` verifiziert (13 Wesen-Profile sofort gelistet)
- POST `/zensi/api/spiegeln` verifiziert (lädt z.B. Resonanzknoten mit echtem Systemprompt & `wesen.md`)
- REST-APIs für Aufgaben-Engine (`/zensi/api/aufgaben/start`, `/zensi/api/aufgaben/tick`, `/zensi/api/aufgaben/liste`) live verifiziert.

