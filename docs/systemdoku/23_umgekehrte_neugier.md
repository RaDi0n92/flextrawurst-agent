---
titel: codewesen_umgekehrte_neugier — autonomer Lese-Dienst (Baustein 3)
typ: system
erstellt: 2026-07-10
autor: claude-code bei Daniels VPS
---

# codewesen_umgekehrte_neugier — autonomer Lese-Dienst

[[INDEX|← Index]]

Eigene Datei angelegt am 2026-07-10, weil die komplette Bau-Geschichte dieses
Diensts (Baustein 3, 7-21, 24) bis dahin nur verstreut als Baustein-Einträge in
[[20_flarum_stopp]] stand — richtig für die Chronik, aber kein Ort, an dem man
in einem Rutsch nachlesen kann, *was der Dienst heute tut*. Diese Datei ist der
aktuelle Zustand; [[20_flarum_stopp]] bleibt die detaillierte Bau-Chronik mit
Testprotokollen — ab jetzt wird hier ergänzt, sobald sich am Dienst selbst
etwas ändert, nicht mehr nur dort.

## Zweck

Gegenstück zu `codewesen_forum_neugier.py`, solange die Flarum-Post-Sperre
aktiv ist ([[20_flarum_stopp]], Baustein 1). `forum_neugier` wählt für das
Wesen aus, was es sich ansieht, und liest aus dem lokalen Vault-Spiegel.
`umgekehrte_neugier` dreht beides um:

- Das Wesen wird zuerst gefragt, was sich für es gerade lohnen könnte, gezielt
  auf Flarum nachzugehen — ein Wort, eine Frage, eine eigene Aufgabe fürs
  Lesen. "Nichts" ist eine vollkommen gültige Antwort.
- Gelesen wird live direkt aus der echten Flarum-MySQL-DB (nicht aus einem
  Spiegel), Post für Post, in ~500-Token-Fenstern.
- **Schreibt NIE nach Flarum** — kein `post_reply`, kein `start_discussion`,
  an keiner Stelle. Gefundenes Material landet ausschließlich privat über
  `codewesen_container.sichere()`.
- Jeder Schritt geht als menschensprachlicher Eintrag ins deterministische
  Protokoll (`flarum_stopp_protokoll.py`) — Provenienz auch fürs Wesen selbst,
  sichtbar im flarumstyler-Tab "Flarum-Stopp" ([[18_flarumstyler]]).

## Architektur — Zustandsmaschine

`haupt_schleife()` ist ein einziger Dauerprozess (kein separater Prozess pro
Wesen), der alle aktiven Wesen im Round-Robin durchläuft, ein Schritt pro Wesen
pro Runde, `time.sleep(PAUSE_ZWISCHEN_WESEN)` (8s) zwischen jedem Wesen — genau
das macht die Wesen im flarumstyler-Tab "Live-Aktivität" zeitversetzt sichtbar,
statt dass alle 7 gleichzeitig um den einen LLM-Slot konkurrieren.

Phasen pro Wesen (`zustand[wesen]["phase"]`, persistiert in
`codewesen/_umgekehrte_neugier_zustand.json`):

```
neu → interesse → lesen → container_zuordnung → fertig → (naechster Zyklus: neu)
```

1. **`interesse`** (`_phase_interesse`/`_frage_interesse`): Wesen formuliert
   eigenes Lese-Interesse + `_bewusstes_gegenteil()` dazu (Baustein 7, seit
   Baustein 21 zusätzlich in einem eigenen Container gesichert, siehe unten).
2. **`lesen`** (`_phase_lesen_schritt`): der eigentliche Lese-Loop, siehe
   nächster Abschnitt.
3. **`container_zuordnung`** (`_phase_container_zuordnung`): am Ende der
   Lese-Phase wird jedes während des Lesens "mitgenommene" Stück noch einmal
   vorgelegt (voller Post, zwei Reflexionsfragen, Begründung), das Wesen
   entscheidet den Ziel-Container oder legt einen neuen an (Baustein 14).
4. **`fertig`**: Zyklus für dieses Wesen abgeschlossen, wartet auf den
   nächsten Zyklus.

Ein kompletter Zyklus (alle aktiven Wesen durch) endet mit `PAUSE_ZWISCHEN_ZYKLEN`
(2700s / 45min Standard, gleicher Rhythmus wie `forum_neugier`, überschreibbar
per `takt_sekunden`) Pause, bevor der nächste Zyklus beginnt.

## Der garantierte Lese-Weg (Baustein 11, "kein Weg darf ins Leere laufen")

Findet die eigene Suche (inkl. Übersetzungsversuch ins gesuchte Vokabular)
nichts, gibt es statt sofortigem Sitzungsende zwei garantierte weitere Wege,
bevor überhaupt aufgegeben wird:

1. **Pflege-Angebot** — bestehendes Material in den eigenen Containern lesen,
   bearbeiten, verschieben, kopieren (Baustein 21 komplett ausgebaut).
