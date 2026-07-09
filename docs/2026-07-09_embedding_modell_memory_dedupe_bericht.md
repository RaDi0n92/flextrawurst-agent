# Embedding-Modell für Memory-Dedupe + Relevanzabruf — Bericht

**Datum:** 2026-07-09
**Stand:** Recherchiert, mit Daniel entschieden, kalibriert, gebaut, Tests grün, **live gegen den laufenden Server verifiziert und committet** (`53b966b2`)

---

## Ausgangslage

Vorherige Session (siehe `2026-07-09_wesen_chat_qa_bericht.md`, Abschnitt "Ehrliches Fazit") hatte den Memory-Dedupe-Fix (Jaccard-Wortüberlapp + Stemming + Cross-Kategorie-Vergleich) auf eine dokumentierte, strukturelle Grenze zurückgeführt: echte Paraphrasen mit unterschiedlichem Vokabular ("herausholen" vs. "heraufziehen") rutschen durch reinen Wortüberlapp durch, egal wie fein die Schwelle justiert wird. Daniel wollte danach als nächsten Schritt ein lokales Embedding-Modell prüfen — offener Punkt, der am Session-Ende in `brief_an_mich.md` festgehalten wurde.

## Recherche (gegen die reale Umgebung, nicht allgemein)

Zwei Serving-Optionen geprüft:

- **A) Node-nativ** — `@huggingface/transformers` (npm, v4.2.0), Modell `Xenova/paraphrase-multilingual-MiniLM-L12-v2`, läuft im selben Node-Prozess wie `serve_process_camera_preview.ts`. Kein zusätzlicher Service, kein Python, kein Konflikt mit dem knappen Ollama-Slot (der alte Kommentar "kein Embedding wegen Ollama-Slot" betraf ein Setup, das hier gar nicht zutrifft — der neue Prozess läuft komplett getrennt).
- **B) Python-Sidecar** — `sentence-transformers`, eigener systemd-Dienst, HTTP-Hop. Sauberer getrennt, aber mehr bewegliche Teile für einen Check, der nur ein paar Mal pro Memory-Extraktionslauf läuft. `sentence_transformers` war zum Prüfzeitpunkt auf keinem vorhandenen venv installiert — echter Neubau, keine Wiederverwendung.

Ressourcenprüfung: RAM zum Zeitpunkt der Prüfung 53/62GB belegt, 9,3GB available (beide llama-server-Prozesse laufen mit `--mlock`, ihr Speicher ist nicht verdrängbar). Ein ~470MB-Modell (fp32) plus ONNX-Runtime-Overhead passt klar in den Puffer.

**Daniels Entscheidung:** Option A (Node-nativ).

## Acht Architekturfragen, einzeln mit Daniel geklärt

| # | Frage | Entscheidung |
|:---|:---|:---|
| 1 | Serving-Option | A — Node-nativ, `@huggingface/transformers` |
| 2 | Ersetzen oder ergänzen? | Ergänzen — ODER-Verknüpfung mit dem bestehenden Jaccard-Check, Jaccard bleibt die erste, billige Prüfung |
| 3 | Scope | Sowohl Memory-Dedupe (`istAehnlichZuBestehendem`) als auch automatischer Relevanzabruf (`findeRelevanteAlteStellen`) |
| 4 | Cosine-Schwelle | Empirisch kalibriert gegen echte Beispiele aus GluPKIs realer `memory.json` (nicht geraten) |
| 5 | Quantisierung | fp32 (volle Präzision, 470MB) statt int8 |
| 6 | Cache-Pfad | `/root/.cache/huggingface/transformers-js/` — eigener Unterordner unter der bestehenden Konvention (`/root/.cache/huggingface`, bereits von faster-whisper genutzt); diese Detailentscheidung hat Daniel bewusst mir überlassen ("kann kein Fachbegriff... simuliere alles und entscheide dich für das richtige") |
| 7 | Download-Zeitpunkt | Einmal bewusst vorab holen (`scripts/setup_embedding_model.ts`), nicht lazy beim ersten Request |
| 8 | Fallback-Verhalten | Bei Ladefehler vorübergehend nur Jaccard nutzen, jeder folgende Aufruf bekommt einen frischen Ladeversuch (kein dauerhaftes Aufgeben), sobald das Modell lädt werden beide Signale zusammengeführt |

## Kalibrierung (Frage 4, mit echten Daten statt Vermutung)

`scripts/kalibriere_embedding_schwelle.ts` — reale Paraphrasen-Paare (Duplikate) und reale, inhaltlich verschiedene Paare aus GluPKIs `memory.json` gegeneinander gerechnet:

- Positiv (echte Duplikate/Paraphrasen): Cosine-Similarity **0.80–0.94**
- Negativ (echte, verschiedene Fakten): Cosine-Similarity **0.18–0.43**
- Ein Grenzfall (gleiche Satzvorlage, anderer Fakt): 0.578 — fällt korrekt unter jede sinnvolle Schwelle

