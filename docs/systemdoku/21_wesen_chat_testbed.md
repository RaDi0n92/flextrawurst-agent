---
titel: Wesen-Chat-Testbed (codexium2/solarius2)
typ: system
erstellt: 2026-07-09
autor: claude-code bei Daniels VPS
---

# Wesen-Chat-Testbed (codexium2/solarius2)

[[INDEX|← Index]]

## Zweck

Die beiden Testbed-Spawner `codexium2` und `solarius2` (unterschieden von den älteren, einfacheren `codexium`/`solarius`) sind die Versuchsfläche für alles, was in einem Wesen-Chat über reines Rollenspiel hinausgeht: dauerhafte Erinnerungen, gepinnte Ausschnitte, Zusammenfassen langer Verläufe, erzählerische Rückblicke, Feedback-Kanäle. Alles hier Beschriebene gilt **nur** für diese beiden Spawner (`isTestbedSpawner()` im Server), nicht für die zwei älteren.

Server: `flextrawurst/scripts/serve_process_camera_preview.ts` (Port 8787). Frontend: `flextrawurst/out/process_camera/wesen_chat.html`.

**Diese Datei ist die laufend aktualisierte Referenz für den aktuellen Stand.** Ausführliche Einzel-Sessionberichte (was genau wann warum geändert wurde, mit Live-Test-Protokollen) liegen als datierte Dateien in `docs/` — siehe Verweise unten bei jedem Baustein.

## System-Prompt-Aufbau (`buildSystemPrompt()`)

Zusammengesetzt aus, in dieser Reihenfolge:

1. Feste Preamble (`_wesen_preamble.md`, Daniels eigener Rollenspiel-Grundtext, gilt für alle Wesen)
2. Charakterfelder — alle `.md`-Dateien im Wesen-Ordner (`wesen.md` = Kernidentität, plus optional `was_ich_bin.md`, `beispieldialoge.md` etc.)
3. Rückblicke auf frühere Gespräche — nur wenn beim Sessionstart bewusst ausgewählt (siehe Abschluss-Archiv unten)
4. `[Deine Sinne]`, Rollenspiel-Formatierungsregeln, 333-Token-Antwortlängenregel: **entfernt 2026-07-09** (siehe unten)
5. `[Erinnerungen]` — Memory-Inhalt
6. Wiederkehrende Themen: **komplett entfernt 2026-07-09** (siehe unten)
7. Container (aktive, gepinnte Behälter)
8. Verdichtungen: **nicht mehr hier** — fließen seit 2026-07-09 direkt in die Nachrichtenliste ein, nicht in den System-Prompt (siehe unten)
9. Globale Grenzen (nur wenn Toggle aktiv)
10. Alias-Register + aktiver Alias
11. Allgemeines Feedback (💬-Werkzeuge-Kanal)
12. MERKEN-Vorschlag-Hinweis

Zusätzlich, **nicht** Teil von `buildSystemPrompt()` selbst, sondern direkt am Chat-Handler: pro Nachricht wird bei mehreren definierten Aliasen der aktive Alias-Name als `"Name": ` vor den Nachrichtentext gesetzt (nur im ausgehenden Request, nie gespeichert/angezeigt).

## Memory

Kategorisierte Faktenliste (`ueber_mich`, `wichtige_momente`, `offene_fragen`, `meinungen`, `wesen_selbst`), Budget `MEMORY_BUDGET_ZEICHEN = 11111`. Editierbar (Textarea inline) und entfernbar über das 🧠-Popup, `PUT /wesen/:spawner/:name/memory` (Budget-Check + Provenienz-Diff serverseitig).

**Extraktion** (`runMemoryExtraktionJob`): liest **hart codiert nur die letzten 20 rohen Nachrichten** der gesamten Historie (`loadHistory(hp).slice(-20)`, nicht sessionbegrenzt, nicht kontextfenster-proportional) plus alle aktiv gepinnten Container-Einträge. **Bekannte, noch nicht behobene Lücke:** entspricht nicht dem tatsächlichen Kontextfenster — gefunden 2026-07-09, siehe `docs/2026-07-09_drei_systemprompt_bausteine_entfernt_bericht.md`.

