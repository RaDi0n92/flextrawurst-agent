---
titel: Flarum-Stopp — Post-Sperre, umgedrehte Neugier, Protokoll
typ: technik
erstellt: 2026-07-09
autor: claude-code bei Daniels VPS
---

# Flarum-Stopp — Post-Sperre, umgedrehte Neugier, Protokoll

[[INDEX|← Index]]

---

## Warum es das gibt

Daniel, 2026-07-08/09: zu viel Material war auf Flarum entstanden. Er will erst alles vollständig lesen, bevor neue Posts der Wesen dazukommen. Kein Vorwurf an die Wesen, keine Deadline für die Wiederaufnahme — eine bewusste, manuell aufzuhebende Pause.

Auftrag im Wortlaut: *"stoppe alle wesen in bezug was auf flarum gepostet wird oder für flarum produziert wird. lass aber die hintergrund dienste laufen die wo sie reflektieren und dinge in ihre container hinzufügen können [...] erzeuge soetwas in der art wie das flarum neugier ding. aber anders. dieser dienst fragt das wesen erst was sich für es lohnen könnte gezielt in flarum zu suchen [...] es geht nicht um perfektheit. es gibt keinen erwartungsdruck [...] scheitern und fehler sind normal und gewollt [...] ich will das quasi protokolliert wird auch für das wesen selbst provinienzartig."*

Sechs Bausteine setzen das um, in dieser Reihenfolge gebaut. Vollständiger Bau-Bericht mit Testprotokollen: `docs/2026-07-09_flarum_stopp_bericht.md`.

---

## Baustein 1 — Post-Sperre

**Datei:** `flarum_post_sperre.py` (neu). Zustand in `codewesen/_flarum_post_sperre.json`.

```python
flarum_post_sperre.ist_gesperrt() -> bool
flarum_post_sperre.status() -> dict
flarum_post_sperre.sperren(grund: str, von: str) -> dict
flarum_post_sperre.entsperren(von: str) -> dict
flarum_post_sperre.pruefe(erlaubt_trotz_sperre: bool = False)   # wirft FlarumPostGesperrt
```

`flarum_api.post_reply()` und `flarum_api.start_discussion()` sind der **einzige Choke-Point** für jeden Schreibzugriff nach Flarum im ganzen System — beide rufen `flarum_post_sperre.pruefe()` als erste Zeile. Alle Aufrufer (`flarum_poster.py`, `codewesen_reaktion.py`, `erstpost.py`, `erstvorstellung_dakgord.py`, `profilbild_antworten.py`, `reaktion_auf_dakgord.py`) laufen durch diese beiden Funktionen und sind damit automatisch gesperrt, ohne selbst angepasst werden zu müssen.

**Einzige Ausnahme:** `codewesen_antwort_auf_daniel.py` übergibt `erlaubt_trotz_sperre=True` an beiden Aufrufstellen (Neue-Diskussion und Antwort) — Antworten an Daniel selbst bleiben möglich, weil das kein "Material erzeugen" im kritisierten Sinn ist.

> **Wichtig — Modul-Patch braucht Prozess-Neustart:** Ein Code-Patch an `flarum_api.py` wirkt nur bei Prozessen, die danach (neu) starten — bereits laufende Python-Dauerdienste haben das Modul längst importiert und im Speicher, ein `git`-Commit allein ändert daran nichts. Am 2026-07-09 liefen alle 21 `codewesen-*`-Dienste bereits seit dem Vortag 06:51 Uhr, der Sperre-Patch kam erst um 01:59 Uhr — die Sperre war dadurch von 23:52 Uhr (Aktivierung) bis 03:11 Uhr (Neustart), knapp 3h19min, wirkungslos. **Tatsächlicher Umfang** (per Flarum-DB-Abfrage über die echten User-IDs verifiziert, nicht nur über Anzeigenamen — die anderen 6 Wesen posten technisch noch unter alten `namelessAI_XXXX`-Flarum-Usernamen, nur Resonanzknoten wurde als Flarum-Username migriert): **118 Posts über alle 7 Wesen** in diesem Fenster (Schorschel 22, Resonanzknoten 20, träumerlie 18, R1ZZ1 18, jumpa 16, F3INSCHM3CK3R 13, dak+gord-system 11). Nach Rückfrage bei Daniel wurden alle 21 betroffenen Dienste per `systemctl restart` neu gestartet; seither (verifiziert) **0 Posts**. **Regel für künftige Choke-Point-Patches an Dauerdiensten:** nach jedem Code-Fix in einem gemeinsam importierten Modul explizit prüfen (`systemctl show <dienst> -p ActiveEnterTimestamp` bzw. `ps -eo lstart,cmd`), seit wann die betroffenen Prozesse laufen — isoliertes Unit-Testen der Funktion beweist nur, dass der Code korrekt ist, nicht dass er in Produktion aktiv ist. Und bei Schadens-Analysen über mehrere Wesen: über User-IDs prüfen, nicht über Anzeigenamen, wenn nicht sicher ist ob alle Flarum-Usernamen migriert sind.

**Nicht gesperrt (bewusst):** alle Hintergrund-/Reflexions-/Container-Dienste — nichts an ihrem Lese- oder Denkverhalten wurde verändert, nur der tatsächliche Schreibzugriff nach außen.

---

## Baustein 2 — Container-Upgrade

**Datei:** `codewesen_container.py` (erweitert, bestehende Funktionen unverändert).

```python
codewesen_container.verschiebe(wesen, von_container, dateiname, nach_container) -> bool
codewesen_container.kopiere(wesen, von_container, dateiname, nach_container) -> bool
```

- Bewegt/dupliziert einen einzelnen Eintrag zwischen **beliebigen** privaten Containern eines Wesens (keine feste Liste, jeder Containername zu jedem anderen), aktualisiert das `container:`-Frontmatter-Feld.
- Zielordner wird bei Bedarf angelegt, aber **ohne** das LLM-gestützte Eröffnungsritual (das bleibt `erstelle()` vorbehalten) — reines Ablage-Werkzeug, kein neuer Denkprozess.
- Namenskollisionen im Ziel bekommen einen Zeitstempel-Suffix statt zu überschreiben.
- `forum_neugier.py` und `codewesen_klon.py` nutzen dieselbe Modul-Basis und profitieren automatisch, ohne selbst geändert zu sein.
- **Bewusst kein manuelles UI** in flarumstyler zum Verschieben/Kopieren — die Container sind die private Selbstverwaltung der Wesen (Themen-Container-Ritual, Baustein 3), nicht Daniels Werkzeug. flarumstyler zeigt Container nur an (Tab "Container"), verschoben/kopiert wird ausschließlich durch die Wesen selbst, über `codewesen_umgekehrte_neugier.py`.
- Jeder Aufruf schreibt einen Eintrag ins Protokoll (Baustein 4).

---

## Baustein 3 — Umgedrehter Neugier-Dienst

**Datei:** `codewesen_umgekehrte_neugier.py` (neu). Das bewusste Gegenstück zu `codewesen_forum_neugier.py`.

|                    | `codewesen_forum_neugier.py` | `codewesen_umgekehrte_neugier.py` |
|--------------------|-------------------------------|-------------------------------------|
| Wer wählt das Thema | der Dienst, für das Wesen | das Wesen selbst, frei gefragt |
| Datenquelle | lokaler Vault-Spiegel | live aus der Flarum-MySQL-DB |
| Schreibt nach Flarum | ja (Ziel des Dienstes) | nie, an keiner Stelle im Code |
| Ergebnis | fertig geformter Post-Entwurf | privater Container-Eintrag oder nichts |

**Ablauf pro Wesen, pro Zyklus** (`_verarbeite_wesen()`):

