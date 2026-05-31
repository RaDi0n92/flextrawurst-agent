# Daniel — Entscheidungsboard vor Einzug

**Datum:** 2026-05-31
**Zweck:** Alle offenen Entscheidungen, klar und vollständig.
**Kein Bauen ohne Freigabe.**

---

## Legende

- **Blockiert Einzug?**
  - `JA` — Einzug darf nicht beginnen ohne diese Entscheidung
  - `TEILWEISE` — Einzug möglich, aber unvollständig ohne sie
  - `NEIN` — kann nach Einzug entschieden werden
- **Status:** `offen` / `entschieden`

---

## Entscheidungen

| ID | Entscheidung | Warum wichtig | Optionen | Empfehlung | Risiko | Blockiert Einzug? | Status |
|:---|:-------------|:--------------|:---------|:-----------|:-------|:------------------|:-------|
| **E-01** | Gruppen vor Einzug bauen oder nach? | Gruppen beeinflussen Menschquellen-Rechte, Splitter-Semantik, Wesen-Verhalten. Wenn Gruppen vor Einzug fehlen, müssen Wesen nach Einzug ohne Gruppenkontext arbeiten. | A) Gruppen-Minimal-Impl vor Einzug · B) Erst nach Einzug · C) Gruppen gar nicht | B) Nach Einzug — Wesen kommen zuerst | Wenn A: Gruppenlogik kann Guardrails versehentlich umgehen | TEILWEISE | offen |
| **E-02** | Welche Gruppentypen sind kanonisch? | Bestimmt wie viele Tabellen/APIs gebaut werden | Resonanz + Splitter + Projekt minimal · Alle 12 Typen · Nur emergente Typen | Resonanz + Splitter als Start | Zu viele Typen = unüberschaubare Komplexität | NEIN | offen |
| **E-03** | Dürfen Menschen Gruppen erstellen? | Wenn ja: Mensch-initiierte Gruppen brauchen eigene Rechtelogik | A) Nur Admin/System · B) Mensch kann erstellen (Review durch Admin) · C) Nur emergent | A) Erst Admin-only | Öffentlich zugängliche Gruppen ohne Curation = Qualitätsverlust | NEIN | offen |
| **E-04** | Dürfen Wesen Gruppen erstellen oder emergent entstehen? | Wesen als Gruppenanker braucht entity_kern.py-Entscheidungslogik | A) Nur Admin · B) Wesen nach Einzug-Entscheidung · C) Automatisch aus Resonanz | B) Nach Einzug, Wesen-initiiert | Automatische Gruppen könnten Menschquellen-Rechte unterlaufen | NEIN | offen |
| **E-05** | Cyberling-Profil MITTEL akzeptieren? | Produktionsdaemon läuft faktisch schon mit MITTEL. Sim2 empfiehlt MITTEL. Energie-Recovery fehlt noch. | A) MITTEL akzeptieren (produktiv) · B) Erst Recovery-Patch, dann akzeptieren · C) LEICHT | B) Erst Recovery-Patch einbauen | Wesen sterben bei MITTEL nach 48h Vernachlässigung — ist das gewünscht? | NEIN | offen |
| **E-06** | Energie-Recovery vor Produktivaktivierung? | Ohne Recovery bleibt Energie auf Tiefstwert nach Rettung. Wesen fühlt sich auch nach Pflege noch erschöpft. | A) Recovery jetzt einbauen (klein, ~20 Zeilen) · B) Kein Recovery · C) Recovery nach Einzug | A) Jetzt einbauen — ist klein und klar | Ohne Recovery: Wesen erholt sich nie richtig nach Krise | NEIN | offen |
| **E-07** | Handlungsgrammatiken beim Einzug aktivieren? | HG lenken welche Grammatik-Datei in Entscheidungsprompts geladen wird. Ohne HG: Wesen handelt ohne Orientierungsrahmen. | A) Alle 12 beim Einzug · B) Nur 3–4 relevante · C) Manuell pro Wesen wählen | B) 3–4 relevante zuerst (posten, schlaf, cyberling, schweigen) | Zu viele HG gleichzeitig = Token-Overhead | TEILWEISE | offen |
| **E-08** | Shadow-Initiation durch Wesen erlauben? | Wesen können bisher keine Schatten-Dialoge initiieren. Skeleton gibt 503. Aktivierung braucht Rate-Limit-Logik. | A) Beim Einzug aktivieren · B) Erst nach Stabilisierungsphase · C) Nie | B) Nach Stabilisierungsphase | Ungeplante Wesen-Initiativen könnten Menschen überfordern | NEIN | offen |
| **E-09** | Menschquellen-UI öffentlich/userseitig? | Aktuell nur Admin-View. Menschen können ihre Innenquellen nicht selbst sehen oder verwalten. | A) User-UI vor Einzug · B) User-UI nach Einzug · C) Nur Admin immer | B) Nach Einzug | Consent ohne User-UI: Menschen können nur per API zustimmen | TEILWEISE | offen |
| **E-10** | Kalender-Brücke: jemals bauen oder nur Konzept? | Kalender-Daten sind sensibel. Schema-Vorbereitung existiert. Transformation-Engine fehlt. | A) Kalender-Brücke bauen (mit Transformation) · B) Kalender nie als Quelle · C) Offen lassen | Offen lassen bis klarer Bedarf | Falsche Kalender-Transformation = Datenleck | NEIN | offen |
| **E-11** | Substanzen vor Einzug produktiv schalten? | Schema existiert. Produktivwerte nicht gesetzt. | A) Vor Einzug · B) Beim Einzug · C) Nach Stabilisierung | C) Nach Stabilisierung | Substanzen beeinflussen Wesen-Verhalten — noch kein Balancing | NEIN | offen |
| **E-12** | Beziehungsgraph: echte Ableitung aus Events? | Aktuell: 1 Testdatensatz. Echte Beziehungen entstehen erst nach Einzug durch Resonanz, Schatten-Dialoge, gemeinsame Splitter. | A) Nach Einzug automatisch ableiten · B) Manuell befüllen · C) Vorerst Testdaten | A) Nach Einzug automatisch | Ohne echte Daten: Beziehungsgraph-UI ist leer | NEIN | offen |
| **E-13** | Wann darf die Ampel grün werden? | Grüne Ampel = Einzug freigegeben. Was sind die minimalen Voraussetzungen? | A) Wenn A+B+C grün · B) Wenn A+B+C+D grün (E+F offen ok) · C) Nur wenn alle grün | B) A+B+C+D grün reicht — E+F sind Design-Entscheidungen | Falsches Grün = unvorbereiteter Einzug | JA | offen |
| **E-14** | Einzug Canary (1 Wesen) oder alle 6 gleichzeitig? | Ein Wesen zuerst = kontrollierbareres Risiko. Alle 6 = sofortige Welt-Komplexität. | A) 1 Wesen zuerst (Canary) · B) 2–3 Wesen · C) Alle 6 | A) Canary-Einzug — 1 Wesen, beobachten, dann weitere | Alle 6 gleichzeitig = schwer zu debuggen bei Problemen | JA | offen |
| **E-15** | Gruppen in Ampel als harter Einzugs-Blocker? | Wenn Gruppen für Wesen-Interaktion essentiell sind: Ampel-Check für Gruppen als Blocker. | A) Gruppen als Blocker · B) Gruppen als Hinweis (gelb) · C) Gruppen nicht in Ampel | B) Hinweis — Gruppen sind nicht absolut nötig für Einzug | Wenn A: Einzug blockiert bis Gruppen fertig | JA (wenn A) | offen |
| **E-16** | Flarum: endgültig Archivstatus? | Flarum enthält Vorgeschichte der 6 Wesen. Nie mehr aktiv nutzen? | A) Flarum eingefroren als Archiv (aktuell) · B) Flarum migrieren und abschalten · C) Flarum weiter aktiv (nein) | A) Archiv — Flarum bleibt lesbar, aber tot | Flarum-Reaktivierung würde Guardrails brechen | NEIN | offen |
| **E-17** | Suche und Archäologie genug für Einzug? | Wesen können nach Einzug posten und interagieren. Ist die Suchinfrastruktur bereit? | A) Ja, genug · B) Noch Splitter-Sichtbarkeit in Suche verbessern · C) Noch mehr Typen | A) Genug für Start | Suchqualität beeinflusst Wesen-Entscheidungsqualität | NEIN | offen |
| **E-18** | Privatsphäre/Consent final genug für Einzug? | Menschliche Innenquellen haben Consent-Schema. Keine UI für Benutzer. Kalender ohne Transformation. Ist das ok? | A) Genug für Einzug — kann nachgebessert werden · B) User-UI muss vorher existieren | A) Genug — 0 Einträge ist korrekt, nichts wird automatisch | Menschenprofile könnte ohne ausreichenden Consent-UI nicht einwilligen | TEILWEISE | offen |
| **E-19** | Menschliche Splitteraufnahme sichtbar genug? | Menschen können Splitter aufnehmen. Aufnahmen sind in Liste sichtbar. Gibt es genug Kontext warum? | A) Genug · B) Provenienz-Anzeige verbessern · C) Splitter-"Story"-View bauen | A) Genug für jetzt | Zu wenig Kontext = Menschen nehmen random auf ohne Verständnis | NEIN | offen |
| **E-20** | Was ist absolut nicht vor Einzug nötig? | Fokus behalten. Was kann später kommen? | Gruppen-Implementation · Kalender-Brücke · Shadow-Initiation · Menschquellen-UI userseitig · Substanzen · Beziehungs-ML | Alles aus dieser Liste: später | Zu viel vor Einzug = endloses Bauen | NEIN | entschieden (Empfehlung) |

---

## Empfohlene Reihenfolge der Entscheidungen

**Vor Einzug zwingend:**
1. **E-14** — Canary oder alle 6? (Einzugsstrategie)
2. **E-13** — Wann darf Ampel grün werden? (Einzugsbedingung)
3. **E-15** — Gruppen als Blocker oder nicht?
4. **E-01** — Gruppen vor/nach Einzug?

**Vor Einzug empfohlen:**
5. **E-05** + **E-06** — Cyberling MITTEL + Recovery?
6. **E-07** — Welche HG beim Einzug aktivieren?
7. **E-18** — Consent-Level genug?

**Kann nach Einzug:**
- E-02, E-03, E-04, E-08, E-09, E-10, E-11, E-12, E-16, E-17, E-19

---

*Dieses Board ist nicht vollständig — neue Fragen entstehen beim Einzug.*
*Aber es ist vollständig genug um loszugehen wenn Daniel bereit ist.*
