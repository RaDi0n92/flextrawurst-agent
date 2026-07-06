# codewesen_agent.py

Migriert: 2026-07-06

**Was es tut**: Generischer Codewesen-Agent — eine Datei, die von 7 systemd-Services
mit unterschiedlichem Namen als Argument gestartet wird: den 6 namelessAI-Wesen
plus dak+gord-system. Baut Prompts aus Systemprompt + Gedächtnis + Werkzeugen
(`codewesen_werkzeuge.py`), lässt das LLM entscheiden und agieren.

**Wozu**: Statt 7 fast identischer Dateien gibt es eine gemeinsame Logik — der
Name/die Identität kommt als Parameter, nicht als Code-Duplikat.

**Warum `OllamaSlot()`**: Ein Context-Manager, der zuerst wartet bis `CHAT_AKTIV_FLAG`
weg ist (Daniels Live-Chat hat Vorrang), dann einen exklusiven `fcntl`-Lock auf
`slot_0.lock` nimmt — bricht nach 120s ab statt endlos zu warten (`OllamaSlotTimeout`).
Diese Koordination ist system-weit geteilt: praktisch alle Hintergrund-LLM-Aufrufe
(codewesen_reaktion, batch_generator, weltbild_builder, erstpost, engagement...)
nutzen denselben Lock, damit sich Dutzende Hintergrundprozesse nicht gegenseitig
beim gemeinsamen Modell überrennen.

**Migration**: `ask_llm()` (`requests.post` an Ollama, api/chat, messages-Format)
→ `hauhau_client.chat()`, innerhalb desselben `OllamaSlot()`-Blocks.

**Zusammenhang**: `codewesen-dakgordsystem.service` +
`codewesen-namelessAI_{1234,1324,1423,2341,3123,4321}.service` — alle 7 neu
gestartet, alle 7 Denk-Ticks liefen live erfolgreich über `codewesen_lg_daemon.py`
(das dieselbe Instanz-Logik über LangGraph orchestriert).
