# agent/dak_gord_system/ollama_chat.py

Migriert: 2026-07-06

**Was es tut**: Das zentrale LLM-Interface für dak+gord-system (Daniels direkter
Gesprächspartner-Agent) — `ollama_chat()` unterstützt: Streaming mit Token-Callback,
Tool-Calling (`datei_lesen`, `datei_schreiben`, `python_code_ausfuehren`), Vision
(Bild-Anhang), und ein 4-stufiges Modell-Routing (`waehle_modell()` wählt per
Keyword-Heuristik zwischen "schnell"/"mittel"/"tief"/"qwen" je nach Frageinhalt).

**Wozu**: dak+gord braucht mehr als reinen Chat — er liest/schreibt Dateien,
führt Code aus, sieht Bilder. Das Tool-Calling-Format unterscheidet sich
fundamental zwischen Ollama (`arguments` als dict) und OpenAI/llama-server
(`arguments` als JSON-**String**, muss geparst werden) — das war die technisch
heikelste Stelle der ganzen Migration.

**Bewusste Design-Entscheidung — "Freier Modus" bleibt auf Ollama**: Ein
separater Modus (`MODELL_FREI = "dolphin-mistral:7b"`, aktivierbar per `/frei`-
Befehl in `freier_modus.py`) ist ein eigenständiges, bereits unzensiertes Modell
für einen anderen Zweck — keine gemma4-Altlast. `ollama_chat()` prüft jetzt:
ist das gewählte Modell `MODELL_FREI`? Dann alter Ollama-Pfad unverändert.
Sonst: neuer `hauhau_client`-Pfad. Die vier Tier-Konstanten (TIEF/MITTEL/
SCHNELL/QWEN) zeigen jetzt alle auf `hauhaucs-q6` — es gibt nur noch ein
"echtes" Modell, die Tier-Wahl bleibt als Interface bestehen, hat aber keine
unterschiedliche Wirkung mehr.

**Neue Hilfsfunktion in hauhau_client.py**: `chat_raw()` — gibt die volle
Response zurück statt nur `content`, weil Tool-Calls in `message.tool_calls`
stecken, nicht im normalen Text.

**Getestet**: Beide Pfade isoliert erfolgreich — Streaming-Chat ("Test" → "Test")
und Tool-Calling (Anfrage "lies /etc/hostname" → korrekt `##LESEN: /etc/hostname##`
erzeugt, JSON-String-Argumente korrekt geparst).

**Zusammenhang**: Genutzt von `web_chat.py` (`dak-gord-web.service`, Port-Chat-UI)
über `graphen/gespraechsgraf.py`. Live neu gestartet, Verlauf (36 Nachrichten)
korrekt wiederhergestellt.