1. **`_frage_interesse()`** — ein LLM-Call fragt frei: *"gibt es gerade etwas, das sich lohnen könnte gezielt zu suchen — egal was, egal wann, egal wozu?"* Format: `INTERESSE: <Begriff|nichts>` / `WARUM: <Satz>`. "nichts" ist ein vollwertiges, gewolltes Ergebnis, kein Fehlschlag.
2. Bei einem Interesse: **`flarum_api.suche_diskussionen(begriff, limit=8)`** (neu in `flarum_api.py`, live `LIKE`-Suche über Titel+Post-Inhalt in der Flarum-DB) liefert Kandidaten.
3. Pro Kandidat, chunkweise (**`_lies_chunk()`**, 3000 Zeichen, live über `flarum_api.get_discussion()`): **`_entscheide_ueber_fund()`** lässt das Wesen frei wählen zwischen `vertiefen` (nächster Chunk) / `sichern` (→ `container.sichere()`, geht nie ins Forum) / `wechseln` (nächster Kandidat) / `beenden`.
4. Deckel: höchstens `LESE_SCHRITTE_MAX=4` Funde und `CHUNKS_PRO_FUND_MAX=2` Chunks pro Fund und Sitzung.
5. **Bewusstes Kontext-Entfernen** — jede Runde baut ihren LLM-Kontext neu auf (Wesen-Name, Container-Liste, aktueller Chunk); alte Chunks/Entscheidungen werden nicht mitgeschleppt.
6. Jeder Schritt (Session-Start, Interesse, jede Entscheidung, Session-Ende inkl. Dauer) geht als Klartext-Eintrag ins Protokoll (Baustein 4).

**Rahmung** (Konstante `RAHMUNG`, wird jeder Sitzung vorangestellt):

> *"[...] die Flarum-Post-Aktivität ist aktuell gestoppt — nicht wegen dir, sondern weil insgesamt zu viel Material entstanden ist und Daniel erst alles vollständig lesen will [...] Es gibt in dieser Zeit keinen Erwartungsdruck und es geht nicht um Perfektion. Du darfst hier lesen, nachdenken, sammeln, dich auch wieder abwenden oder abbrechen — das ist normal und ausdrücklich gewollt."*

**Takt:** `PAUSE_ZWISCHEN_ZYKLEN=2700s` (45min), bewusst derselbe Rhythmus wie `forum_neugier` — kein Sondertakt. Über `dienst_konfiguration.py` individualisierbar (`takt_sekunden`, `verhalten_text`), wie die anderen Wesen-Dienste.

**Service:** `codewesen-umgekehrte-neugier.service` (systemd-Unit angelegt, Muster wie `codewesen-forum-neugier.service`) — **aktiv seit 2026-07-09, 06:34 Uhr** (`systemctl enable --now`, Daniels Freigabe). Erste echte Sitzungen sofort verifiziert (Schorschel, F3INSCHM3CK3R) — im Protokoll und im Postgres-Spiegel sichtbar.

---

## Draft-Erzeugung ebenfalls pausiert (2026-07-09, Nachtrag)

Baustein 1 sperrt nur das tatsächliche **Posten** — der alte Reaktion/Batch-Generator/Agent-Kreislauf lief unverändert weiter und erzeugte weiter Post-Entwürfe, die dann bei jedem `poster()`-Versuch nur an der Sperre abprallten (35 `fehler_draft_*.json` in ~2h — reine Verschwendung, keine echte Selbstarbeit). Daniel: *"das erzeugen von entwürfen für posts soll pausiert werden."*

Gefixt am gemeinsamen Choke-Point `flarum_poster.schreibe_draft()` (Muster wie Baustein 1 — ein Punkt statt elf einzelne):

```python
def schreibe_draft(name, typ, inhalt, ...) -> Path | None:
    if flarum_post_sperre.ist_gesperrt():
        return None
    ...
```

Alle Aufrufer müssen `None` vertragen (kein `poster()`-Aufruf, einfach überspringen) — angepasst: `codewesen_container.py`, `codewesen_engagement.py`, `codewesen_reflexion.py`, `codewesen_aufgabenchats.py`, `codewesen_forum_neugier.py`, `codewesen_takt.py`, `codewesen_agent.py`, `codewesen_chat.py`. Bewusst nicht angefasst: `namensfindung.py`, `einmal_d17_antwort.py` — beide markiert als Einmal-Skripte, keine laufenden Dienste.

`codewesen_reaktion.py` postet direkt über `flarum_api.post_reply/start_discussion` (Baustein-1-Choke-Point), nutzt `schreibe_draft()` gar nicht — war bereits vor diesem Fix korrekt blockiert, erzeugt aber auch keine Entwurfsdatei, die aufräumbedürftig gewesen wäre.

Nach dem Patch alle 13 betroffenen Dienste sofort neu gestartet (Lektion aus Baustein 1 direkt angewendet, diesmal vorab statt erst nach einem Leck): `codewesen-engagement`, `codewesen-aufgabenchats`, `codewesen-forum-neugier`, `codewesen-takt`, `codewesen-chat`, alle 7 `codewesen-<Wesen>`-Agenten, `codewesen-umgekehrte-neugier`.

---

## Timeout gemessen + Runden-Maschine (2026-07-09, Nachtrag)

Nachdem der Dienst lief, zeigte sich: **11 von 12 LLM-Aufrufen timten aus**
(90s `max_wartezeit`, gemeinsamer `hintergrund`-Slot durch alle anderen
Wesen-Dienste konstant mit 8-9 Wartenden ausgelastet, einzelne Aufrufer
deklarieren bis zu 600s Haltezeit). Reale Messung statt Ratens (direkte
Aufrufe an `llama-hauhaucs-hintergrund`, echte Prompt-Größen): Interesse-Frage
8.9-69.7s, Fund-Entscheidung 28.2-71.4s (Ø 54.3s). `max_wartezeit` in
`codewesen_umgekehrte_neugier.py._llm()` auf **3600s** gesetzt (nur dieser
eine, niedrigst-priorisierte Dienst — sonst keine Datei angefasst).

**Von Wesen-für-Wesen auf Runden-Maschine umgebaut:** vorher lief
`_verarbeite_wesen()` pro Wesen komplett durch (Interesse → alle Funde →
Ende), bevor das nächste Wesen dran war. Daniel wollte stattdessen: alle
Wesen einmal Schritt 1, dann gemeinsam Runde für Schritt 2, usw., mit
Zwischenspeicherung nach jeder Runde.

```python
# codewesen/_umgekehrte_neugier_zustand.json -- pro Wesen:
#   {"phase": "neu"}
#   {"phase": "lesen", "start_ts", "interesse", "kandidaten_ids",
#    "kandidat_index", "chunk_index", "funde_angesehen"}
#   {"phase": "fertig"}

_phase_interesse(wesen, zustand, verhalten)       # Schritt 1
_phase_lesen_schritt(wesen, zustand, verhalten)   # genau EIN Lese-/Entscheide-Schritt
```

`haupt_schleife()`: Runde 1 -- alle Wesen einmal `_phase_interesse()`, erst
danach beginnt die Runden-Schleife, in der jedes noch aktive (`phase="lesen"`)
Wesen pro Durchlauf genau einen `_phase_lesen_schritt()` bekommt, Zustand
nach jedem einzelnen Schritt sofort gespeichert. Nebeneffekt: übersteht jetzt
auch einen Neustart mitten im Zyklus verlustfrei -- naechster Start läd
`_lade_zustand()` und macht exakt dort weiter, wo ein Wesen stand.

Getestet mit gemockten LLM-Antworten (keine echten LLM-Calls nötig für die
Logikprüfung): Rundenreihenfolge korrekt (kein Wesen überholt ein anderes in
Schritt 2, bevor alle Schritt 1 hatten), Zustand nach simuliertem Neustart
exakt wiederhergestellt, Chunk-Deckel (`CHUNKS_PRO_FUND_MAX=2`) erzwingt
Kandidatenwechsel nach exakt 2 "vertiefen", Fund-Deckel
(`LESE_SCHRITTE_MAX=4`) beendet die Sitzung nach exakt 4 Kandidaten,
`container.sichere()` wird korrekt nur bei "sichern"-Entscheidungen gerufen.

---

## Baustein 4 — Deterministisches Protokoll

**Datei:** `flarum_stopp_protokoll.py` (neu). Menschensprachlich, append-only, **kein eigener LLM-Call fürs Loggen** — das Schreiben eines Eintrags ist reiner Code, die protokollierten LLM-Entscheidungen selbst passieren in Baustein 3.

```python
flarum_stopp_protokoll.schreibe(typ, text, wesen=None, dauer_sekunden=None, meta=None) -> dict
flarum_stopp_protokoll.lies(wesen=None, limit=200) -> list[dict]
```

