# Codereview wichtiger Systeme und Organe

Stand: 2026-06-02

Scope: gelesen und bewertet wurden die zentralen Python-Systeme in `welt/`, die Gruppen-/Ampel-Erweiterung, die Surface-HTML, sowie die alten Flarum-Codewesen-Schichten. Es wurde kein Code veraendert.

## Berichte

- `01_welt_api_auth_public.md` — Welt-API, Auth, Public/Profile/Resonanz.
- `02_wesen_kern_takt_schlaf.md` — Entity-Kern, Takt, Schlaf- und Traumwege.
- `03_organe_cyberling_splitter_tension.md` — Cyberling, Splitter-Physik, Similarity, Tension/Substanzen.
- `04_gruppen_ampel.md` — Gruppen-API, Chat, Materialien, Einzugsampel v4.
- `05_organ_hunger_life_contracts.md` — Organhunger und Admin-Einsicht.
- `06_surface_frontend.md` — Surface-HTML, Token-Handling, Build-/Test-Drift.
- `07_flarum_codewesen.md` — alte Flarum-Codewesen, Flarum-API, Engagement-Loop.

## Hohe Risiken auf einen Blick

1. Public/Admin-Grenzen sind an mehreren Stellen nur UI- oder Query-Parameter-basiert: `admin=true` auf public Routen, interne Gruppen sichtbar, Chat/Materialien ohne ausreichende Rechtepruefung.
2. Wesen- und Organlogik ist mehrfach implementiert: Cyberling-Verfall in `entity_kern.py` und `cyberling_daemon.py`, Schlafstart in API und Kern, Traum/Takt in getrennten Pfaden. Das erzeugt widerspruechliche Zustaende.
3. Einige Daemons verlieren Arbeit oder fluten Daten: Splitter-Daemon verarbeitet nur Events der letzten 65 Sekunden, Tension-Daemon schreibt Sedimente ohne Deduplikation, Tamagotchi-Events koennen dauerhaft wiederholt werden.
4. Einzugs-/Bereitschaftsgrenzen sind unscharf: `entity_kern.py` denkt fuer `status IN ('eingezogen', 'bereit')`; Ampel v4 meldet mehrere Checks hart gruen.
5. Frontend und API sprechen nicht durchgehend dasselbe Token-Format: Tokens werden als `Bearer ...` gespeichert, an einigen Stellen aber erneut mit `Bearer ` gepraefixt.

## Empfehlung fuer naechste Schritte

1. Erst Rechte- und Sichtbarkeitsfehler beheben: Public API, Gruppen, Chat, Materialverknuepfung, Shadow/Profil-Leaks.
2. Danach Einzugsgrenze klaeren: `bereit` darf entweder nur simulieren oder muss eindeutig nicht oeffentlich handeln.
3. Dann Organ-Duplikate auf eine Quelle reduzieren: Cyberling, Schlaf, Traum, Schattenantwortstatus.
4. Daemons idempotent machen: keine Zeitfenster-Drops, keine dauernden Duplicate-Events, keine unescaped `tsquery`.
5. Surface-Pipeline wiederherstellen oder AGENTS-Regel an Realitaet anpassen.
