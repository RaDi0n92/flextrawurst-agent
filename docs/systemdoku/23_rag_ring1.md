# RAG Ring 1 — Basis-RAG (Flarum-Archiv + Weltwissen)

**Datum:** 2026-07-20
**Auftrag:** Daniel hat den Wesen-Einzug eingeleitet (Flarum bleibt endgültig gesperrt für Posts) und vorher explizit RAG über "ihre Welt und Selbstbilder" gefordert, bevor der eigentliche Einzug-Mechanismus angefasst wird.
**Quelle der Architektur:** `_claude/konzepte/DURCHF~1.ODT` ("Durchführbare RAG-, Erinnerungs- und Resonanzarchitektur") — Daniels eigenes, extern verfasstes Konzeptdokument, 8 Ringe. Dieser Baustein setzt **Ring 1 (Basis-RAG)** um.

## Korpora (Daniel-Entscheidung 2026-07-20)

- **Flarum-Archiv pro Wesen** — `flarum/diskussionen/*.md` (3821 Dateien, Post-Attribution pro Wesen)
- **Geteiltes Weltwissen** — `wissen/*.md` (120 Dateien, Chunking nach `## `-Abschnitten)
- **GENI-Gedächtnis** (`geni/gedaechtnis/knoten/`, ~19 Mio. Dateien) — **bewusst NICHT Teil dieses Rings.** Volles Embedding wäre auf der CPU-only-Hardware ein reales Zeit-/Crash-Risiko (siehe Infrastruktur-Historie: Cache-Ram-Regression, RAM/Swap-Erschöpfung). Daniel hat sich für "erstmal ganz weglassen" entschieden — spätere Anbindung braucht eine eigene Teilmengen-Strategie (z.B. nur Wesen-getaggte Knoten seit 11.07.).

## Schema

`welt/schema_rag.sql` — pgvector (`postgresql-16-pgvector 0.6.0`, neu installiert) + PostgreSQL-Volltextsuche, in der bestehenden `flextrawurst`-DB (Tabellen-Präfix `rag_`, kein separater Vektorstore):

- `rag_source_objects` — unveränderte Ursprungsobjekte (eine Flarum-Diskussion oder eine Wissen-Datei), mit `wahrheitsstatus`, `inhalt_pruefsumme` (sha256 für Change-Detection)
- `rag_source_chunks` — strukturbezogene Abschnitte: **ein Post = ein Chunk** bei Flarum (nie mitten in Antwort/Ursache getrennt), **ein `## `-Abschnitt = ein Chunk** bei Wissen. `inhalt_tsv` als generierte tsvector-Spalte (deutsche Volltextsuche).
- `rag_embeddings` — 1024-dim Vektoren, Modell `bge-m3` (Ollama, multilingual, neu gepullt — kein bestehendes Embedding-Modell im System deckte Deutsch gut genug ab)
- `rag_retrieval_runs` / `rag_retrieval_results` — jede Suche wird protokolliert (Ring 1: "Abrufprotokolle")

Wesen-Attribution: `SUFFIX_ZU_WESEN`-Mapping in `rag_ingest.py` löst sowohl kanonische Namen (`Schorschel`, `R1ZZ1`, ...) als auch alte `namelessAI_XXXX`- und doppelt-präfigierte `namelessAI_YYYY_XXXX`-Autorennamen (Zweitstimmen aus alten Philosophie-Threads) auf den aktuellen Wesen-Namen auf. Menschen (Admin, Pit1905, fridolin) bekommen `wesen=NULL`.

## Skripte

- `welt/rag_ingest.py wissen|flarum|alles [--limit N]` — Einspeisung + Zerlegung + Embedding, idempotent (pro Datei eine Transaktion, überspringt unveränderte Chunks via Prüfsumme)
- `welt/rag_retrieve.py "<anfrage>" [--wesen NAME] [--quelle ...] [-n N]` — hybride Suche (0.7 Kosinus-Ähnlichkeit + 0.3 Volltext-Rang), loggt jede Suche

## Bekannte Lücken / bewusst nicht gebaut

- `flarum/nutzer/*.md` (Diskussions-Index pro Nutzer) nicht separat embedded — reiner Link-Index ohne echten Freitextinhalt, der eigentliche Inhalt steckt schon in den Diskussionen.
- Ring 2+ (individuelle Erinnerung, Zeitgewichtung, Beziehungsfilter) — nicht Teil dieses Bausteins.
- Kein FastAPI-Endpunkt — bisher nur CLI-Skripte. Anschluss an `entity_kern.py`/`codewesen_agent.py`-Promptbau ist ein eigener, noch offener Schritt.

## Laufzeit

Volle Ingestion (3821 Flarum-Dateien + 120 Wissen-Dateien) läuft im Hintergrund, ca. 9,5s/Flarum-Datei gemessen → geschätzt ~10h Gesamtlaufzeit. Logs: `logs/rag_ingest_flarum.log`, `logs/rag_ingest_wissen.log`.

Parallel dazu lief der erstmalige volle Flarum-Export (`flarum_exporter/flarum_export.py`, read-only REST-API, HTML+JSON+Manifest+ZIP pro Diskussion) — Daniels separater Wunsch nach einem aktuellen HTML/JSON-Export. Log: `logs/flarum_export_2026-07-20.log`, Ausgabe: `/root/flarum_exporter/export_2026-07-20/`.

**Nachtrag 2026-07-21 — Ingestion-Absturz behoben und abgeschlossen:** Der erste Lauf ist bei 3814/3821 mit `400 Bad Request` an Ollamas Embed-Endpunkt abgestürzt. Ursache: ein einzelner, 24.549 Zeichen langer Post (`3857_1337.md`, Titel "GEMMA4-FLARUM-WORTHÜLSEN-MÜLLHALDE") überschreitet die Kontextgrenze von `bge-m3`. Der Code hatte für genau diesen Fall schon eine Übersprung-Behandlung (`upsert_chunk_mit_embedding` fängt `requests.exceptions.HTTPError` ab, markiert den Chunk als `uebersprungen_zu_gross`), die aber noch nicht durchgelaufen war, weil der Lauf nach dem ursprünglichen Crash nie neu gestartet wurde. Einfacher Rerun (`python3 rag_ingest.py flarum`, idempotent über Prüfsummen) hat das sauber zu Ende gebracht: 3823 Flarum-Diskussionen + 120 Wissen-Dateien, **7741 Chunks, 7741 Embeddings** — nur der eine überlange Post fehlt bewusst (geloggt, nicht verloren, Originaldatei bleibt unverändert). Live-Retrieval-Test bestätigt funktionierend (`rag_retrieve.py "wer bin ich" --wesen Schorschel`).