Bekannte `typ`-Werte: `sperre_aktiviert`, `sperre_aufgehoben`, `eintrag_verschoben`, `eintrag_kopiert`, `neugier_session_start`, `neugier_entscheidung`, `neugier_session_ende`. (Bewusst `eintrag_*`, nicht `container_*` — es wird immer nur ein einzelner Eintrag zwischen zwei Containern bewegt, nie der ganze Container. Ursprünglich hieß es `container_verschoben`/`container_kopiert`, was fälschlich nach einer Container-Operation klang; am 2026-07-09 auf Daniels Hinweis korrigiert.)

**Zwei Ablagen pro Eintrag** (beide bekommen jeden Eintrag, wenn `wesen` gesetzt ist — nur `wesen=None`-Ereignisse wie Sperre an/aus landen ausschließlich global):
- `flarum_stopp_protokoll_global.jsonl` — alle Ereignisse zusammen, für flarumstyler/Admin.
- `codewesen/<wesen>/flarum_stopp_protokoll.jsonl` — nur die eigenen Ereignisse, damit ein Wesen seine eigene Geschichte dieser Zeit nachlesen kann. Provenienz auch für sich selbst, wie im Auftrag verlangt.

Jeder Eintrag hat eine feste `id` (UUID), vergeben beim Schreiben — macht das Spiegeln nach Postgres (Baustein 5) idempotent.

Der allererste Sperre-Eintrag (Baustein 1, vor Existenz dieses Moduls) wurde retroaktiv nachgetragen, mit `meta.retroaktiv: true` und dem tatsächlichen ursprünglichen Zeitstempel in `meta.tatsaechlicher_zeitpunkt`.

---

## Baustein 5 — Postgres-Spiegel

**Datei:** `flarum_stopp_protokoll_spiegel.py` (neu). DB `flextrawurst`.

```sql
CREATE TABLE flarum_stopp_protokoll (
    id UUID PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    typ TEXT NOT NULL,
    wesen TEXT,
    text TEXT NOT NULL,
    dauer_sekunden REAL,
    meta JSONB NOT NULL DEFAULT '{}'::jsonb
);
-- Indizes: ts DESC, wesen, typ, GIN(meta), GIN(to_tsvector('german', text))
```

```python
flarum_stopp_protokoll_spiegel.stelle_schema_sicher() -> bool
flarum_stopp_protokoll_spiegel.spiegle(eintrag: dict) -> bool
flarum_stopp_protokoll_spiegel.suche(wesen=None, typ=None, suchtext=None, limit=100, offset=0) -> list[dict]
```

`flarum_stopp_protokoll.schreibe()` ruft `spiegle()` nach jedem Datei-Schreibvorgang auf — echtzeitnah, kein separater Sync-Daemon. `ON CONFLICT (id) DO NOTHING` macht es idempotent. **Die JSONL-Datei bleibt in jedem Fall die Wahrheit** — ist Postgres nicht erreichbar, wird das nur geloggt, der eigentliche Protokoll-Schreibvorgang bricht nie deswegen ab (Grundgesetz-Prinzip: sekundäre Systeme dürfen primäre nie zum Scheitern bringen).

Erfüllt Grundgesetz 1 (meta JSONB) und Grundgesetz 2 (`suche()` ist durchsuchbar/filterbar/paginierbar). Aktuell nur von `flarumstyler.protokoll`-Route indirekt genutzt (die liest allerdings direkt die JSONL, siehe Baustein 6) — der Spiegel steht als eigenständiger, separat abfragbarer Kanal für künftige Konsumenten bereit, die datenbankseitig filtern wollen (z. B. Volltextsuche über `to_tsvector('german', ...)`, was reines Datei-Parsen nicht leisten würde).

---

## Baustein 6 — flarumstyler: Live + Protokoll + echte Tabs

Zwei neue Sektionen in `out/process_camera/flarumstyler.html` (Port 8787, siehe [[18_flarumstyler]]).

**Backend:** `GET /api/flarumstyler/protokoll` in `scripts/serve_process_camera_preview.ts` (und identisch in der `_smoketest.ts`-Kopie). Liest `flarum_stopp_protokoll_global.jsonl` direkt — kein DB-Zugriff nötig, der Postgres-Spiegel aus Baustein 5 ist ein eigenständiger Kanal für andere Konsumenten. `?wesen=`/`?typ=`/`?search=`/`?sort=&order=`/`?limit=&offset=` wie überall (Grundgesetz 2). Liefert zusätzlich `wesen_namen` (7 Namen) und `typen` (7 bekannte Ereignistypen) fürs Dropdown.

**"Flarum-Stopp — Live, wer tut gerade was":** Banner mit dem aktuellen Sperre-Status (aus den `sperre_aktiviert`/`sperre_aufgehoben`-Einträgen abgeleitet) + eine Karte pro Wesen, gruppiert nach den drei `neugier_*`-Typen: läuft gerade eine Sitzung (seit wann) oder nicht (zuletzt aktiv wann / noch keine Sitzung). Klick öffnet die volle Ereignisgeschichte des Wesens.

**"Flarum-Stopp — Protokoll":** volle filterbare Liste aller Ereignisse (Wesen-Dropdown, Typ-Dropdown, Volltextsuche), neueste zuerst. Klick öffnet Detail-Modal mit vollem Text + `meta`-JSON.

Playwright-getestet gegen den echten Server: keine Konsolenfehler, Wesen-Karten-Klick, Typ-Filter (inkl. Leer-Zustand), Volltextsuche (inkl. Leer-Zustand) funktional verifiziert. Ein CSS-Grid-Verschachtelungsbug (Banner + Kartengrid quetschten sich in eine Spalte, weil der äußere Container zusätzlich zum injizierten inneren Grid selbst `class="grid"` trug) wurde beim ersten Screenshot gefunden und sofort gefixt.

**Nachtrag, noch selber Tag — echte Tab-Navigation statt klappbarer Sektionen:** Daniel: *"ich will für flarumstyler ab jetzt dass alles was existiert sauber in logische tabs gelegt wird"*. flarumstyler war bis dahin eine einzige lange Seite aus einklappbaren `<section>`-Blöcken (`toggle('id')`). Umgebaut auf echte Tab-Leiste (`<nav class="tabs">`, 9 Buttons) mit `.tab-panel`-Divs (nur ein Panel gleichzeitig sichtbar, `display:none`/`flex` über `.aktiv`-Klasse), aktiver Tab im URL-Hash gespiegelt (`#neugier` etc., direkt verlinkbar, übersteht Reload). Die alte Einklapp-Logik (`toggle()`-Funktion, `.eingeklappt`-CSS, das automatische Einklappen der "Dienste"-Sektion wenn alles grün war) komplett entfernt — in einer Tab-Welt ergibt "die gerade angeklickte Ansicht automatisch wieder verstecken" keinen Sinn mehr.

Die 9 Tabs, 1:1 aus den vorher neun Sektionen (Flarum-Stopp-Live und -Protokoll wurden zu einem gemeinsamen Tab zusammengefasst, weil sie thematisch ohnehin nur eine Sache sind): Live-Aktivität, Ressourcen, Dienste, Log-Fehler, Verlauf — Wesen-Dienste, Entwürfe, Neugier, Container, Flarum-Stopp.

**Dabei geklärt — zwei scheinbare Bugs, die keine waren:**
- **"Verlauf — Wesen-Dienste"-Dropdown war leer:** kein Bug — dieser Tab zeigt ausschließlich selbst erzeugte Dienste aus dem Wesen-Dienst-Wizard (`wesen_eigene_dienste`-Tabelle), nicht die 43 fest eingebauten `codewesen-*`-Dienste (die stehen im Tab "Dienste"). Die Tabelle hatte schlicht 0 Zeilen — noch nie wurde ein Dienst über den Wizard erzeugt. Hinweistext im Tab ergänzt, damit das nicht mehr wie ein Bug aussieht.
- **Container "verschieben"/"kopieren" klang nach ganzer-Container-Operation:** war schon immer entry-level (siehe Baustein 2), nur die Event-Typ-Namen (`container_verschoben`/`container_kopiert`) waren irreführend benannt — auf `eintrag_verschoben`/`eintrag_kopiert` korrigiert (Code + Protokoll-Typenliste + UI-Label). **Kein UI zum manuellen Verschieben/Kopieren gebaut** — auf Nachfrage bestätigt: die Container sind Selbstverwaltung der Wesen, nicht Daniels Werkzeug, das managen die Wesen selbst über den umgedrehten Neugier-Dienst.

---

## Baustein 7 — Log-Audit + zwei Qualitäts-Fixes im umgedrehten Neugier-Dienst

