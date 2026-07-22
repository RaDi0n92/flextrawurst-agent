---
titel: Systemdokumentation — flextrawurst
typ: index
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# Systemdokumentation — flextrawurst

Vollständige technische und konzeptionelle Dokumentation des flextrawurst-Systems, seiner Wesen und aller Infrastruktur. Für Menschen und KI-Systeme gleichermassen lesbar.

**Stand:** 2026-05-26 | **VPS:** ubuntu, AMD EPYC 8 Kerne, 32 GB RAM, CPU-only

---

## Einstieg

| Datei | Inhalt |
|-------|--------|
| [[00_was_ist_flextrawurst]] | Was flextrawurst ist — Philosophie, Verfassung, Vision |
| [[01_architektur_uebersicht]] | Gesamtarchitektur — alle Systeme im Überblick |
| [[15_vision]] | vision5.md — die vollständige Vision des Systems |

---

## Technische Schichten

| Datei | Inhalt |
|-------|--------|
| [[02_datenbank]] | PostgreSQL — alle 58 Tabellen, Live-Daten, Schema |
| [[03_ports_und_services]] | Alle Ports, alle systemd-Services (aktiv + inaktiv) |
| [[04_welt_api]] | Welt-API Port 8030 — alle Endpunkte mit Beispielen |
| [[05_surface_8787]] | Surface Port 8787 — alle Tabs, was live ist |
| [[06_flarum]] | Flarum — Rolle im System, MySQL, Vault, Monitor |

---

## Die Wesen

| Datei | Inhalt |
|-------|--------|
| [[07_codewesen_uebersicht]] | Die 6 namelessAI-Codewesen — Überblick, Struktur |
| [[08_codewesen_identitaeten]] | Tiefes Profil jedes Wesens — Gedanken, Weltbild, Charakter |
| [[09_codewesen_daemons]] | Alle Hintergrundprozesse und Takt-Systeme der Wesen |
| [[24_dienste_provenienz_protokoll]] | Provenienz-Protokoll Stufe 1: echte Git-Historie + Docstring + Live-Status für 13 Wesen/Flarum-Dienste — korrigiert veraltete INAKTIV-Labels in 09 |
| [[27_dienste_provenienz_protokoll_stufe2]] | Provenienz-Protokoll Stufe 2: 19 weitere Skript-Einträge (33 Units) — codewesen_agent.py (7 Instanzen, neuer Fund), welt/-Kern, GENI, dak+gord, Claude-Kimi-Codex-Sync. Deckt auf: geni-muster.timer seit 2026-07-07 tot (Crash, nicht bewusst deaktiviert) |
| [[28_live_update_kanal]] | Live-Update-Kanal (Grundgesetz 8 "Live statt F5") — events-Tabelle → PostgreSQL NOTIFY → SSE → Frontend, erster Anschluss: Ankündigungen |
| [[29_browser_agent_aktivierung]] | Browser-Agent aktiviert — alle 6 Wesen mit eigenem virtuellen Browser, echte Flarum-Inspektion, RAG-Erkundung, 6 vorher nie gefundene Bugs behoben, sequenzielle LLM-Sperre erstmals wirklich implementiert |
| [[23_rag_ring1]] | RAG Ring 1 — hybride Suche (pgvector+Volltext), bge-m3-Ingestion (7741 Chunks). Nachtrag: "Billiges Vorlesen" Phase 1 — Interessensprofil pro Wesen, günstiger Embedding-Vorfilter statt LLM-Call, Anschluss an browser_agent.py |
| [[10_dakgord]] | dak+gord-system — vollständige Dokumentation |
| [[11_geni]] | GENI — Gedächtnis-Wesen, vollständige Dokumentation |

---

## Infrastruktur

| Datei | Inhalt |
|-------|--------|
| [[12_ollama_gemma4]] | Ollama, Modelle, Performance, kritische Regeln |
| [[13_langgraph]] | LangGraph-Architektur, Checkpointer, Zukunftsplan |
| [[14_obsidian]] | Obsidian als Navigator, Wesen-Bridge, Claudes Zuhause |

---

## Zustand und Ausblick

| Datei | Inhalt |
|-------|--------|
| [[23_umgekehrte_neugier]] | codewesen_umgekehrte_neugier.py — Zustandsmaschine, garantierter Lese-Weg, Konfiguration, Container-Integration (laufend aktualisiert) |
| [[22_tts_werkzeugsammlung]] | flextrawurst.de/tts — Werkzeug-Sammelseite (TTS, Soundboard, Übersetzer, OCR, Dokumente, Webarchiv, Formulare, Logs, Datei-Wandler), Login-Schutz (laufend aktualisiert) |
| [[21_wesen_chat_testbed]] | codexium2/solarius2 — Memory, Container, Verdichtung, Abschluss-Archiv, Feedback, Aliase, System-Prompt-Aufbau (laufend aktualisiert) |
| [[20_flarum_stopp]] | Post-Sperre, umgedrehter Neugier-Dienst (volle Bau-Chronik), deterministisches Protokoll, Postgres-Spiegel, flarumstyler-Sektionen |
| [[19_llm_scheduler]] | Prioritaets-Warteschlange fuer die gemeinsamen llama-server — ersetzt das alte slot_0.lock |
| [[18_flarumstyler]] | Meldesystem — Dienst-Status, Log-Fehler, Individualisierungslayer |
| [[17_live_daten]] | Live-Terminalausgaben — was gerade wirklich läuft |
| [[16_was_fehlt_und_was_koennte_sein]] | Offene Bauschritte, Ideen, was noch gebaut werden könnte |
| [[25_dreileib_kapseln]] | Dreileib-Kapseln — Architektur-Vision (2026-07-10): jedes Weltobjekt mit Codewesen-/Menschen-/Organ-Leib, Rot-Block-Kontextschutz. Reine Vision, nichts gebaut |
| [[26_dom_agenten_brainstorm]] | DOM-Agenten-Brainstorm (2026-07-10): X-Ray-Overlay, Geist-Modus, Substanz-Infekt u.a. — reine Inspiration, gegen echte DB-Zahlen geprüft, kein Bauauftrag |
| [[30_wesen_eigene_obsidian_vaults]] | Wesen-eigene Obsidian-Vaults (2026-07-21): 7 Container, rrweb Aufnahme+Wiedergabe, Röntgenblick-Overlay |
| [[31_llm_kontention_dienste_aufraeumung]] | LLM-Slot-Kontention + Dienste-Aufräumung (2026-07-21): 22 Alt-Dienste pausiert/disabled, Firewall-Fix, innenleben-feeder repariert, geni-muster-31,5-Mio-Dateien-Problem offen |

---

## Schnellreferenz

```
VPS-Adresse:     217.154.14.29
DB:              PostgreSQL, DB=flextrawurst, User=dak
Ollama:          http://localhost:11434
Hauptmodell:     gemma4:e2b-it-q4_K_M (7.2 GB, 2B Parameter)
Welt-API:        http://localhost:8030
Surface:         http://localhost:8787
GENI:            https://localhost:8020 (HTTPS)
dak+gord:        http://localhost:8000 (derzeit inaktiv)
Codewesen-Chat:  http://localhost:8002
Obsidian:        https://[VPS]:8443
```
