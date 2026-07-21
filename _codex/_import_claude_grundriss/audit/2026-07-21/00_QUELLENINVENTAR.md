# Flextrawurst — Quelleninventar & Weltzustands-Audit, Stichtag 2026-07-21

Erzeugt von Claude Code direkt auf dem laufenden VPS (nicht extern hochgeladen — sudo-Postgres-Zugriff, MySQL-root-Zugriff, systemctl, komplettes Dateisystem).

## Stichtag-Metadaten

- **Sammelzeitraum:** 2026-07-21, ca. 20:57–21:14 Uhr (Servereigene Zeitzone, siehe `date`-Ausgaben in den Einzeldateien)
- **Branch `/root`:** master (siehe `01_strukturkarte/root_git_status.txt`)
- **Branch `/root/werkraum`:** siehe `01_strukturkarte/werkraum_git_status.txt`
- **Während der Sammlung weitergebaut?** Nein, keine Code-Änderungen durch mich während des Audits (nur Lese-/Export-Operationen). Ein realer Live-Vorfall ereignete sich aber WÄHREND der Sammlung: die Server-Platte lief zwischenzeitlich voll (ENOSPC), Daniel hat das behoben — siehe `08_dienste/BEFUND_cyberling_crashloop_und_geni_muster_failed.md` und `09_logs/README.md`. Das ist Teil des Audits geworden, nicht nur Störung.
- **Vollständiger ChatGPT-Sammelauftrag im Wortlaut:** nicht als eigene Datei hier abgelegt — steht im Konversationsverlauf mit Daniel vom 2026-07-21, referenziert in Memory `project_flextrawurst_datenatlas_audit`.

## Ordnerübersicht (entspricht ChatGPTs Paket-A/B/C-Gliederung)

| Ordner | Inhalt | Größe |
|---|---|---|
| `01_strukturkarte/` | Git-Status beider Repos, Verzeichnisbaum, Befund zu Symlink-Struktur + Alt-Verzeichnissen | 132K |
| `02_kanon_ids/` | CANONICAL_ENTITY_IDS, Statusvokabular, **Befund: 6-vs-7-Wesen-Kollision vollständig aufgelöst** | 80K |
| `03_pg_schema/` | Vollständiges PostgreSQL-Schema (5533 Zeilen), Tabellenübersicht (100 Tabellen, Zeilen+Größe) | 180K |
| `04_pg_daten/` | 96 Tabellen als JSONL (Personendaten redigiert: `users.password`, `human_users.password_hash`+`email` ausgeschlossen; 4 LangGraph-Checkpoint-Tabellen als technisches Zwischenspeicher-State ausgeschlossen) | 282M |
| `05_flarum/` | Vollständiger Flarum-Export (Schema+Daten), Secrets-Tabellen ausgeschlossen, Pseudonymisierung nicht nötig (keine Drittpersonen vorhanden — siehe README darin) | 12M |
| `06_api/` | OpenAPI-Export, echte quellcodebasierte Auth-Klassifikation aller 352 Routen, **2 Sicherheitsbefunde** | 380K |
| `07_surface/` | Deployte Surface-Quelle (`build_surface.ts`) + gebautes HTML-Artefakt | 2.5M |
| `08_dienste/` | Alle relevanten systemd-Dienste+Timer im Detail, **Befund: Crash-Loop + failed Service live beobachtet** | 24K |
| `09_logs/` | 7-Tage-journalctl für 13 Dienste (38.390 Zeilen), Fehlerzeilen-Übersicht | 4.5M |
| `10_paket_b/` | 7 Wesen-Vaults vollständig, Claude-Beobachtungsschicht, 16 Handlungsgrammatiken, Kanon/Verfassung/Grundgesetze, Event-Typ-Katalog (44 Typen) | 476K |
| `11_paket_c/` | Anonymisierte Nginx-Zugriffsauswertung (373.844 Requests, 14 Tage!), Ressourcen-Snapshot — **mehr vorhanden als erwartet, siehe Domain-Korrektur** | 20K |

**Gesamt: ~301 MB**

## Die vier verifizierten Hauptbefunde dieses Audits (Kurzfassung)

1. **6-vs-7-Wesen-Kollision vollständig aufgelöst** (`02_kanon_ids/BEFUND_6_vs_7_wesen.md`): Kanonischer Code hat 7 Entitäten (inkl. dak+gord-system), die Surface zeigt an verschiedenen Stellen widersprüchlich 6 ODER 7 — inklusive eines Falls, wo der i18n-Übersetzungswert "7" sagt, aber der HTML-Fallback-Text "6" zeigt. Zusätzlich ungeklärte Konzeptfrage: zählt dak+gord zu den "Wartenden" oder ist es eine eigene, bereits aktive Kategorie?
2. **`GET /admin/einzugsampel` (v1) ohne Auth-Prüfung** (`06_api/BEFUND_admin_einzugsampel_v1_ungeschuetzt.md`): aktuell offen, im Gegensatz zu v2/v3/v4, die bereits geschützt sind.
3. **Disk-Voll-Vorfall während der Session** hat mind. 6 Dienste getroffen (Postgres-Recovery → cyberling-daemon-Crashloop, plus OSError in geni-hoerer/flarum-monitor/innenleben-feeder), hat sich selbst geheilt — zeigt eine blinde Stelle: kein zentraler Alarm verknüpft die Symptome über Dienste hinweg.
4. **flextrawurst.de ist live und wird tatsächlich besucht** (`11_paket_c/README.md`) — widerspricht einer 15 Tage alten internen Notiz, dass die Domain noch nicht deployed sei. 373.844 Requests in 14 Tagen, 3.455 eindeutige Besucher.

## Was bewusst NICHT exportiert wurde

- `.env`-Dateien, JWT-Secret-Datei, SSH-Schlüssel, Passwort-Hashes, echte Rohzugriffslogs mit IP-Adressen (nur gehashte Aggregation)
- `node_modules/`, virtuelle Python-Umgebungen, Caches, Ollama/llama.cpp-Modellgewichte
- LangGraph-Checkpoint-Tabellen (4 Tabellen, ~485MB in der DB — internes Zwischenspeicher-State, kein Weltinhalt)
- Rohe Flarum-Tokens/API-Keys/OAuth-Provider-Daten

## Bekannte Lücken / nicht geschafft (Zeitgrund, keine silent caps)

- Keine Zeile-für-Zeile-Triage aller 38.390 Log-Zeilen — nur die auffälligen Muster
- Keine 30-Tage-Logs, nur 7 Tage
- Entwicklungs-/Migrationsgeschichte nur über Git-Log + CLAUDE.md-Bau-Reihenfolge abgedeckt, keine eigene Zeitachsen-Rekonstruktion
- Tabellenübersicht (100 Tabellen) hat keine manuelle "vermutete Bedeutung" pro Tabelle — Namen sind großteils selbsterklärend, bei Bedarf gezielt nachfragen
- API-Beispielantworten nur für 4 von ~350 Routen gezogen (repräsentative öffentliche GETs, nicht erschöpfend)

## Altvorläufer/mögliche tote Systeme — nicht bewertet, nur benannt (aus 01_strukturkarte)

`flextrawurst-agent/`, `flextrawurst-pro/`, mehrere `*_review_*`-Snapshot-Ordner vom Security-Audit 2026-06-14, diverse Backup-Archive auf `/root/` — Einordnung (aktiv/tot/Vorläufer) braucht Daniels Wissen, nicht aus den Dateien allein ableitbar.