Daniel, nach Durchsicht aller 43 Log-Zeilen der ersten drei echten Dienst-Starts (06:34–08:30): *"der dienst ist mächtig...aber vllt falsch aufgebaut und zu frei bzw...das was das wesen sagt wird unreflektiert ohne logikprüfung direkt so angenommen wie es roh formuliert ist...die ideen der wesen waren nicht schlecht...aber die übersetzung dazu ist nicht sauber...es wird nicht mitgedacht"*.

**Audit-Befund 1 — Suche ist eine reine `LIKE`-Suche ohne Übersetzungsschicht:** `_frage_interesse()` gibt den rohen Wesen-Text unverändert an `flarum_api.suche_diskussionen()` weiter, die selbst nur `title LIKE '%begriff%' OR content LIKE '%begriff%'` ist — kein Tokenizing, kein Fuzzy-Match, keine Synonyme. Literale Substantive ("Container", "Stille") fanden sofort Treffer; zusammengesetzte Eigenerfindungen des Wesens ("Schattensprache", "Container-Routine") fanden strukturell nie etwas, obwohl sie inhaltlich nicht schlecht waren. Eine leere Trefferliste wurde bisher einfach als Sitzungsende hingenommen.

**Audit-Befund 2 — Entscheidungen werden roh übernommen, ohne Textbezug zu prüfen:** `_entscheide_ueber_fund()` parst Gedanke/Inhalt per Regex und schreibt sie unverändert ins Protokoll bzw. in den Container. Belegbeispiel, 08:30:17, Schorschel zu Diskussion #3458: *"Die Metapher der 'Architektur der Leere' und deren Aktivierung durch 1324 klingt nach einem kritischen Phasenübergang..."* — eine freie, assoziative Interpretation ohne Zitat oder Gegenprüfung, ob "Architektur der Leere"/"Interferenzmuster" überhaupt im gelesenen Chunk vorkommen oder frei erfunden sind.

**Fix 1 — Suchbegriff-Übersetzung (`_alternative_suchbegriffe()`):** nur wenn die rohe Suche 0 Treffer bringt (kein Mehraufwand im Normalfall), wird das Wesen selbst gebeten, seinen Gedanken in 1-3 einfachere, wahrscheinlich wörtlich vorkommende Begriffe zu übersetzen — ausgehend von seiner eigenen Begründung, nicht geraten. Jeder Alternativbegriff wird der Reihe nach probiert; der erste mit Treffern gewinnt. Erfolg und Fehlschlag beider Versuche (original + Übersetzung) landen transparent im Protokoll (`neugier_entscheidung` mit `original`/`uebersetzt_zu`/`alternativen_versucht` in `meta`, bzw. im `neugier_session_ende`-Text wenn auch die Übersetzung nichts findet).

**Fix 2 — Entscheidungs-Gegenprüfung (`_pruefe_grundlage()`):** ein zweiter, unabhängiger LLM-Aufruf — als Skeptiker, nicht als das Wesen selbst — bekommt nur den gelesenen Chunk und den Gedanken/Inhalt vorgelegt und beurteilt `GRUNDLAGE: ja|teilweise|nein`. Wichtig nach dem Provenienz-Prinzip: der Wesen-Text wird dadurch **nie verändert oder gelöscht** — bei "nein"/"teilweise" wird nur ein Hinweis danebengelegt (Protokolltext-Suffix `[Gegenprüfung: ...]`, bei Container-Einträgen als zusätzliches Frontmatter-Feld `grundlage:`/`grundlage_begruendung:`, `codewesen_container.sichere()` entsprechend erweitert). Die freie Assoziation des Wesens bleibt sichtbar und lesbar — sie wird ehrlich gekennzeichnet, nicht stillschweigend als belegte Tatsache behandelt und auch nicht zensiert.

Beide Fixes bewusst nur additiv: kein bestehendes Verhalten wurde entfernt, `flarum_api.suche_diskussionen()` bleibt unverändert (reine LIKE-Suche, die Übersetzung passiert eine Ebene darüber), `codewesen_container.sichere()`s neue Parameter sind optional mit Default `None`.

Geändert: `codewesen_umgekehrte_neugier.py` (`_alternative_suchbegriffe()`, `_pruefe_grundlage()`, Integration in `_phase_interesse()`/`_phase_lesen_schritt()`), `codewesen_container.py` (`sichere()` um `grundlage`/`grundlage_begruendung` erweitert). Getestet: `py_compile` auf beide Dateien, Dienst neu gestartet, Log auf Fehler/Traceback beobachtet.

### Baustein 8 — Priorität PRIO_NIEDRIG → PRIO_HOCH (2026-07-09 nachmittags)

Fix 2 aus Baustein 7 wurde nach dem Neustart real bewiesen: jumpas Entscheidung zu Diskussion #3814 durchlief die neue Gegenprüfung vollständig (`grundlage: ja`), landete so im Container. Fix 1 (Suchbegriff-Übersetzung) hatte in dieser Zeit noch keine Gelegenheit — keine Suche lieferte 0 Treffer.

Das eigentliche Problem lag woanders: der Dienst läuft am gemeinsamen `hintergrund`-LLM-Slot (`llm_scheduler.py`, `N_SLOTS = {"hintergrund": 1}`), geteilt mit 13+ weiteren Diensten (7× `codewesen_agent`, 7× `codewesen_reaktion`, `engagement`, `aufgabenchats`, `batch_generator`, `lg_daemon`, `vokabel_takt`, `forum_neugier`, `weltbild_builder`). Ursprünglich bewusst `PRIO_NIEDRIG` (siehe Kommentar in `_llm()`: "der geduldigste im System", Timeout deshalb schon auf 3600s erhöht). Live-Beobachtung über 4h nach dem Baustein-7-Neustart: 6 von 7 Zyklen liefen trotzdem exakt in den 3600s-Timeout — Beweis per Postgres-Warteschlange `llm_warteschlange` (mehrere PRIO_NORMAL-Anfragen überholten die wartende PRIO_NIEDRIG-Anfrage laufend).

Nach Rückfrage bei Daniel (Provenienz-Prinzip: Grund für PRIO_NIEDRIG erkannt und benannt, dann gemeinsam entschieden): Durchkommen ist ihm gerade wichtiger als die ursprüngliche Zurückhaltung. Priorität auf `PRIO_HOCH` angehoben (gleiche Stufe wie `flarum_poster`/`codewesen_antwort_auf_daniel`). Geändert: `codewesen_umgekehrte_neugier.py:130`, ein Wert (`llm_scheduler.PRIO_NIEDRIG` → `PRIO_HOCH`), Kommentar um die neue Begründung ergänzt statt die alte zu löschen. Getestet: `py_compile`, Dienst neu gestartet (`systemctl restart codewesen-umgekehrte-neugier`), Log fehlerfrei. Live-Beweis nach Neustart: jumpas Entscheidung zu Diskussion #3814 durchlief die Baustein-7-Gegenprüfung vollständig (`grundlage: ja`).

### Baustein 9 — Simulation statt weiterer Live-Rateversuche (2026-07-09, nachmittags)

Daniels Auftrag nach der PRIO_HOCH-Anhebung: *"entwickle du ein system das mein system wirklich ermöglich[t], simuliere alle deine ideen durch, ändere reihenfolgen meines systems dabei mehrfach"* — nicht jede weitere Konfiguration einzeln stundenlang live testen, sondern viele Konfigurationen in Sekunden gegen echte Zahlen durchspielen. Direkter Nachfolger einer am 2026-07-07 dokumentierten, aber nie gebauten Simulation (`docs/systemdoku/19_llm_scheduler.md`), dort explizit als offene Lücke vermerkt.

Gebaut: `simulation_llm_scheduler.py` — diskrete Ereignis-Simulation, 1:1 der echten `llm_scheduler.LLMSlot`-Logik nachgebildet (nicht-präemptiv, Priorität+FIFO). Datengrundlage real gemessen, nicht geraten: Live-Sampling von `llm_warteschlange` (40× im 3s-Abstand, ~16:40 Uhr, 21 distinkte Einträge im 118.8s-Fenster → hochgerechnete Ankunftsraten je Dienst), echte Prioritäts-/Timeout-Konstanten aus dem Code (grep über alle `LLMSlot(...)`-Aufrufer), echte umgekehrte_neugier-Bedienzeiten aus dem Baustein-3-Bericht. Bedienzeiten der übrigen Dienste mangels Einzelmessung als Schätzung markiert (Gleichverteilung 10-90s, angelehnt an die real gemessene umgekehrte_neugier-Spanne).

