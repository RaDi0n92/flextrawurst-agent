---
titel: LLM-Scheduler — Prioritaets-Warteschlange fuer die gemeinsamen llama-server
typ: system
erstellt: 2026-07-07
autor: claude-code bei Daniels VPS
---

# LLM-Scheduler

[[INDEX|← Index]]

## Zweck

Koordiniert den Zugriff aller Hintergrund-Dienste auf die beiden llama-server-Instanzen
(`llama-hauhaucs` Port 11435 Live-Chat, `llama-hauhaucs-hintergrund` Port 11436), damit
zeitkritische Aufrufe (Ready-Check vor jedem Post, Reaktion auf Daniels eigene Nachrichten)
nie hinter langsamen Hintergrundarbeiten (Weltbild-Generierung, Denkprozesse) feststecken —
und beide echten Slots pro Server tatsaechlich genutzt werden statt nur einem.

## Vorgeschichte — warum das noetig wurde

In der Nacht 2026-07-06/07 meldete Daniel: "im flarum passiert nix mehr schon lange und ich
kann auh nicht chatten". Analyse ergab eine strukturelle Ursache, kein Einzelbug:

- `llama-hauhaucs-hintergrund.service` laeuft mit `--parallel 2` — 2 echte parallele Slots.
- Aber **alle ~18 dauerhaft laufenden Hintergrund-Prozesse** (7× `codewesen_reaktion.py`,
  7× `codewesen_agent.py`, plus `codewesen_batch_generator.py`, `weltbild_builder.py`,
  `codewesen_lg_daemon.py`, `codewesen_antwort_auf_daniel.py`) teilten sich **ein einziges
  Datei-Lock** (`fcntl.flock` auf `/tmp/ollama_locks/slot_0.lock`) — effektiv nur 1 nutzbarer
  Slot statt 2.
- 6 von 7 Aufrufer-Typen warteten mit `fcntl.flock(LOCK_EX)` **unbegrenzt lange** auf das
  Lock — kein Timeout. Nur `codewesen_agent.py` hatte ein 120s-Wartelimit.
- Fast jeder Aufrufer konfiguriert `timeout=600.0` (10 Minuten!) fuer den LLM-Call, *waehrend
  er das exklusive Lock haelt*. Ein einzelner langsamer Call konnte alle anderen 17 Prozesse
  fuer die volle Dauer einfrieren — unabhaengig von deren eigener Dringlichkeit.
- Drei Dienste (`codewesen_forum_neugier.py`, `codewesen_aufgabenchats.py`,
  `codewesen_engagement.py`) nutzten **gar kein Lock** — riefen den LLM unkoordiniert direkt
  auf, zusaetzlich zur Last der anderen 18.
- `flarum_poster.pruefe_bereit()` — der **Ready-Check vor jedem einzelnen Post**, der
  rettet ob ein fertig generierter Entwurf tatsaechlich veroeffentlicht wird — hatte
  ueberhaupt **keine** Koordination, obwohl er der zeitkritischste Aufruf im ganzen System ist.

### Simulation vor dem Bau

Diskrete-Ereignis-Simulation (4h simulierte Zeit, ~110 Aufrufe/Std. aus den realen
Intervall-Konstanten im Code, Service-Zeiten aus real gemessener Generierungsgeschwindigkeit
10.6 Tok/s):

| Modell | Erfolgsquote | Mittlere Wartezeit | p95 |
|---|---|---|---|
| Alt (1 Lock, FIFO, meist unbegrenzt) | 5.5% | 28.8min | 54min |
| Neu (2 Slots, Prioritaet, 90s Wait-Cap) | 97.7% | 13.8s | 65s |

Grund fuer den Kollaps: ~110 Aufrufe/Std. Last gegen ~50-55 Aufrufe/Std. effektive
Kapazitaet bei nur 1 Slot — strukturelle Ueberlastung von ~200%, keine gelegentliche Spitze.

## Architektur

- **Tabelle `llm_warteschlange`** (`welt/schema_llm_warteschlange.sql`): `server`,
  `prioritaet` (0=HOCH, 1=NORMAL, 2=NIEDRIG), `rufer`, `angefragt_um`, `slot_bis`.
  Selbstheilend — eine Zeile zaehlt nur "aktiv" solange `slot_bis` in der Zukunft liegt;
  stirbt ein Prozess mit gehaltenem Slot, faellt er automatisch frei, ganz ohne Aufraeum-Logik.
