# dak+gord-system – Module Map

## `starte_dak_gord_system.py`
Zweck:
- Einstiegspunkt und Chatloop

Eingaben:
- Nutzereingaben
- Dateibefehle
- Anschlussfragen

Ausgaben:
- Antworten
- Fokuswechsel
- Trigger von Spuren und Modellläufen

Zukunft:
- bleibt Einstieg
- wird später stärker an expliziten LangGraph-Run-State angebunden

---

## `agent/dak_gord_system/anschlusskontext.py`
Zweck:
- hält Fokus und Anschlusskontext stabil

Zukunft:
- bleibt Gedächtnis-/Kontextmodul
- wird später von Graph-State gelesen und beschrieben

---

## `agent/dak_gord_system/agentdateien.py`
Zweck:
- baut `.agent.md`
- stabiler Gesamtstand
- aktueller Fokus
- Verlauf

Zukunft:
- bleibt Langzeitgedächtnis auf Dateiebene
- wird später von Graph-Nodes aktualisiert

---

## `agent/dak_gord_system/verdichtung.py`
Zweck:
- erzeugt strukturierte Verdichtungen aus Textausschnitten

Zukunft:
- bleibt Fachmodul
- wird später als `build_summary_node` aufgerufen

---

## `agent/dak_gord_system/neugierkern.py`
Zweck:
- Werkraum-Neugier
- Vision-Zyklus
- Spur- und Wochenlogeinträge

Zukunft:
- bleibt Domänenlogik
- wird später als Hintergrund-Run oder Graph-Node benutzt

---

## `agent/dak_gord_system/neugier_ticker.py`
Zweck:
- entkoppelter Hintergrundlauf für Neugier

Zukunft:
- bleibt kurzfristig sinnvoll
- kann später in echten Hintergrund-Graph-Run überführt werden

---

## `agent/dak_gord_system/ollama_chat.py`
Zweck:
- Modellaufrufe

Zukunft:
- bleibt Modelladapter
- später sauberer als Tool/Model-Layer kapseln

---

## Spurenordner
Zweck:
- langfristige Beobachtbarkeit

Wichtige Teile:
- `spuren/wochenlog`
- `spuren/verdichtung`
- `spuren/agentdateien`
- `spuren/neugier_ticker.log`

Zukunft:
- bleibt
- wird später strukturierter an Run-State gekoppelt