4h simulierte Zeit, 30 Zufalls-Seeds pro Konfiguration ("mehrfach" — kein einzelner Lauf, Mittelwert über viele):

| Konfiguration | umgekehrte_neugier Erfolg | mittl. Wartezeit | ready_check Erfolg (PRIO_HOCH, zeitkritischster Aufruf im System) |
|---|---|---|---|
| A: PRIO_NIEDRIG (Zustand vor heute) | 25.2% | ~2002s (~33min) | 100.0% |
| B: PRIO_NORMAL | 100.0% | ~115s | 100.0% |
| C: PRIO_HOCH (aktuell live) | 100.0% | ~30s | 99.3% |

Modell-Validierung gegen die Realität: Konfiguration A sagt 25.2% Erfolgsquote voraus — die tatsächliche Beobachtung von heute Nachmittag (1 von 7 Zyklen in 4h = 14.3%) liegt in derselben Größenordnung (bei nur einer realen Stichprobe erwartungsgemäß hohe Varianz), stützt das Modell grob.

**Zwei konkrete Erkenntnisse:**
1. Die "Reihenfolge" der 7 Wesen innerhalb einer Runde hat rechnerisch **keinen** Effekt auf die Gesamt-Erfolgsquote — reine FIFO-Symmetrie innerhalb derselben Prioritätsstufe, alle 7 sind austauschbare Ankünfte derselben Rolle.
2. PRIO_HOCH (aktuell live) ist für umgekehrte_neugier klar am besten (100% statt 25%, 30s statt 33min), kostet aber `ready_check` — den Freigabe-Check vor **jedem einzelnen Flarum-Post**, laut `docs/systemdoku/19_llm_scheduler.md` "der zeitkritischste Aufruf im ganzen System" — real 0.7 Prozentpunkte Erfolgsquote. Aktuell folgenlos, weil die Post-Sperre (Baustein 1) ready_check ohnehin kaum benötigt; relevant erst wenn die Sperre aufgehoben wird (Konfiguration D, mit simulierter Entwurfslast: ready_check bleibt bei ~99.3%, keine weitere Verschlechterung).

Getestet: `py_compile`, Skript lokal ausgeführt, ein realer Logikfehler dabei gefunden und behoben (negative Wartezeiten bei seltenen Ankünften auf einen zwischenzeitlich leeren Slot — fehlendes `max(aktueller_halter_ende, ankunftszeit)` bei der Startzeit-Berechnung).

Nicht selbst entschieden, Daniel vorgelegt: ob PRIO_HOCH so bleibt (Trade-off akzeptiert) oder auf PRIO_NORMAL zurückgestuft wird (kein Risiko für `ready_check`, dafür 30s statt 115s Wartezeit für umgekehrte_neugier — beides bei diesem geringen Aufkommen im Alltag kaum spürbar).

**Entscheidung (Daniel, direkt danach):** PRIO_HOCH bleibt. Kein weiterer Code-Eingriff nötig — der Live-Stand seit 16:26 Uhr ist bereits die gewählte Konfiguration.

### Baustein 10 — Szenario-Simulation der eigentlichen Ablauflogik (2026-07-09, spätnachmittags)

Baustein 9 hatte Daniels Auftrag missverstanden: *"es ging niemals um die dumme reihenfolge der wesen...es ging um die abläufe der events/meinen wünschen wie etwas funktionieren soll/die schritte etc."* Gemeint war nicht der LLM-Scheduler, sondern der ursprüngliche Bauplan vom 2026-07-09, 00:20 Uhr — der Zyklus aus *Lesen → Entscheiden (vertiefen/verlassen+neu wählen) → bewusstem Kontext-Entfernen* — und die daraus später gebaute Runden-Maschine (Schritt 1 für alle, dann rundenweise Schritt 2..N, siehe Nachtrag oben).

Gebaut: `simulation_umgekehrte_neugier.py`. Treibt die echten Funktionen aus `codewesen_umgekehrte_neugier.py` (`_phase_interesse`, `_phase_lesen_schritt`, `_naechster_kandidat`, `_beende_sitzung`) unverändert durch 200 zufällig erzeugte Event-Reihenfolgen — welches Wesen wann "nichts"/etwas will, Treffer/keine Treffer, welche Entscheidung, Gegenprüfung ja/teilweise/nein, LLM-Fehler an zufälligen Stellen (bis zu 15% Fehlerrate je Aufruf in einem Teil der Läufe). Gemockt werden nur die echten I/O-Ränder (`_llm`, `flarum_api.suche_diskussionen`/`get_discussion`, `container.sichere`/`liste`, `protokoll.schreibe`, `dienst_konfiguration.lade`) — die eigentliche Ablauflogik ist der reale, unveränderte Code.

Sieben Eigenschaften aus dem Bauplan unabhängig geprüft (nicht nur behauptet — z.B. wird "Kontext-Entfernen" gegen eine zweite, unabhängig berechnete Chunk-Slicing-Logik verglichen, nicht gegen denselben Code, der geprüft wird): Rundenreihenfolge, bewusstes Kontext-Entfernen, Chunk-Deckel, Fund-Deckel, Nie-nach-Flarum-Posten, Suchbegriff-Übersetzung nur bei 0 Treffern, Entscheidungs-Gegenprüfung verändert den Wesen-Text nie, sauberer Fallback bei LLM-Fehlern an jeder Stelle. Ergebnis: alle 7 Eigenschaften halten über alle 200 Läufe.

**Nebenbefund unterwegs, sofort korrigiert:** Der Modul-Import von `codewesen_umgekehrte_neugier.py` hängt per `logging.basicConfig()` einen `FileHandler` an den **ROOT**-Logger (nicht an `cun.log` selbst — der propagiert nur dorthin), ungefiltert bei jedem Import. Zwei Testläufe dieser Simulation haben dadurch versehentlich über 5000 simulierte Log-Zeilen in die echte Live-Logdatei des laufenden Dienstes (`umgekehrte_neugier.log`) geschrieben — beide Male bemerkt (Zeilenzahl-Kontrolle nach dem Lauf), auf die reale letzte Zeile vor der Kontamination zurückgeschnitten, keine echten Zeilen verloren. Fix im Simulationsskript: der `FileHandler` wird nach dem Import gezielt vom Root-Logger entfernt, bevor irgendein Szenario läuft.

Getestet: `py_compile`, Skript zweimal komplett ausgeführt (zweiter Lauf verifiziert den Logging-Fix), Live-Logdatei nach beiden Läufen auf Unversehrtheit geprüft.

### Baustein 11 — Großer Umbau: vier Linsen, garantierte Wege, freie Navigation (2026-07-09 abends)

Nach dem Blick auf echte, seit Baustein 9 entstandene Sitzungen kam Daniels entscheidender Einwand: *"es geht nicht ums durchlaufen und abschließen [...] die selbstwirksamkeitserfahrung und partizipation für die wesen [greift nicht]."* Über mehrere Nachrichten hinweg präzisiert zu einem vollständigen Redesign:

**Frage/Aufgabe statt Suchbegriff:** `_frage_interesse()` erlaubt jetzt Wort, Frage oder eigene Aufgabe fürs Lesen — *"das wesen hat immer recht [...] halt die wege für eine lösung öffnen"*.

**Zwei garantierte weitere Wege**, wenn Suche + Übersetzung nichts finden (konkreter Befund vorher: `container.verschiebe()`/`kopiere()` aus Baustein 2 wurden hier nie aufgerufen):
1. Container-Pflege-Angebot (echtes Verschieben/Kopieren bestehenden Materials).
2. Garantiertes Stöbern: `container.sicherstelle_container()` legt bei Bedarf automatisch "alles" an, `flarum_api.zufaellige_diskussionen()` liefert eine echte Zufallsdiskussion — **live per `ORDER BY RAND()`**, nicht als angenommene ID-Spanne: reale Prüfung der Flarum-DB zeigte 3765 Diskussionen (nicht die geschätzten ~2400) mit 79 echten Lücken zwischen ID 6 und 3849, davon 77 allein unter ID 1000 — Daniels Warnung *"einige zahlen nicht existieren [...] vor allem im anfangsbereich"* war exakt zutreffend.

