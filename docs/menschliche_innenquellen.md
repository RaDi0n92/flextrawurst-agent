# Menschliche Innenquellen

Dokument für flextrawurst — Herkunfts- und Consent-Schicht für menschliche Inhalte.

---

## Was sind Menschliche Innenquellen?

Menschliche Innenquellen sind alle Inhalte, die ein Mensch in seiner persönlichen Welt erzeugt hat:
Notizen, Tagebuch, Traumtagebuch, Kalender, Gedankenblasen, gespeicherte Zitate, Erinnerungsmarker.

Diese Quellen können — mit ausdrücklicher Zustimmung — Splitter erzeugen, die dann im Zwischenraum/KompOase treiben.

**Default ist privat.** Nichts wird automatisch verwendet.

---

## Welche Quellen gibt es?

| source_type | Tabelle | Beschreibung |
|:------------|:--------|:-------------|
| `human_note` | `mw_notizen` | Notizen, Gedanken, Aufgaben |
| `human_diary` | `mw_tagebuch` | Tagebucheinträge |
| `human_dream_diary` | `mw_traumtagebuch` | Traumtagebuch |
| `human_calendar` | `mw_kalender` | Kalendereinträge |
| `human_thought_bubble` | `gedankenblasen` | Gedankenblasenfeld |
| `human_shadow_comment` | `schattenkommentare` | Geteilte Schatten-Dialoge |
| `human_quote` | — | Gespeicherte Zitate |
| `human_memory_marker` | — | Erinnerungsmarker (zukünftig) |

---

## Default: privat

Alle Innenquellen landen zunächst in `human_material_sources` mit:

```
consent_status = 'offen'
visibility_layer = 'private'
quote_permission = 'privat'
origin_visibility = 'privat'
```

Kein Wesen, kein Suchergebnis, kein öffentlicher Kontext bekommt Zugriff, bis ein Mensch ausdrücklich zustimmt.

---

## Wie entsteht ein Splitter?

Ein Splitter aus einer Innenquelle entsteht nur durch explizite API-Aktion:

```
POST /api/human-material/{id}/to-splitter
```

**Voraussetzungen:**
1. `consent_status == 'gegeben'` — Mensch hat aktiv zugestimmt
2. `quote_permission in ('erlaubt', 'anonym_erlaubt')` — Verwendungsrecht erteilt

Der Splitter trägt dann:
- `origin_type = 'human_material'`
- `origin_id = source_id`
- `herkunft_sichtbar = true` wenn `quote_permission == 'erlaubt'` (mit Herkunft)
- `herkunft_sichtbar = false` wenn `quote_permission == 'anonym_erlaubt'` (anonym)
- `herkunft_wesen` = `public_origin_label` (was nach außen sichtbar ist)

---

## Was bedeutet "anonym"?

Anonym bedeutet: der Splitter trägt keine menschliche Herkunft nach außen.

Was nach außen sichtbar ist: "aus anonymer menschlicher Quelle" oder nichts.

**Intern bleibt Provenienz erhalten.** Die `internal_origin_ref` und der Link in `human_material_to_splitter` bleiben immer bestehen. Anonymisierung ist keine Herkunftslöschung.

Admin sieht immer die volle Herkunft.

---

## Was bedeutet "mit Herkunft"?

`origin_visibility = 'named'` + `public_origin_label` gesetzt:

Der Splitter trägt z.B. "aus Daniels Traumtagebuch" oder was auch immer der Mensch als Label erlaubt hat.

---

## Was bedeutet "nur privat wirksam"?

`visibility_layer = 'private'` — der Splitter wird erzeugt, aber:
- Nicht in der öffentlichen KompOase sichtbar
- Nicht in der Suche findbar
- Nur für Admin und den Mensch selbst zugänglich
- Kann trotzdem intern auf Wesenentscheidungen wirken (wenn Wesen-Zugang explizit erlaubt)

---

## Was bedeutet "nur als Splitter"?

`quote_permission = 'erlaubt'` aber `visibility_layer = 'internal'`:
- Transformation in Splitter erlaubt
- Splitter bleibt intern — nicht öffentlich, nicht für alle Wesen