**Auslöser** (Stand 2026-07-09):
- Manuell: 🧠 Memory → "Erinnerungen ziehen"
- Automatisch beim Start einer neuen Session (`/session/beenden`)
- **Neu 2026-07-09:** automatisch alle 20 Nachrichten seit dem letzten Extraktionsversuch, mit Vorab-Hinweis ab 10 Nachrichten in der UI. Ehrliche Zeitschätzung aus dem Durchschnitt der letzten 5 echten Durchläufe (`letzte_dauern_sek`) — keine erfundene Live-Prozentzahl, da die JSON-Extraktion keine bekannte Ziellänge hat.

**Dedupe** (verhindert wiederholte Extraktion desselben Inhalts): zweistufig seit 2026-07-09 — Jaccard-Wortüberlapp + Stemming + Cross-Kategorie-Vergleich (Schwelle 0.45) ODER Embedding-Cosine-Ähnlichkeit (`Xenova/paraphrase-multilingual-MiniLM-L12-v2`, Node-nativ, Schwelle 0.65, empirisch kalibriert) — fängt zusätzlich Paraphrasen mit komplett anderem Vokabular, die reiner Wortüberlapp nicht erkennt. Details: `docs/2026-07-09_embedding_modell_memory_dedupe_bericht.md`.

**Wiederkehrende Themen:** war ein Zusatzfeature (Modell erkennt beim Extrahieren, ob ein Thema schon mehrfach vorkam), **komplett entfernt 2026-07-09** auf Daniels Wunsch — beruhte auf zeichengenauem, vom Modell selbst gewähltem Themennamen-Matching, das in echter, natürlicher Rede praktisch nie zuverlässig griff. Code (Merge-Funktionen, Speicherformat) bleibt als Soft-Delete im Server stehen, nirgends mehr aufgerufen.

## Container

Frei anlegbare, benennbare Behälter mit gepinnten Ausschnitten (Mensch- oder Wesen-Ausschnitte), Budget `CONTAINER_BUDGET_ZEICHEN = 11111`. Nur aktive Container fließen in den System-Prompt ein.

## Verdichtung

Fasst ausgewählte Nachrichten zu einer Zusammenfassung zusammen — Original bleibt im sichtbaren Verlauf, nur was ans Wesen geschickt wird schrumpft.

**Seit 2026-07-09 grundlegend überarbeitet:**
- **Chronologisch echt integriert:** `aktiveZeitachse()` baut jetzt direkt die tatsächlich ans Modell gesendete Nachrichtenliste. Eine Verdichtung erscheint an der Stelle, an der ihre Original-Nachrichten standen — vorher landete sie als ein flacher Block am Ende des System-Prompts, unabhängig von der echten Position.
- **Chat-Format-Grenze live gefunden:** eine Verdichtung als eigene Nachricht mit `role: "system"` mitten im Verlauf ließ den Chat abstürzen ("System message must be at the beginning" — die Jinja-Chat-Vorlage des Modells erlaubt `system` nur als allererste Nachricht). Fix: der Verdichtungstext wird vor die nächste sichtbare Nachricht gewoben (gleiches Muster wie die bestehende Anhang-Injektion), Rolle der Trägernachricht bleibt unverändert.
- **Popup neu:** Checkbox-Mehrfachauswahl (einzeln bis alle Nachrichten), Regler markiert weiterhin einen chronologischen Bereich vor, Sortier-Dropdown (chronologisch / Zeichen / Tokens, auf-/absteigend), laufende Auswahl-Summe, geschätzte freigemachte Tokens vor dem Übernehmen.
- Beliebig verschachtelbar — eine Verdichtung kann selbst wieder Teil einer neueren Verdichtung werden (`findeAeusserstenTraeger`).

Details: `docs/2026-07-09_verdichtung_chronologisch_memory_autotrigger_bericht.md`.

**Offen:** kein automatischer Verdichtungs-Rhythmus (z.B. alle 10 Nachrichten, oder größere Nachrichten ab X Tokens sofort einzeln) — nur manuell ausgelöst. Falls das gebaut wird, muss der Regler intelligent bei der ersten noch nicht verdichteten Nachricht ansetzen und beim Hochregeln bereits verdichtete Einheiten überspringen (von Daniel 2026-07-09 als Voraussetzung benannt, noch nicht umgesetzt).

## Abschluss-Geschichte (erzählerischer Rückblick)

Anders als Memory (Stichpunkte) ein zusammenhängender, erzählerischer Rückblick auf das Gespräch — jederzeit auf Wunsch generierbar, landet als Entwurf, muss angenommen oder verworfen werden.

