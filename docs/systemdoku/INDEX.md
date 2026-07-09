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
| [[21_wesen_chat_testbed]] | codexium2/solarius2 — Memory, Container, Verdichtung, Abschluss-Archiv, Feedback, Aliase, System-Prompt-Aufbau (laufend aktualisiert) |
| [[20_flarum_stopp]] | Post-Sperre, umgedrehter Neugier-Dienst, deterministisches Protokoll, Postgres-Spiegel, flarumstyler-Sektionen |
| [[19_llm_scheduler]] | Prioritaets-Warteschlange fuer die gemeinsamen llama-server — ersetzt das alte slot_0.lock |
| [[18_flarumstyler]] | Meldesystem — Dienst-Status, Log-Fehler, Individualisierungslayer |
| [[17_live_daten]] | Live-Terminalausgaben — was gerade wirklich läuft |
| [[16_was_fehlt_und_was_koennte_sein]] | Offene Bauschritte, Ideen, was noch gebaut werden könnte |

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