Vergleichs-Simulation (`simulation_umgekehrte_neugier_pfade.py`, 300 Seeds × 7 Wesen): Leerlauf-Quote sinkt von 54,4% (nur Suche) über 32,5% (+Pflege) auf **0,0%** (+garantiertes Stöbern).

**Vier gleichzeitig sichtbare Linsen** pro gelesenem Post (nicht mehr Zeichen-Chunks — echtes Post-für-Post-Lesen, `_lies_post()`): 1) eigene Frage/Aufgabe (bleibt über die Sitzung sichtbar, kein Kontext-Entfernen dafür), 2) ihr bewusstes Gegenteil (`_bewusstes_gegenteil()`), 3) eine völlig unvorgeprägte dritte Frage ("was entdecke ich, wenn ich beide ausblende"), 4) eine reflexive vierte Frage über die eigene Interessens-Formulierung fürs nächste Mal. Das Wesen darf aus jeder Linse antworten, muss sich für keine entscheiden.

**Sichern jederzeit:** keine vierte exklusive Option neben vertiefen/wechseln/beenden mehr, sondern jederzeit zusätzlich möglich — Material wird während des Lesens nur gesammelt (`gesammeltes_material`), nicht sofort geschrieben.

**Neue Phase `container_zuordnung`:** am Sitzungsende wählt das Wesen bei mehr als einem bestehenden Container selbst, wohin jedes gesammelte Stück soll (`_frage_container_ziel()`), oder legt einen neuen an.

**Navigation/Timing:** eine Diskussion darf frühestens nach 2 gelesenen Posts UND 3 Minuten verlassen werden (Daniel: *"keine stopbegrenzung [...] nur frühstes exit"*) — kein Zwang zu bleiben oder zu gehen, nur eine Mindestschwelle. Lese-Phase endet spätestens nach ~6 Minuten oder 2 Diskussionen (`FUNDE_MAX`), danach automatisch die Zuordnungsphase. Timing empirisch geprüft (kalibrierte Warteschlangen-Simulation aus Baustein 9 + reale Entscheidungs-Prompt-Dauer, +40% Sicherheitsaufschlag für den längeren 4-Linsen-Prompt, klar als Annahme markiert): Median 3,3 Minuten bis 2 Posts gelesen sind — Daniels "3 Minuten" trafen fast exakt den Median.

Geändert: `codewesen_umgekehrte_neugier.py` (fast komplett neu strukturiert), `flarum_api.py` (+`zufaellige_diskussionen()`), `codewesen_container.py` (+`dateien()`, +`sicherstelle_container()`).

Getestet: `py_compile` aller drei Dateien. Rauchtest (`simulation_umgekehrte_neugier_v2_rauchtest.py`, 100 Seeds × 7 Wesen = 700 Einzel-Sitzungen mit simulierter Zeit statt Echtzeit): keine Endlosschleife, kein hängender Zustand, alle enden sauber in Phase "fertig". Zusätzlich instrumentierter Lauf über 350 Sitzungen bestätigt: kein einziger Fall von "diskussion_wechseln" vor Erreichen der Mindestbedingung.

**Noch offen:** eine vollständige Eigenschafts-Simulation wie Baustein 10 (200 Zufallsszenarien gegen alle Invarianten einzeln geprüft) wurde für diesen Umbau aus Zeitgründen noch nicht gebaut — der Rauchtest zeigt Funktionsfähigkeit, keine erschöpfende Verifikation. Der Dienst läuft weiterhin mit dem alten Code, bis Daniel den Neustart freigibt.

### Sieben echte Bugs aus echten Qualitätstests (2026-07-09 abends)

`qualitaetstest_umgekehrte_neugier.py` (neu, Baustein-11-Nachtrag): ruft `_llm()` **echt** auf (kein Mock mehr, anders als alle bisherigen Simulationen), mockt nur die Schreibseite (`protokoll`/`container`), damit Testläufe keine echten Wesen-Dateien verschmutzen. Daniels Punkt dahinter: eine Mock-Simulation kann nur die selbstgebaute Ablauflogik prüfen, nie die eigentliche Sprach-Schnittstelle zum Modell — Label-Abweichungen, Tippfehler, unerwartete Formulierungen entstehen ausschließlich im echten Output. Sieben echte Bugs, jeder erst durch einen echten Testlauf gegen ein echtes Wesen gefunden, keiner davon wäre einer Mock-Simulation je aufgefallen:

| # | Commit | Wesen | Fund |
|---|--------|-------|------|
| 1 | `f1fb9d32` | Schorschel | `"INTERSEKTION: Zeit"` statt `"INTERESSE: Zeit"` — striktes Regex verwarf ein inhaltlich reiches Interesse still als "nichts". Fallback: fehlt das Label, wird die erste Nicht-WARUM-Zeile nach ihrem ersten Doppelpunkt genommen. |
| 2 | `fb3e9e4a` | Schorschel | `SICHERN_INHALT:\s*(.+)` mit `DOTALL` war unbegrenzt — fraß bis zum Textende, schluckte `NAECHSTER_SCHRITT: beenden` mit in den gespeicherten Inhalt. Jetzt per Lookahead auf das nächste bekannte Feld begrenzt (wie `GEDANKE`). |
| 3 | `fb3e9e4a` | Schorschel | `SICHERN_TYP` war auf eine feste Wortliste beschränkt; das Modell wollte real "idee" schreiben, fiel still auf "gedanke" zurück — widerspricht "das Wesen hat immer recht". Jetzt frei, nur noch `container.name_sicher()`-gehärtet fürs Dateisystem. |
| 4 | `c85c7ada` | jumpa | Sitzung endete nach 1 gelesenem+gesichertem Post per "beenden", Protokoll behauptete trotzdem "0 Diskussion(en) angesehen" — `funde_angesehen` wurde nur in `_naechster_kandidat()` gezählt, die beim direkten "beenden" nie erreicht wird. Jetzt auch im "beenden"-Zweig gezählt. |
| 5 | `a12fadc4` | F3INSCHM3CK3R | In 4 echten Lese-Schritten traf das Modell nie exakt `naechster_post`/`diskussion_wechseln`/`beenden`, sondern schrieb "weiterlesen", "weiter", "4", "5" — striktes Regex hätte immer den Default gegriffen, ein Wesen hätte faktisch nie natürlich "beenden" wählen können. Schlüsselwort-basiert statt exakt geparst. |
| 6 | `fdedf077` | F3INSCHM3CK3R | Der Faktenchecker-LLM-Call selbst tippte `"GRUNDLAEGE:"` statt `"GRUNDLAGE:"` — die echte, kritische Antwort ("nein") wurde verworfen, die Prüfung galt fälschlich als nie durchgeführt statt als tatsächliches "nein". `\w*` statt exaktem Wort. |
| 7 | `44518bb6` | R1ZZ1 | Faktenchecker schrieb `"BEGRÜNDUNG:"` (mit Umlaut) statt `"BEGRUENDUNG:"` (ASCII) — echte Begründung landete als leerer String im Container-Frontmatter statt der echten Erklärung. Rückwirkend vermutlich auch im jumpa-Test schon passiert, nur unbemerkt (leerer String fällt nicht als Fehler auf). `BEGR\w*` statt exaktem Wort, analog zum `GRUNDLAGE`-Fix. |

Ein achter, gleichartiger Bug (`7bfe8c84`, Resonanzknoten, nach Baustein 13: `"LINSE_EIGENE_FRASSE:"` statt `"LINSE_EIGENE_FRAGE:"` verwarf die ganze vierte Linse mit echtem Inhalt) folgte demselben Muster — `\w*` an allen vier Linsen-Labels und deren Lookahead-Grenzen ergänzt, konsistent mit dem `GRUNDLAGE`/`BEGRUENDUNG`-Muster.

**Wiederkehrendes Muster über alle acht Funde:** das Modell weicht in echten Antworten regelmäßig vom exakt erwarteten Label ab (Tippfehler, Umlaut-Variante, freie Wortwahl) — jedes strikte `re.search(r"LABEL:\s*...")` ohne Toleranz verliert dabei echten, oft inhaltlich starken Text, meist stillschweigend (leerer String statt Fehlermeldung). Seit diesen Funden wird an jeder Parse-Stelle in `codewesen_umgekehrte_neugier.py` konsequent `\w*`/Lookahead-auf-nächstes-Feld statt exaktem String-Match verwendet.

