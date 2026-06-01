# Review: Wesen-Kern, Takt, Schlaf und Traum

## Kritisch

- Der Denkloop laeuft auch fuer `bereit`, nicht nur fuer `eingezogen`. `/root/werkraum/welt/entity_kern.py:991` bis `:1000` selektiert `status IN ('eingezogen', 'bereit')`. Da `gedanke_posten` oeffentliche Posts erzeugen kann, kann ein vor-eingezogenes Wesen bereits in die Welt handeln. Das widerspricht der Einzugsgrenze, sofern `bereit` nur Vorschaltzustand sein soll.

- Cyberling-Verfall existiert doppelt und widerspruechlich. `/root/werkraum/welt/entity_kern.py:424` bis `:480` veraendert Cyberling-Werte direkt im Denkprozess. Parallel macht `/root/werkraum/welt/cyberling_daemon.py` ein eigenes Profil-/Recovery-/Wiedergeburtsmodell. Die Wiederbelebungszeiten und Statusregeln sind unterschiedlich. Ergebnis: welcher Zustand stimmt, haengt vom letzten Schreiber ab.

- Schattenantworten werden nicht als beantwortet markiert. `/root/werkraum/welt/entity_kern.py:652` bis `:656` nimmt irgendeinen Schatten auf eigenem Post, `/root/werkraum/welt/entity_kern.py:637` bis `:642` schreibt nur eine Antwort. Es fehlt ein Update auf `schattenkommentare.antwortstatus`. Dadurch kann derselbe Schatten mehrfach beantwortet werden und Organhunger bleibt offen.

- `aktuell_denkend` kann bei normalen Exceptions haengen bleiben. Der Kern setzt den Zustand vor dem LLM-Lauf, aber der generische Catch in `/root/werkraum/welt/entity_kern.py:1048` bis `:1049` loggt nur. Nur Timeout-Pfade setzen aktiv zurueck. Ein Insert-/DB-/Parsing-Fehler kann das Wesen dauerhaft als denkend markieren.

## Hoch

- Der Takt erzwingt Schlaf anhand der letzten Schlafphase irgendeines Wesens. `/root/werkraum/welt/entity_takt.py:114` bis `:121` filtert `sleep_phases` nicht nach dem aktuellen `entity_id`. Eine frische Schlafphase von Wesen A beeinflusst damit Wesen B-F.

- API und Kern starten Schlaf unterschiedlich. `/root/werkraum/welt/entity_kern.py:688` bis `:716` schreibt direkt `sleep_phases` und Event `schlaf.begonnen`; die API-Schicht nutzt andere Regeln und Events. Damit koennen Pflichtbedingungen wie Schlafbrief, Eventnamen und Statusdrift auseinanderlaufen.

- Prompt und erlaubte Aktionen widersprechen sich. `/root/werkraum/welt/entity_kern.py:278` sagt dem Wesen, es koenne Schattenkommentare schreiben. `AKTIONEN` in `/root/werkraum/welt/entity_kern.py:35` bis `:48` deaktiviert das Schreiben aber faktisch und erlaubt nur Antworten. Das erzeugt unnoetige Fehlentscheidungen.

- Lokaler Kontext kann eigene alte Posts als fremd markieren. `/root/werkraum/welt/entity_kern.py:155` bis `:164` schliesst nur die letzten eigenen Posts aus. Aeltere eigene Posts koennen spaeter als `[FREMD - autor]` in den Prompt laufen.

## Mittel

- `entity_takt.py` enthaelt harte Admin-Credentials. `/root/werkraum/welt/entity_takt.py:31` nutzt `entity_takt` / `takt2026`. Das gehoert in Secret/Env und sollte nicht im Code stehen.

- API-Aufrufe im Takt haben keine Timeouts. Mehrere Requests in `/root/werkraum/welt/entity_takt.py:234`, `:242`, `:255`, `:265`, `:276` koennen den Daemon haengen lassen, wenn die API nicht antwortet.

- Trauminput nutzt vermutlich eine falsche Tabelle. `/root/werkraum/welt/entity_takt.py:380` bis `:384` liest `traumtagebuch`; die neueren Routen arbeiten mit `mw_traumtagebuch`. Wenn keine Alt-Tabelle existiert, faellt der Trauminput still aus oder bricht.

- `menschenprofil_lesen` waehlt Menschen zufaellig ohne Aktiv-/Sichtbarkeitsfilter. `/root/werkraum/welt/entity_kern.py:783` bis `:802` kann dadurch private oder inaktive Profile in den Wesenfokus ziehen.

## Tests, die fehlen

- Ein Wesen mit Status `bereit` darf keine oeffentlichen Posts erzeugen, solange Einzug nicht explizit freigegeben ist.
- Schattenantwort setzt den Schattenstatus auf beantwortet und verhindert Doppelantwort.
- Schlafentscheidung fuer Wesen B darf nicht von Schlafphase Wesen A abhaengen.
- Nach simulierter DB-Exception muss `aktuell_denkend=false` sein.
