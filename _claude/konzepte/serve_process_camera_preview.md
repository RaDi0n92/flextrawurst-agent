# serve_process_camera_preview.ts (dolphin)

Migriert: 2026-07-06

**Was es tut**: Der große Preview-Server (Port 8787, 3105 Zeilen) hinter
"dolphin" — Daniels Haupt-Interaktions-Oberfläche mit Codewesen/Spawner-
Charakteren (solarius/solarius2/codexium/codexium2), inkl. Session-Verwaltung,
Anhänge (Bilder/Dokumente/URL/Audio), Gedächtnis-Extraktion, Gesprächsabschlüsse,
Live-Streaming-Chat mit Abbruch-Unterstützung.

**7 Ollama-Aufrufstellen gefunden, 6 migriert, 1 bewusst nicht**:
1. Bild-Beschreibung via `VISION_MODEL` (kleines 4,5B-Modell) — **bleibt auf Ollama**,
   siehe eigener Konzept-Absatz unten.
2. Gedächtnis-Extraktion (`runAbschlussJob`-Nachbar, JSON-Antwort) → `hauhau_client.chat()`
3. Gesprächsabschluss-Text (`runAbschlussJob`) → `hauhau_client.chat()`
4. Modell-Umschalt-Endpunkt (`/dolphin/api/set-model` + `/dolphin/api/models`) — **entfernt**,
   gleiche Begründung wie bei zensi (nur noch 1 Modell, kein Dropdown mehr sinnvoll)
5. Haupt-Chat-Streaming (`/dolphin/chat`) → `hauhau_client.chatStream()`
6. Wesen-Chat-Streaming (`/{spawner}/{name}/chat`, mit Abbruch-Tracking über
   `aktiveGenerationen`-Map) → `hauhau_client.chatStream()`

**Warum VISION_MODEL nicht migriert wird**: Bewusste, dokumentierte Architektur-
Entscheidung von vor der Migration — das 35B-Hauptmodell brauchte auf reiner CPU
über 3 Minuten für ein Bild (nie zu Ende getestet), das kleine 4,5B-Modell schafft
dieselbe Beschreibung in ~14 Sekunden. Zwei-Schritt-Pipeline: kleines Modell
beschreibt das Bild als Text, das Hauptmodell bekommt nur den Text, nie die
Rohbilddaten. Bleibt unverändert auf Ollama (Port 11434) — hat nichts mit gemma4
zu tun und war schon vorher richtig gelöst.

**Wichtiger Nebenfund — entfernter toter Mechanismus**: `hauptmodellVoraussichtlichBlockiertBis`
war ein 90-Sekunden-Sperrzeitstempel, der nach jedem Bild-Upload gesetzt wurde,
weil früher Haupt- und Vision-Modell sich einen einzigen Ollama-Slot teilten
(`OLLAMA_MAX_LOADED_MODELS=1`) — Bild verarbeiten verdrängte das Hauptmodell aus
dem RAM, Neuladen dauerte ~40s. Seit das Hauptmodell auf einem eigenen
llama-server-Prozess (Port 11435) läuft, gibt es diese Verdrängung nicht mehr —
der Mechanismus wurde komplett entfernt (hätte sonst faelschlich alle 90s nach
jedem Bild-Upload "Hauptmodell lädt neu" gemeldet, obwohl das Hauptmodell nie
betroffen war).

**Bug gefunden + gefixt während des Live-Tests**: Der Wesen-Chat-Handler schickte
die SSE-Response-Header schon vor dem Streaming-Start, sein `onError`-Callback
hatte aber nur einen Fallback für "Header noch nicht gesendet" (503) — bei einem
echten Streaming-Fehler (siehe unten) blieb die Verbindung für den Client ohne
jede Antwort für immer offen hängen. Jetzt schreibt `onError` bei bereits
gesendeten Headern ein sauberes SSE-Fehlerereignis + `[DONE]` + `res.end()`.

**Wichtiger operativer Nebenfund (nicht behoben, nur entdeckt)**: llama-server
teilt `--ctx-size 12345` durch `--parallel 2` auf ~6400 Token **pro Slot** auf —
nicht die vollen 12345 wie angenommen. Ein Live-Test mit dem Spawncharakter
"Alex" (13234 Token Verlauf) schlug prompt mit `exceed_context_size_error` fehl.
Betrifft potenziell alle Wesen mit längeren Gesprächsverläufen, nicht nur dolphin.
Noch keine Entscheidung getroffen (mehr ctx-size = mehr RAM, weniger parallel =
weniger Gleichzeitigkeit) — mit Daniel zu klären.

**Zusammenhang**: `process-camera-preview.service`, neu gestartet, mehrere
Live-Tests erfolgreich (Haupt-Chat mit Token-Zählern, Wesen-Chat mit und ohne
Kontext-Überschreitung).