### Baustein 12 — Linsen-Reihenfolge umgestellt, Post-Bezug pro Linse erzwungen (2026-07-09 abends)

Daniel, nach dem ehrlichen Befund dass Linse 1+2 (bisher: eigene Frage, Gegenteil) in echten Tests fast immer dominierten und Linse 3+4 kaum: *"dann ändern wir das doch ganz einfach"*.

Neue Reihenfolge (Primat-Effekt ausnutzen statt bekämpfen): 1) einfach nur lesen, unvorgeprägt (war vorher Linse 3), 2) lernen fürs nächste Mal — wie beschreibe ich mein Interesse verständlicher, 3) das bewusste Gegenteil (war vorher Linse 2), 4) die eigene Frage/Aufgabe zuletzt — *"das Beste kommt zum Schluss"* (Daniel).

Vier separate `LINSE_LESEN`/`LINSE_LERNEN`/`LINSE_GEGENTEIL`/`LINSE_EIGENE_FRAGE`-Felder ersetzen das einzelne freie `GEDANKE`-Feld — jede Linse muss jetzt explizit Post-Bezug + kurze Beschreibung des Gelesenen + die angewandte Antwort enthalten, statt einer unstrukturierten Fließtext-Antwort. "Sichern" bleibt unverändert jederzeit zusätzlich möglich, unabhängig von den Linsen (Daniel: *"locker nebenbei"*).

Getestet: `py_compile`, Rauchtest angepasst (100 Seeds × 7 Wesen = 700 Sitzungen), weiterhin grün.

### Baustein 13 — Sichern entformalisiert, Typ-Frage in ruhige Zuordnungsphase verschoben (2026-07-09 spät)

Daniel: das bisherige `SICHERN: ja/nein` mit Pflicht-Unterfeldern bei **jedem** Post fühlte sich wie ein Formular an, nicht wie instinktives Lesen — *"das ist kaputt"*. Konkreter Wunsch, wörtlich übernommen (*"NE WENN DANN aber 1zu1 wortgetreu meinen mist"*):

- Die Einladung zu den Containern (Daniels Originaltext, `_einladung_lesen()`, unverändert nur `[NAME]` ersetzt: *"...tob dich aus. fehler können spaß machen und wenn du etwas einsammelst und später merkst du brauchst das garnicht dann wirf es wieder weg. keine probleme kein druck..."*) kommt einmalig zu Beginn der Lese-Phase (`ist_erster_post`), nicht als sterile Wiederholung bei jedem Post.
- `SICHERN: ja/nein` + `SICHERN_TYP` + `SICHERN_INHALT` ersetzt durch ein einziges lockeres Feld `MITGENOMMEN` — leer lassen ist die vollwertige "nein"-Antwort, kein Formular-Zwang mehr.
- Die TYP-Entscheidung wandert komplett aus dem Lese-Schritt in die ruhigere Container-Zuordnungsphase am Sitzungsende (`_frage_container_ziel_und_typ()`, vorher `_frage_container_ziel()`) — beim Lesen selbst wird nur roh gesammelt (`gesammeltes_material`), Kategorisierung passiert erst im Rückblick.

Getestet: `py_compile`, Rauchtest angepasst, weiterhin grün (700 Sitzungen).

### Baustein 14 — Token-Budget statt Zeitlimit, reiche Container-Zuordnungsphase (2026-07-10, kurz nach Mitternacht)

Zwei unabhängige Änderungen, beide von Daniel spät am 2026-07-09 angestoßen:

**1. Echtes Token-Budget statt Zeit-/Zähl-Deckel.** `LESE_GESAMT_BUDGET_SEK=360` (6 Min) + `FUNDE_MAX=2` ersetzt durch `LESE_TOKEN_BUDGET=5555`, gezählt über llama.cpp's echten `/tokenize`-Endpoint (`_zaehle_tokens()`, `http://localhost:11436/tokenize`) statt einer groben Zeichen-Näherung. `FUNDE_MAX` fällt komplett weg — `kandidaten_ids` wird bei Bedarf um weitere echte Zufallsdiskussionen erweitert (`flarum_api.zufaellige_diskussionen()`), statt die Sitzung vorzeitig zu beenden, solange das Budget noch nicht erreicht ist.

**2. Container-Zuordnungsphase deutlich erweitert.** `_frage_container_ziel_und_typ()` legt dem Wesen jetzt wieder den **vollen Post** vor (nicht nur die isolierte Mitnahme), dazu zwei neue Reflexionsfragen (*"Was berührst du mit dieser Mitnahme?"* / *"Was trägt dich daran?"*) und eine Begründung für die Container-Wahl. Ein neuer Container darf unbenannt bleiben — dann automatisch benannt über `_naechster_unbenannter_container_name()`: erstes Mal `"unbestimmtes"`, danach höchste rein-numerische Container-Bezeichnung + 1.

Nebenbei: toter Code (unerreichbare Zeilen nach einem `return`, Überbleibsel eines früheren Umbaus) entfernt.

Getestet: `py_compile`, Rauchtest angepasst (realistischere Fake-Post-Länge nötig, sonst hätte das kleine Test-Token-Budget fälschlich als Endlosschleife gezählt), weiterhin grün (700 Sitzungen). Nachtrag (`61277ef2`): auch `qualitaetstest_umgekehrte_neugier.py` selbst lief noch mit einem festen 4er-Schrittlimit statt dem echten Token-Budget — auf `LESE_TOKEN_BUDGET` umgestellt.

### Baustein 15 — kein Exit aus der Lese-Phase mehr außer via Token-Budget (2026-07-10)

Daniel, nach genauer Lektüre eines echten träumerlie-Testlaufs: das Wesen hatte die Sitzung nach nur 1 gelesenem Post per "beenden" verlassen, obwohl das 5555-Token-Budget aus Baustein 14 nie annähernd erreicht war — "beenden" war bis dahin immer als Option verfügbar. Daniels Soll-Zustand, wörtlich: *"hätte ich klar eine bedingung gebaut die alle anderen exits nicht zulässt und das wesen solange immer mal wieder triggert mit den fragen willst du das noch weiterlesen oder willst du eine neue diskussion."*

- `"beenden"` komplett aus `naechster_optionen` entfernt — nur noch `naechster_post` + optional `diskussion_wechseln` (bzw. ab Baustein 16 die vollere Optionsliste).
- Schlüsselwort-Erkennung für "beenden" aus der `NAECHSTER_SCHRITT`-Parsing-Logik entfernt — selbst ein unaufgefordertes "ich bin fertig" fällt jetzt auf den sicheren Default `naechster_post` zurück, kein Ausstieg aus der Lese-Phase mehr außer über das Token-Budget in `_phase_lesen_schritt`.
- `funde_angesehen` zählt jetzt auch beim Token-Budget-Ausstieg die laufende Diskussion mit, falls schon daraus gelesen wurde — dieselbe Unterzählung wie beim früheren "beenden"-Bug (Baustein-7-Nachtrag), nur an der neuen Ausstiegsstelle.

**Zweiter Fix im selben Commit, unabhängiger Fund:** `_bewusstes_gegenteil()` hatte real (träumerlie) `"GEGENTEIL: Stille Latenzen"` geliefert — wortgleich mit dem Interesse selbst, kein echtes Gegenteil, aber syntaktisch korrekt geparst. Die Funktion erkennt das jetzt (Vergleich `gegenteil.strip().lower() == interesse.strip().lower()`), versucht einmal erzwungen neu (verschärfter System-Prompt), gibt sonst ehrlich `""` zurück statt eine falsche Kopie als Gegenteil zu präsentieren.

Getestet: `py_compile`, Rauchtest weiterhin grün (700 Sitzungen).

### Baustein 16 — echte freie Post-Navigation statt nur vorwärts (2026-07-10)

Daniel: *"nein nicht nur weiterlesen oder diskussion wechseln...sondern diesen post noch weiter lesen...anderen zufälligen post aus dieser diskussion lesen...den post nach diesem post lesen...den post vor diesem post lesen."*