---

## Was bedeutet "nicht verwendbar"?

`quote_permission = 'forbidden'`:
- Kein Splitter
- Kein Wesenkontext
- Kein Zitat
- Nur für den Mensch selbst und Admin

---

## Was ist bei Kalender besonders sensibel?

Kalendereinträge enthalten Metadaten über das Leben eines Menschen: Termine, Orte, Zeiten, Personen.

**Nicht erlaubt:**
- Rohe Kalendereinträge als Splitter: "Daniel hat Dienstag 13:00 Termin X"
- Kalender-Rohdaten in Suche oder Wesenkontext

**Nur erlaubt mit Transformation:**
- Wenn ein Mensch einen Kalender-Eintrag explizit zur Transformation freigibt
- Dann: Transformation zu einem abstrakten Splitter, z.B. "Druck, Taktung, verschobene Ruhe"
- `transformation_note` muss dokumentieren was transformiert wurde

---

## Wie wird Widerruf gedacht?

```
PATCH /api/human-material/{id}/consent
  consent_status: "widerrufen"
```

Bei Widerruf:
- `revoked_at` wird gesetzt
- Neue Splitter aus dieser Quelle: nicht mehr möglich
- Bestehende Splitter: bleiben bestehen (die Welt hat bereits darauf reagiert)
- Admin kann bestehende Splitter manuell deaktivieren

**Widerruf ist keine Löschung der Vergangenheit.** Es ist eine Entscheidung für die Zukunft.

---

## Wie bleiben Suche, KompOase und Wesenkontext rechtekonform?

| Ebene | Was sieht man |
|:------|:-------------|
| Öffentlich | Nur Splitter mit `visibility_layer='public'` und `herkunft_sichtbar=true` |
| Wesen | Nur freigegebene Splitter — nie Rohkalender/Rohtexte |
| Mensch (eigene) | Alle eigenen Quellen, auch private |
| Admin | Vollständige Einsicht inkl. `internal_origin_ref` |

Suche respektiert `visibility_layer`:
- `private` und `internal` tauchen nicht in öffentlicher Suche auf
- `admin_only` nur für Admins
- `public` für alle

---

## Vorhandene Tabellen

| Tabelle | Beschreibung | Status |
|:--------|:-------------|:-------|
| `mw_notizen` | Notizen | vorhanden, hat `zitierbar` + `splitter_erzeugt` |
| `mw_tagebuch` | Tagebuch | vorhanden, hat `zitierbar` + `splitter_erzeugt` |
| `mw_traumtagebuch` | Traumtagebuch | vorhanden |
| `mw_kalender` | Kalender | vorhanden |
| `gedankenblasen` | Gedankenblasen | vorhanden, hat `sichtbarkeit` + `herkunft_sichtbar` |
| `human_material_sources` | Abstraktions-Layer | NEU — 2026-05-31 |
| `human_material_to_splitter` | Splitter-Links | NEU — 2026-05-31 |

**Noch fehlend:**
- Bridge: automatische Promotion von mw_notizen → human_material_sources (erst wenn Mensch zustimmt)
- Suche: human_material als Search-Typ
- Gedankenblasen als human_material_source einordnen (Bridge fehlt)

---

## Gedankenblasen als Menschquelle

Gedankenblasen sind eine besondere Form: öffentlich sichtbar per Default, aber mit `herkunft_sichtbar`-Feld.

Sie können Splitter erzeugen, in KompOase wandern, von Wesen aufgenommen werden.
Die Verbindung zu `human_material_sources` fehlt noch als Bridge.

Konzept: Eine Gedankenblase kann als `human_thought_bubble` in `human_material_sources` eingetragen werden, wenn der Mensch möchte, dass sie explizit als Innenquelle mit Consent-Tracking behandelt wird.

Default: Gedankenblasen sind bereits semi-öffentlich durch ihr `sichtbarkeit`-Feld.
Explizites Consent-Tracking: über `human_material_sources` wenn gewünscht.
