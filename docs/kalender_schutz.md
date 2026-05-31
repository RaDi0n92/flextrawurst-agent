# Kalender-Schutz — Konzept und Schema-Vorbereitung

**Datum:** 2026-05-31
**Status:** Konzept vorbereitet, keine automatische Verarbeitung aktiv

---

## Grundsatz

Kalender ist besonders sensibel. Er enthält Taktung, Druck, Bewegungsprofile, Namen,
Termine, Orte und soziale Verbindungen — ohne Kontext hochgradig interpretierbar.

**Kein Kalender-Rohdaten-Import ohne Transformation und explizite Zustimmung.**

---

## Was NICHT passiert

- Kein automatischer Import: `"Daniel hat Dienstag 13:00 Termin X"` wird nie direkt zu Splitter
- Kein Bewegungsprofil öffentlich
- Keine Namen/Orte/Zeiten roh sichtbar
- Keine automatische Verarbeitung bei Kalender-Sync

---

## Was MÖGLICHERWEISE passiert (nur mit Consent + Transformation)

Transformiertes Beispiel (erlaubt):
> "Ein menschlicher Tag trägt Druck, Taktung, Verschiebung von Ruhe."

Mit Herkunft nur bei klarer Freigabe:
> "Aus Daniels Kalenderstruktur entsteht ein Splitter über Druck, Rhythmus
>  und verschobene Aufmerksamkeit."

---

## Schema-Vorbereitung in `human_material_sources`

`source_type = 'human_calendar'` kann bereits eingetragen werden.
`meta`-Feld trägt alle Kalender-spezifischen Flags:

```json
{
  "raw_sensitive": true,
  "requires_transformation": true,
  "calendar_transform_note": "Rohinhalt nicht exportierbar — nur abstrahierte Struktur erlaubt",
  "allowed_transformation_types": ["rhythm_pattern", "pressure_level", "attention_shift"],
  "original_ref": null
}
```

Diese Felder werden vom `to-splitter`-Endpunkt **noch nicht aktiv geprüft**.
Das ist Absicht — kein Kalender-Code gebaut bevor Daniel freigibt.

---

## Herkunfts-/Rechtemodi für Kalender

| Modus | Bedeutung |
|:------|:----------|
| `consent_status = 'offen'` | Default — nichts wird verarbeitet |
| `consent_status = 'erteilt'` | Transformation erlaubt (noch nicht aktiv) |
| `quote_permission = 'privat'` | Nur interne Verwendung |
| `quote_permission = 'anonym_erlaubt'` | Abstrahierte Version ohne Namen |
| `quote_permission = 'namentlich_erlaubt'` | Klare Herkunft erlaubt |
| `anonymization_mode = 'full'` | Alle identifizierenden Merkmale entfernen |
| `meta.raw_sensitive = true` | Transformation Pflicht vor Splitter |

---

## Wenn Kalender-Brücke gebaut wird (noch nicht freigegeben)

Voraussetzungen:
1. Daniel gibt explizit frei: "bau die Kalender-Brücke"
2. Transformation-Engine existiert (nicht Rohdaten)
3. Consent-UI für Kalender-Freigabe existiert
4. Test: Rohdaten tauchen NICHT in Splitter oder Suche auf
5. `meta.raw_sensitive` wird im `to-splitter`-Endpunkt aktiv geprüft

Bis dahin: `/api/human-material/{id}/to-splitter` prüft `meta.raw_sensitive` nicht.
Kalender-Splitter können daher aktuell noch NICHT korrekt blockiert werden.
Das ist kein Bug — Kalender-Quellen sollten bis zum Kalender-Brücken-Build
nicht eingetragen werden.

---

## Surface-Hinweis

Im EINSICHT INNENQUELLEN-Tab wird bei `source_ref_table = 'kalender'`
ein roter Hinweis angezeigt:
> "⚠ Kalenderquelle — Transformation erforderlich vor Splitter-Erzeugung."

---

*Dieser Schutz ist konzeptionell fertig. Der Code ist bewusst nicht gebaut.*
*Einzug und Kalender-Bridge sind unabhängige Entscheidungen.*