**Archiv statt Einzeldatei** (seit 2026-07-09, `AbschlussArchivEintrag[]` in `abschluss_archiv.json`): jede Annahme fügt einen **neuen** Eintrag hinzu (`archiv.push`), verknüpft mit dem Session-Index zum Zeitpunkt der Annahme — überschreibt nie einen älteren Eintrag. Bestätigt: nimmt man in Session 1 einen Abschluss an und generiert/übernimmt in Session 2 einen weiteren, bleiben **beide** erhalten; das gilt fortlaufend für jede weitere Session. Alte `letzter_abschluss.md`-Dateien werden beim ersten Zugriff automatisch als ein Eintrag migriert (`sessionIndex: null`).

**Auswahl beim Sessionstart:** vor der ersten Nachricht jeder neuen Session (ab Session 2) öffnet "↻ Neue Session" ein Dialog mit Checkbox-Mehrfachauswahl über alle Archiv-Einträge (`openNeueSessionModal`) — Standard ist **nichts ausgewählt**, jede Übernahme in die neue Session ist eine bewusste, einzelne Wahl. Die Auswahl wird als `abschluss_kontext_aktiv.json` gespeichert und fließt als `[Rückblicke auf frühere Gespräche — vom Menschen bewusst in dieses Gespräch mitgenommen]`-Block in den System-Prompt der neuen Session ein.

## Feedback

Zwei ursprünglich parallele Kanäle, **seit 2026-07-09 nur noch einer erreicht das Wesen**:

- **Allgemein** (💬 unter Werkzeuge, alle vier Spawner): freier Text, nicht an eine Nachricht gebunden, output-unabhängig. Einziger Kanal, der noch ans Wesen geht (`[Feedback vom Menschen]`-Block im System-Prompt).
- **Pro Nachricht** (👍/👎 + Kommentar unter jeder Bubble, nur Testbed-Spawner): **erreicht das Wesen nicht mehr.** Speicherung bleibt unverändert (`feedback.json` als Wahrheit für die UI + eine lesbare `.md`-Datei pro Eintrag im `feedback/`-Unterordner, existiert schon seit 2026-07-05) — nur die Auslieferung an das Modell wurde entfernt. Grund: unklar, was ein Charakter mit einem Daumen anfangen soll, zusätzlich ließen sich auch eigene (Mensch-)Nachrichten bewerten, was als "Feedback zur Nachricht des Menschen" ans Wesen ging.

## Aliase

Mehrere Rollen/Personas des Menschen (nicht des Wesens) pro Wesen, mit Name + kurzer Beschreibung. Zwei getrennte Injektionsstellen:
- **System-Prompt:** statisches Register aller Aliase + welcher gerade aktiv ist
- **Pro Nachricht:** der Browser schickt bei jedem Senden mit, welcher Alias aktiv ist (kein Datei-Zustand) — der Server prägt daraus nur den Namen (nicht die Beschreibung) als `"Name": ` vor den Nachrichtentext, nur im ausgehenden Modell-Request

## Automatischer Relevanzabruf — entfernt 2026-07-09

`findeRelevanteAlteStellen()` durchsuchte bei **jeder** Nachricht alte Sessions (auch die unmittelbar vorherige) nach thematisch passenden Stellen und hängte bis zu 3 Treffer ungekürzt an den System-Prompt. Auf Daniels Wunsch deaktiviert ("killt jedes Kontextfenster instant") — Soft-Delete, Funktion bleibt im Code, `relevanteFunde` ist fest ein leeres Array. Details: `docs/2026-07-09_relevanzabruf_deaktiviert_bericht.md`.

**Offene Idee (nicht umgesetzt):** statt pauschal bei jeder Nachricht, nur triggern wenn der Mensch explizit danach fragt ("weißt du noch...", "erinnerst du dich an...") — ein gezielterer RAG-Trigger statt Blindsuche.

## Bekannte offene Punkte (Stand 2026-07-09)

- Memory-Extraktions-Reichweite (20 Nachrichten statt Session/Kontextfenster) — gefunden, noch nicht behoben
- Kein automatischer Verdichtungs-Rhythmus, Regler noch nicht "intelligent" gegenüber bereits verdichteten Abschnitten
- Rückblick-als-RAG-Trigger — vertagt, kein Auftrag