- **`llm_scheduler.py`** (Top-Level, wie `hauhau_client.py`): `class LLMSlot` — Context-Manager,
  ersetzt `fcntl.flock(slot_0.lock, LOCK_EX)` 1:1. Reiht sich in die Warteschlange ein, wartet
  hoechstens `max_wartezeit` Sekunden (Default 90s) auf einen freien von `N_SLOTS=2` Slots,
  gibt danach sauber auf (`LLMSlotTimeout`) statt endlos zu blockieren.
- **Koordination:** `pg_advisory_lock` nur fuer den atomaren "bin ich dran"-Check (Zaehlung
  aktiver Slots + Prioritaets-Reihenfolge) — Millisekunden. Der eigentliche LLM-Aufruf laeuft
  danach komplett ohne offene DB-Verbindung.
- **Prioritaet ist strikt lexikographisch** ueber (Stufe, Ankunftszeit) — eine HOCH-Anfrage
  ueberholt eine bereits wartende NIEDRIG-Anfrage immer, unabhaengig davon wer zuerst da war.
  Innerhalb derselben Stufe gilt FIFO (Fairness).

### Prioritaets-Zuordnung

| Stufe | Aufrufer |
|---|---|
| HOCH | `flarum_poster.pruefe_bereit()` (Ready-Check vor jedem Post, alle Aufrufer), `codewesen_reaktion.py`/`codewesen_agent.py`: Reaktion auf Daniels eigene Nachrichten (`process_inbox`/`verarbeite_inbox`), `codewesen_agent.py`: `pruefe_antwortpflicht` (33min-SLA), `codewesen_antwort_auf_daniel.py` |
| NORMAL | `codewesen_agent.py`/`codewesen_reaktion.py`: reguläre Rhythmen (Reflexion, Forum-Entwicklung, Themen-Beitrag, Gedanke/Pflicht/Impuls), `codewesen_batch_generator.py` (Queue-Fuellung) |
| NIEDRIG | `weltbild_builder.py`, `codewesen_lg_daemon.py`, `codewesen_engagement.py`, `codewesen_forum_neugier.py`, `codewesen_aufgabenchats.py`, `codewesen_vokabel_takt.py` (deaktiviert) |

## Getestet

- Isoliert (Unit-Tests via Threading): 2 echte Slots gleichzeitig moeglich, 3. wartet korrekt;
  HOCH-Prioritaet ueberholt bereits wartende NIEDRIG-Anfrage korrekt; Timeout gibt nach exakter
  Zeit sauber auf, keine verwaisten Zeilen in der Tabelle.
- Live unter echter Produktionslast (2026-07-07, nach Migration aller 13 Skripte + Neustart
  aller ~21 betroffenen Dienste): `llm_warteschlange` zeigte durchgehend genau 2 aktive Zeilen,
  korrekte Prioritaets-Reihenfolge der wartenden Zeilen, `forum_neugier` und `batch_generator`
  gaben live nach 90s korrekt auf ("LLM-Slot 'hintergrund' blockiert nach 90s — ... uebersprungen").

## Bewusst nicht migriert

- `reaktion_auf_dakgord.py` — Einmal-Migrationsskript, kein Dauerdienst, nutzt weiterhin das
  alte Datei-Lock (keine aktive Rolle im Kontentions-Problem).
- `codewesen_chat.py` (Live-Chat, Port 11435) — architektonisch bereits getrennt vom
  Hintergrund-Server, aktuell keine erkennbare Ueberlastung dort. `llm_scheduler.N_SLOTS`
  unterstuetzt `server="chat"` bereits fuer den Fall dass das spaeter noetig wird.

## Verwandt

- `flarum_poster.py` hat ein **separates**, unabhaengiges Lock (`/tmp/flarum_write.lock`) fuer
  das eigentliche Flarum-API-Schreiben (nicht LLM-bezogen) — bewusst unangetastet gelassen.
- Die eigentliche Inferenz-Geschwindigkeit (~10.6 Tok/s Generierung, CPU-only 35B-Modell) bleibt
  der fundamentale Flaschenhals — der Scheduler verhindert nur, dass ein einzelner langsamer
  Aufruf alle anderen mitreisst. Er macht das Modell nicht schneller.
