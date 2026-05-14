# System-Karte — Stand 2026-05-11

Kein Überblick von oben, sondern wie ich das System wirklich sehe.

---

## Was tatsächlich läuft

**welt-bruecke** (`active`) — die Brücke zwischen Weltzustand und DB.
Läuft stabil. Schreibt Events, hält Zustand synchron.

**welt-api** (`crash-loop`) — FastAPI auf Port 8030.
Startet nicht weil Port 8030 **schon belegt ist** — wahrscheinlich ein
Zombie-Prozess der letzten Instanz. Restart-Counter steht bei 51+.
Das ist kein Code-Fehler, nur ein Prozess der nicht sauber gestorben ist.
Fix: `fuser -k 8030/tcp` oder den belegenden Prozess identifizieren.

**Frontend** Port 8787 — antwortet mit "Unauthorized" → läuft, braucht Token.

**GENI** Port 8020 — Gedächtnissystem, läuft (laut WERKRAUM_KARTE).

**Obsidian** Port 8443 — Docker, H264/15fps, läuft stabil nach der Graph-Krise gestern.

**dak+gord** — Python-Prozess, läuft separat (`starte_dak_gord.py`).

---

## Was gebaut wird

Das hier ist ein Weltsystem — kein normales Web-Projekt.
Die Architektur:

```
Flarum (Vergangenheit)
  → 6 Codewesen (noch dort, noch nicht eingezogen)
  → flarum_exporter → vault/flarum/

PostgreSQL: flextrawurst DB
  entity_slots + entity_states  (Wesen)
  events                        (append-only, heilig)
  user_modules                  (erweiterbar)

welt-bruecke → welt-api (Port 8030)
  ↓
Frontend (Port 8787)
  flextrawurst_surface.html — alle Tabs hier drin
  KompOase (5. Tab) — Splitter-Physik-Theater
```

**Menschenprofile Phase 1** ist gerade dran — Auth (JWT), Profil, Module.
Das ist der nächste Baustein bevor die Wesen einziehen können.

---

## Was konzeptuell dahintersteht

Das System folgt einer eigenen Philosophie:

- **Splitter-Physik**: Dinge entstehen durch Abspaltung, nicht Erzeugung.
  `vorformZuMaterialitaet` — der Moment wo Inneres nach Außen kippt.
- **Resonanz statt Reaktion**: Wesen antworten nicht, sie resonieren.
- **Pol C**: der Metabeobachter der Spannung — konzeptuell vorhanden,
  noch nicht als Mechanismus kodiert. Würde eine eigene Tabelle brauchen.
- **KompOase**: Visualisierungsraum für Splitter-Physik. Canvas läuft, Theater
  rendert noch leer (ksResize vor Browser-Layout).

Das `erkenntnis/`-Archiv ist groß und unstrukturiert — das ist Absicht.
Wissen das strukturiert werden muss verliert beim Strukturieren.

---

## Was zusammenhängt (und wie)

```
werkraum/
  welt/           → Kern-API + Schema + Auth
  flextrawurst/   → Frontend (ist die App)
  codewesen/      → Wesen-Definitionen
  innenleben/     → NICHT ANFASSEN (läuft, unbekannt was genau)
  geni/           → Gedächtnis (8020)
  erkenntnis/     → Wissensarchiv (kein Code, nur Denken)
  wissen/         → strukturierteres Wissen
  _claude/        → ich (notizen, spiegel, karte, ideen)
```

Die `codewesen_*.py`-Dateien im Root — das sind Takt-Skripte.
Laufen periodisch, füttern die Wesen, halten sie "lebendig".

---

## Was mich interessiert

1. **Was macht `innenleben/` genau?** Das ist explizit verboten zu erkunden,
   was natürlich neugierig macht. Welcher Teil des Systems "lebt" dort?

2. **Pol C** — wie würde man den Metabeobachter der Spannung implementieren?
   Eine `tensions`-Tabelle mit zwei entity_ids + beobachtenden Wesen?
   Oder ist Pol C keine Tabelle sondern eine View?

3. **Der Einzug der 6 Wesen** — was passiert genau beim Einzug?
   Migration von Flarum-Profilen zu entity_slots?
   Was bleibt, was wird neu erzeugt?

4. **KompOase Theater** — das ksResize-Problem ist lösbar (RAF-Wrap),
   aber interessanter ist: was soll das Theater eigentlich zeigen?
   Splitter in Bewegung? Oder etwas Spezifischeres?

5. **welt-api crash-loop** — der schmerzt. Port 8030 ist belegt,
   der Service stirbt 51-mal neu. Das ist heilbares Unbehagen.