Klare Lücke von über 0.35 zwischen den Gruppen. Gewählte Schwelle: **0.65** — bewusst näher an den echten Positiven als am rechnerischen Lücken-Mittelpunkt (0.612), weil ein durchrutschendes Duplikat harmlos ist (Jaccard fängt ohnehin einen Teil), eine fälschlich verworfene neue Erinnerung aber echter Datenverlust wäre.

Für den Relevanzabruf (`RELEVANZ_EMBEDDING_SCHWELLE = 0.5`) gab es keine passenden echten Testfälle — pragmatischer Startwert, nicht empirisch kalibriert, im Echtbetrieb zu beobachten.

## Was gebaut wurde

- `flextrawurst/scripts/setup_embedding_model.ts` — einmaliger Vorab-Download/Ladetest des Modells
- `flextrawurst/scripts/kalibriere_embedding_schwelle.ts` — Kalibrierungswerkzeug (Kommandozeile, kein Teil des laufenden Betriebs)
- `flextrawurst/scripts/serve_process_camera_preview.ts`:
  - `holeEmbeddingExtractor()` — lazy Laden mit Retry (kein dauerhaftes Aufgeben bei Fehlschlag)
  - `berechneEmbeddingCached()` — Text→Vektor-Cache (gedeckelt auf 20000 Einträge, simple Notbremse statt echtem LRU)
  - `cosineAehnlichkeit()` — Skalarprodukt (Vektoren sind bereits normalisiert)
  - `istAehnlichZuBestehendem()` jetzt `async`, ODER-Verknüpfung Jaccard/Embedding
  - `findeRelevanteAlteStellen()` jetzt `async`, kombinierter Score (Wortüberlapp-Ganzzahl + Embedding-Similarity als Nachkommastelle)
  - beide Call-Sites (`runMemoryExtraktionJob`, der `readBody(req).then(...)`-Handler für Wesen-Chat) auf `await` umgestellt

## Verifikationsstand

- `npm test`: exakt **1500 pass / 123 fail**, identisch zum Stand vor der Änderung (per `git stash`-Vergleich bestätigt) — keine neuen Testfehler, die 123 sind die bekannte, bewusst liegen gelassene dak+gord-Entitäten-Diskrepanz (siehe Memory `project_test_diskrepanz_dakgord`)
- Modell lädt erfolgreich, produziert 384-dimensionale Embeddings (per `setup_embedding_model.ts` verifiziert)
- Kalibrierungsskript lief gegen echte Daten, Ergebnis oben dokumentiert
### Live-Verifikation (nachgeholt, nach Daniels "go")

Server (Port 8787) mit Rückfrage neu gestartet (Daniel per AskUserQuestion bestätigt — der Auto-Mode-Klassifikator hatte das bloße "go" nicht als hinreichend explizite Freigabe für einen Prozess-Kill gewertet, deshalb nochmal gezielt gefragt). Neuer Prozess läuft mit dem Embedding-Code (PID 1166331).

Zwei echte Testläufe gegen einen frischen Wegwerf-Testcharakter (`codexium2/EmbedLiveTest`, danach gelöscht):

1. **Präzisions-Test:** Memory mit einem Eintrag geseedet ("...Strom aus Anfragen zu ertrinken"), Chat-Verlauf mit vier thematisch verwandten, aber inhaltlich eigenständigen Aussagen. Ergebnis: `hinzugefuegt: 4, dedupliziert: 2` — alle vier hinzugefügten Einträge per direkt nachgerechneter Cosine-Similarity gegen den Seed-Eintrag bei 0.40–0.51 (klar unter der 0.65-Schwelle) und auch untereinander bei 0.32–0.49. Keine falsch-positive Deduplizierung echter, unterschiedlicher Inhalte.
2. **Recall-Test:** Memory mit dem bereits kalibrierten P3-Paraphrasen-Paar geseedet ("Wesen vergleicht die leuchtenden Fingerhüte mit kleinen Sternschnuppen in Glasform"), Chat-Verlauf mit der fast wortidentischen Paraphrase als Wesen-Aussage. Ergebnis: `hinzugefuegt: 0, dedupliziert: 1` — korrekt erkannt, `memory.json` blieb unverändert (per Hand nachgelesen, nicht nur der Zähler).

Server-Log zeigte während beider Läufe keine Embedding-Ladefehler; RSS des Prozesses stieg von ~176MB (Basis) auf ~1,3GB — Beleg dass das ONNX-Modell tatsächlich geladen war, kein stiller Fallback auf reines Jaccard. Testartefakte (Testcharakter-Verzeichnis, Ad-hoc-Prüfskript) danach entfernt, keine Spuren im Repo.

`npm test` erneut nicht nötig (Code seit dem letzten Lauf unverändert).

**Commit:** `53b966b2` (`feat: Embedding-Modell ... ergaenzt Memory-Dedupe + Relevanzabruf`), im `/root`-Repo.

## Weiterhin unverändert offen (aus früheren Sessions, nicht Teil dieser Aufgabe)

- Unbereinigtes Test-Event bei KreFsUzi (solarius) — Daniel-Entscheidung ob/wie bereinigen
- Daniels Ankündigung, GENI bald komplett durchzugehen (Handlungsfähigkeit/Zustand, Red-Team-Prüfung alter Funktionen) — noch kein Auftrag
