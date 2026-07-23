---
id: FW-MOVE-004
status: BESTAETIGT
typ: source
themenraum: MOVE
version: v21
tags: [bauen, beziehung, fahrzeug, move, playwright, provenienz, region, save, simulation, test, v21, welt, wesen, zeit]
---

# Architektur und Datenmodelle

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/05_ARCHITEKTUR_UND_DATENMODELLE.md" sha256="1cfe6b61e7200dec0d6ae7f91ff33d9963e80a786f5d84237c7ec87a39edd7c2" order="1" -->
# Architektur und Datenmodelle

## Schichten

1. `data.js` – IDs, AI-Wesen, Fahrzeuge, Baumodule, Regionen, Texte und Regeln
2. `renderer.js` – perspektivische Software-3D-Darstellung, Kamera, Geometrie und Picking
3. `world.js` – Weltaufbau, Routinen, Regionen, interaktive Objekte und Epochenvarianten
4. `game.js` – Simulation, Eingabe, Beziehungen, Bauen, Fahrzeuge, Zeit, Abspaltung, Sucht und Speicherung
5. `ui.js` – Panels, Modale, Atlas, Chronik, Bau-, Fahrzeug-, Zeit- und Testwerkzeuge
6. `tests/` – Playwright-Spielpfade und statische Prüfungen

## Stabile IDs

Alle Wesen, Fahrzeuge, Baumodule, Orte, Quellen, Ereignisse und Chronikeinträge besitzen IDs. Anzeigenamen dürfen sich ändern, Beziehungen und Provenienz hängen nicht an sichtbarem Text.

## Zustandsräume

- normaler Spielstand
- isolierte Test-Fork
- aktive Form/Abspaltung
- Gegenwart
- quellenmarkierte Vergangenheit
- bestätigte Endlinie +333
- alternative Zukunftsprojektion

## Weltgedächtnis

Jede zentrale Aktion schreibt:

- Ereignis-ID
- Spielzeit
- Form-ID
- Ort
- Ursache
- direkte Wirkung
- betroffene Systeme
- Herkunft/Quelle
- Modus normal/test

## Renderergrenze

Der Renderer liest Weltzustand, besitzt aber keine Autorität über Simulation oder Speicherung. Ein Renderfehler darf Eingabe, UI oder Save nicht zerstören.

<!-- SOURCE_SEGMENT_END source="v21:docs/05_ARCHITEKTUR_UND_DATENMODELLE.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-MOVE-003__Wesentliche_Systemkollisionen_vier_Wege_und_Entscheidung.md) · `FW-MOVE-003`
- [Nächster Knoten](FW-MOVE-005__F-0197_BESTANDEN.md) · `FW-MOVE-005`
- [Themenindex](00_INDEX.md) · `FW-INDEX-MOVE`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: Test, Redteam, Abnahme](FW-MOVE-001__Test_Redteam_Abnahme.md) · `FW-MOVE-001`
- [Verwandt: K045-Q5 · K045 · Fehlurteil × Beziehungen](FW-MOVE-023__K045-Q5_K045_Fehlurteil_Beziehungen.md) · `FW-MOVE-023`
- [Verwandt: COPY-PASTE-MASTERPROMPT – MAXUS++++++++++++++++ Bauring 2](../10_CREATORWELTEN_EREIGNISSE_ARCHIVE/FW-CREATOR-001__COPY-PASTE-MASTERPROMPT_MAXUS++++++++++++++++_Bauring_2.md) · `FW-CREATOR-001`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