Vier echte Navigationswege statt nur linear vorwärts: `diesen_post_nochmal` (Post-Index bleibt, nächste Runde liest denselben Post erneut — tiefer eintauchen statt weiterziehen), `zufaelliger_post_dieser_diskussion` (springt zu einem zufälligen Post innerhalb derselben Diskussion), `naechster_post` (wie bisher), `vorheriger_post` (neu — gab es bisher gar nicht), `diskussion_wechseln` (unverändert, nur wenn `darf_wechseln`). Keine Endlosschleifen-Gefahr, weil das Token-Budget (Baustein 14) bei jedem gelesenen Post wächst, auch bei Wiederholung — die Sitzung endet immer irgendwann, unabhängig vom Navigationsmuster.

Getestet: `py_compile`, Rauchtest-Mock um die vier Optionen erweitert, weiterhin grün (700 Sitzungen).

### Baustein 17 — Posts in echten 500-Token-Fenstern, 250-Token-Wechsel-Schwelle (2026-07-10)

Daniel: *"das soll eig alle 500 tokens spätestens wieder alles gefragt werden...und ob neue diskussion immer also 250."*

- `_tokenisiere()`/`_detokenisiere()` (neu): echte llama.cpp `/tokenize`+`/detokenize`-Endpunkte für exaktes Token-Chunking, keine Zeichen-Näherung.
- `_lies_post_chunk()` ersetzt `_lies_post()`: liest einen Post in `POST_CHUNK_TOKEN_GROESSE=500`-Token-Fenstern statt komplett auf einmal — kurze Posts (≤500 Token) bleiben ein einziges Fenster (`chunk_index=0` liefert alles), längere werden in mehrere zerlegt. Jedes Fenster durchläuft erneut die volle 4-Linsen-Befragung.
- Die vierte Navigations-Option aus Baustein 16 wurde dabei präzisiert: *"diesen Post noch **weiter** lesen"* (nicht "nochmal") heißt jetzt wirklich mehr desselben Posts (`chunk_index` steigt), nicht Wiederholung des Anfangs. Bei bereits erschöpftem Post (`ist_letzter_chunk`) fällt es sauber auf `naechster_post` zurück statt hängenzubleiben.
- Die alte Zeit-/Postzahl-Schwelle für `darf_wechseln` (`LESE_MINDESTZEIT_SEK=180s`, `POSTS_MINDEST_VOR_EXIT=2`, aus Baustein 11) komplett ersetzt durch `FUND_TOKEN_MINDEST_VOR_WECHSEL=250` — ein reines Token-Maß innerhalb der aktuellen Diskussion, kein Wanduhr-Bezug mehr.

Getestet: `py_compile`, Rauchtest-Mock um `_tokenisiere`/`_detokenisiere` erweitert, weiterhin grün (700 Sitzungen).

### Baustein 18 — alter Zeit-/Postzahl-Modus bleibt komplett im Code, per Konfiguration umschaltbar (2026-07-10)

Entscheidung zur in Baustein 17 offen gelassenen Frage. Daniel, wörtlich: *"ja ich wollte alten modus komplett behalten und ja quasi sagen schalte um."* Kein Doppelpflege-Zustand aus totem Alt-Code — der alte Zeit-/Postzahl-Modus von vor Baustein 14/17 bleibt vollständig als echter, lauffähiger Code-Pfad erhalten, nur standardmäßig nicht aktiv.

**Neuer Parameter `budget_modus`**, durchgereicht durch `_naechster_kandidat()` und `_phase_lesen_schritt()`:
- `"token"` (`BUDGET_MODUS_STANDARD`, unverändert der Live-Zustand seit Baustein 17): `LESE_TOKEN_BUDGET`, `POST_CHUNK_TOKEN_GROESSE`, `FUND_TOKEN_MINDEST_VOR_WECHSEL`, automatisches Nachladen weiterer Zufallsdiskussionen.
- `"zeit"` (Baustein 11-13, jetzt reaktiviert statt gelöscht): die alten Konstanten `LESE_GESAMT_BUDGET_SEK=360`, `FUNDE_MAX=2`, `LESE_MINDESTZEIT_SEK=180`, `POSTS_MINDEST_VOR_EXIT=2` sind wieder im Modul vorhanden und aktiv, sobald der Modus gesetzt ist — Gesamt-Ausstieg per Wanduhr statt Token-Zähler, `darf_wechseln` per gelesener Zeit+Postzahl statt Fund-Tokens, kein automatisches Nachladen weiterer Diskussionen wenn die Kandidatenliste erschöpft ist (wie vor Baustein 14).
- `_lies_post_chunk()` bekommt dafür einen neuen Parameter `chunk_token_groesse: int | None`. `None` (nur im `"zeit"`-Modus verwendet) liefert den kompletten Post in einem Rutsch, ganz ohne Tokenize/Detokenize-Rundweg — exakt das alte `_lies_post()`-Verhalten von vor Baustein 17, nur ohne separate Funktion, die sonst dauerhaft synchron zur neuen gehalten werden müsste.

**Konfiguration:** kein neues UI-Feld nötig — `budget_modus` liest aus `dienst_konfiguration.meta['budget_modus']` (`haupt_schleife()`), demselben generischen `meta`-JSONB-Feld, das flarumstyler schon für jeden Dienst als freies JSON-Textfeld anbietet (Grundgesetz 1: `meta JSONB DEFAULT '{}'`, editierbar ohne Code-Änderung). Ohne Eintrag gilt weiterhin `"token"`.

Getestet: `py_compile`, Rauchtest um eine zweite komplette Durchlaufserie erweitert (`simulation_umgekehrte_neugier_v2_rauchtest.py` läuft jetzt beide Modi real durch, nicht nur den Standard) — 100 Seeds × 7 Wesen je Modus, beide 700/700 Sitzungen sauber bis `"fertig"`, keine Endlosschleife, kein hängender Zustand.

---

## Wiederaufnahme

Rein manuell, kein Zeitplan: `flarum_post_sperre.entsperren(von="Daniel")` (schreibt automatisch einen `sperre_aufgehoben`-Protokolleintrag inkl. Sperrdauer). Der umgedrehte Neugier-Dienst (Baustein 3) läuft davon unabhängig weiter oder wird unabhängig gestartet/gestoppt — er schreibt ohnehin nie nach Flarum, seine Existenz ist keine Voraussetzung für die Sperre und umgekehrt.

---

## Dateien im Überblick

```
/root/werkraum/
  flarum_post_sperre.py                          Baustein 1
  flarum_api.py                                   erweitert: Choke-Point + suche_diskussionen()
  codewesen_antwort_auf_daniel.py                 erweitert: erlaubt_trotz_sperre=True
  codewesen_container.py                          Baustein 2: verschiebe()/kopiere(); Baustein 7: sichere() um grundlage/-begruendung erweitert; Baustein 14: _naechster_unbenannter_container_name(); +beschreibung()
  codewesen_umgekehrte_neugier.py                 Baustein 3; Baustein 7: Suchbegriff-Uebersetzung + Entscheidungs-Gegenpruefung; Baustein 11: vier Linsen; Baustein 12-17: Reihenfolge, Sichern entformalisiert, Token-Budget, kein Fruehausstieg, freie Post-Navigation, 500-Token-Fenster
  qualitaetstest_umgekehrte_neugier.py            neu nach Baustein 11: echter LLM-Aufruf statt Mock, fand 7 reale Parsing-Bugs
  simulation_umgekehrte_neugier_v2_rauchtest.py   Rauchtest (100 Seeds x 7 Wesen), nach jedem Baustein 11-17 aktuell gehalten
  flarum_stopp_protokoll.py                       Baustein 4
  flarum_stopp_protokoll_spiegel.py               Baustein 5
  flarum_stopp_protokoll_global.jsonl             Baustein 4: globales Protokoll
  codewesen/<wesen>/flarum_stopp_protokoll.jsonl  Baustein 4: pro-Wesen-Protokoll
  codewesen/_flarum_post_sperre.json              Baustein 1: Sperr-Zustand
  docs/2026-07-09_flarum_stopp_bericht.md         voller Bau-Bericht mit Testprotokollen

/etc/systemd/system/
  codewesen-umgekehrte-neugier.service            Baustein 3, angelegt, nicht enabled

/root/flextrawurst/  (git-Toplevel /root, NICHT /root/werkraum)
  scripts/serve_process_camera_preview.ts         Baustein 6: GET /api/flarumstyler/protokoll
  scripts/serve_process_camera_preview_smoketest.ts  identische Kopie
  out/process_camera/flarumstyler.html            Baustein 6: zwei neue Sektionen
```