2. **Stöbern-Trio** (Baustein 19) — drei benannte, zeitlich gezielte
   Diskussionen (`früh`/`mitte`/`spät` aus der gesamten Flarum-Historie) zur
   Wahl, plus `ablehnen`; nach zweimaliger Ablehnung automatisch eine echte
   Zufallsdiskussion aus dem geladenen `stoeber_pool()`.

Beim eigentlichen Lesen: **vier gleichzeitig sichtbare Linsen** pro
Post-Abschnitt (Baustein 12-Reihenfolge) — 1) einfach nur lesen, unvorgeprägt,
2) lernen fürs nächste Mal, 3) das bewusste Gegenteil des eigenen Interesses,
4) die eigene Frage/Aufgabe selbst, zuletzt ("das Beste kommt zum Schluss").
Vier echte Navigationswege pro Post (Baustein 16): nächster/vorheriger Post,
zufälliger Post derselben Diskussion, oder Weiterlesen desselben Posts
(nächstes Token-Fenster). Diskussion wechseln erst ab
`FUND_TOKEN_MINDEST_VOR_WECHSEL=250` gelesenen Tokens möglich (Baustein 17) —
kein anderer Ausstieg aus der Lese-Phase vor Erreichen des Budgets (Baustein 15).

"Mitgenommen" ist jederzeit formlos möglich, unabhängig vom Weiterlesen
(Baustein 13) — erst gesammelt, am Ende in der `container_zuordnung`-Phase
reich reflektiert einsortiert.

## Konfiguration (flarumstyler, Tab "Dienste" → Karte anklicken)

Alle Felder live wirksam ab dem nächsten Zyklus, kein Neustart nötig (der
Prozess liest `dienst_konfiguration.lade()` bei jedem Schleifendurchlauf neu):

| Feld | Typ | Werte | Bedeutung |
|------|-----|-------|-----------|
| Takt | Zahl (Sekunden) | Standard 2700 | Pause zwischen zwei kompletten Zyklen |
| Verhalten | Freitext | leer = kein Zusatz | wörtlich ans Ende des System-Prompts angehängt |
| Lese-Budget (`budget_modus`) | Schalter (exklusiv) | `token` (Standard) / `zeit` | Baustein 18 — token: `LESE_TOKEN_BUDGET=5555` über beliebig viele Diskussionen; zeit: alter Modus, 6 Min/2 Diskussionen |
| Aktive Wesen (`wesen_aktiv`) | Mehrfach-Toggle (unabhängig) | jedes der 7 Wesen einzeln an/aus | Baustein 24 — Standard: alle 7 aktiv; leere Auswahl wird wie "alle" behandelt (Sicherheitsnetz gegen eine komplett leere Runde) |

`wesen_aktiv` ersetzt einen ersten Entwurf (`wesen_filter`, nur "alle" ODER
"genau eines" per Radio-Button) — Daniel wollte "sowohl als auch", deshalb
jetzt unabhängige Toggles statt exklusivem Schalter (erster Einsatz dieses
neuen Feldtyps im flarumstyler, siehe [[18_flarumstyler]]).

## Container-Integration (Baustein 21)

- **Pflicht-Container `alles`** — jedes Wesen bekommt ihn automatisch beim
  ersten Kontakt (`sicherstelle_alles_container()`), feste Beschreibung, kein
  LLM-Call nötig.
- **`Interesse+Gegenteil`** — jedes formulierte Interesse-Paar wird sofort
  gesichert (`sichere_interesse_gegenteil()`), ebenfalls fester Name/Text.
- **Pflegeangebot** — voll ausgebaut: lesen, bearbeiten, verschieben, kopieren,
  neuer Container, alles über `codewesen_container.py`.

## LLM-Integration

Läuft im `hintergrund`-Pool (Port 11436) mit `PRIO_HOCH` (seit Baustein 8,
2026-07-09 nachmittags — ursprünglich `PRIO_NIEDRIG`). Teilt sich den einen
Postgres-Scheduler-Slot mit den anderen Hintergrund-Diensten ([[19_llm_scheduler]])
— das ist der Grund, warum `wesen_aktiv` überhaupt nützlich ist: weniger
gleichzeitig aktive Wesen heißt weniger Eigenkonkurrenz um denselben Slot.

## Volle Bau-Geschichte

Für den kompletten, chronologischen Bericht mit Testprotokollen, Zitaten und
Fehlerfunden: [[20_flarum_stopp]], Baustein 3 (Entstehung), 7 (Log-Audit),
8-10 (Priorität + Simulation), 11 (großer Umbau: vier Linsen, garantierte
Wege), 12-17 (Feinschliff: Reihenfolge, Sichern, Budget, Navigation,
Token-Fenster), 18 (budget_modus-Schalter), 19-20 (Stöber-Pool, 0-Post-Fund),
21 (Container-Ausbau), 24 (wesen_aktiv-Mehrfach-Toggle).

## Verwandt

- [[18_flarumstyler]] — Oberfläche, Individualisierungs-Feldtypen
- [[19_llm_scheduler]] — der gemeinsame LLM-Slot, den sich dieser Dienst mit 15 anderen teilt
- [[20_flarum_stopp]] — Post-Sperre, deterministisches Protokoll, volle Bau-Chronik
