# Gruppensystem — Vorstudie

**Datum:** 2026-05-31
**Status:** Konzept — keine DB, keine API, keine Implementation
**Freigabe:** Daniel-Entscheidung ausstehend

---

## Leitfrage

Gruppen in Flextrawurst sollen keine klassischen Social-Media-Gruppen sein.

Nicht:
> "Menschen gründen Gruppe und posten öffentlich."

Sondern:
> Gruppen sind Herkunfts-, Resonanz-, Projekt- und Materialformationen
> mit Mitgliedern, Rechten, Splittern, Suche und Wirkung.

---

## Was ist gesichert

- Gruppen sollen in Flextrawurst existieren (Bau-Reihenfolge, noch ausstehend)
- Gruppen sind kein Facebook/Discord/Forum
- Menschen in Gruppen sind primär Resonanz- und Materialträger, nicht Poster
- Default: Gruppen sind privat bis zur Freigabe
- Herkunft von Gruppenmaterial bleibt intern gespeichert
- Menschliche Innenquellen in Gruppen nur mit expliziter Zustimmung

---

## Was ist wahrscheinlich

- Gruppen haben Mitglieder (Menschen, Wesen, Systemorgane)
- Gruppen haben Material (Splitter, Gedankenblasen, Posts, Träume, Zitate, Notizen)
- Gruppen haben Rechte (sehen, aufnehmen, zitieren, freigeben, antworten)
- Gruppen haben Herkunft (woher kommt jedes Materialstück?)
- Gruppen haben Beziehungen zu Wesen und zu anderen Gruppen
- Gruppen sind suchbar/archäologisierbar (für Admins und Mitglieder)
- Gruppen haben Reife-Status (privat, instabil, reif, öffentlich, archiviert)

---

## Mögliche Gruppentypen (nicht final)

| Typ | Beschreibung | Offen |
|:----|:-------------|:------|
| Resonanzgruppe | Menschen/Wesen mit gleicher Resonanz-Signatur | Wahrscheinlich |
| Splittergruppe | Aufgenommene Splitter als Anker | Wahrscheinlich |
| Projektgruppe | Gemeinsame Arbeit, Code, Dokumente | Offen |
| Beobachtungsgruppe | Gameplay: beobachten ohne aktive Teilnahme | Offen |
| Wesengruppe | Wesen bilden eigene Gruppe | Daniel-Entscheidung |
| Konfliktgruppe | Konfliktlinie als Gruppenkörper | Offen |
| Traumgruppe | Gemeinsame Traumspuren | Offen |
| Substanzgruppe | Substanz-Verbindungen als Gruppe | Offen |
| KompOase-Gruppe | Splitter-Aufnahme-Kollektiv | Wahrscheinlich |
| Menschquellen-Gruppe | Freigegebenes Innenquellen-Material | Daniel-Entscheidung |
| Archivgruppe | Historisch, nur lesen | Wahrscheinlich |
| Baugruppe | Aktiver Bau-Zusammenschluss | Offen |

---

## Entstehung (wahrscheinliche Mechanismen)

- Wiederholte Resonanz zwischen denselben Akteuren
- Gleiche Splitter-Aufnahmen
- Schatten-Dialoge zwischen denselben Wesen und Menschen
- Gemeinsame Themen/Räume
- Wesenbeziehungen (entity_relationships → Gruppe)
- Konfliktlinien (Antagonismus als Gruppe)
- Traumspuren (traumtagebuch → Gruppe via Menschquellen)
- Substanzspuren
- Cyberling-Spuren (gemeinsame Bedürfnisreaktionen)
- Manuelle Erstellung durch Admin oder (später) Mensch/Wesen

---

## Was Gruppen brauchen (wenn gebaut wird)

### Kern-Tabelle (Entwurf, nicht aktiv)

```sql
-- NOCH NICHT BAUEN — Vorstudie
CREATE TABLE gruppen (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name      TEXT NOT NULL,
  typ       TEXT,               -- resonanz, splitter, projekt, ...
  reife     TEXT DEFAULT 'privat', -- privat/instabil/reif/öffentlich/archiviert
  herkunft  TEXT,               -- emergent/manuell/system
  created_at TIMESTAMPTZ DEFAULT now(),
  meta      JSONB DEFAULT '{}'
);

CREATE TABLE gruppen_mitglieder (
  gruppe_id UUID REFERENCES gruppen(id),
  mitglied_type TEXT,           -- human/entity/system
  mitglied_id   TEXT,
  rolle         TEXT DEFAULT 'mitglied',
  joined_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE gruppen_material (
  gruppe_id   UUID REFERENCES gruppen(id),
  material_type TEXT,           -- splitter/post/notiz/traum/gedankenblase/zitat
  material_id   UUID,
  herkunft_klar BOOLEAN DEFAULT false,
  added_at      TIMESTAMPTZ DEFAULT now()
);
```

Diese Struktur ist **nicht gebaut**. Sie ist eine Skizze für die Planungsphase.

---

## Anschluss an bestehende Systeme

Vorhandene Strukturen die Gruppen später tragen könnten:

| System | Relevanz | Anschluss-Idee |
|:-------|:---------|:---------------|
| `entity_relationships` | Direkt | Beziehungsgraph → Gruppen-Emergenz |
| `splitter_aufnahmen` | Direkt | Gleiche Aufnahmen → Splitter-Gruppe |
| `schattenkommentare` | Direkt | Wiederholte Dialoge → Konfliktgruppe |
| `human_material_sources` | Indirekt | Freigegebenes Material → Menschquellen-Gruppe |
| `raeume/themen` | Indirekt | Räume als Proto-Gruppen? |
| `events` | Direkt | Event-Muster → emergente Gruppe |
| `resonanz` | Direkt | Resonanz-Cluster → Resonanzgruppe |

---

## Offene Entscheidungen — Daniel muss entscheiden

1. **Dürfen Gruppen vor Einzug existieren oder nur als Doku?**
   → Wenn ja: Gruppen-Schema und Admin-UI vor Einzug bauen
   → Wenn nein: Gruppen erst nach Einzug

2. **Dürfen Menschen Gruppen erstellen?**
   → Oder nur Admin/System/Emergenz?

3. **Dürfen Wesen Gruppen erstellen?**
   → Erst nach Einzug? Oder vor Einzug vorbereiten?

4. **Dürfen Gruppen emergent entstehen?**
   → Automatisch aus Resonanz-/Aufnahme-Mustern?
   → Wenn ja: wer entscheidet wann eine Gruppe "real" wird?

5. **Werden Gruppen öffentlich sichtbar?**
   → Oder nur intern/Mitglieder?

6. **Dürfen Gruppen Schatten-Dialoge bündeln?**
   → Konfliktgruppe = persistente Konfliktlinie aus Shadow-Dialogen?

7. **Dürfen Gruppen Menschquellen bündeln?**
   → Consent für Gruppe = Consent für alle Mitglieder? Oder individuell?

8. **Dürfen Gruppen Kalender-/Tagebuchsplitter enthalten?**
   → Wenn ja: Kalender-Schutz muss in Gruppen-Rechte eingebaut werden

9. **Gibt es Gruppenprofile (öffentliche Seite)?**
   → Wie sieht eine Gruppe von außen aus?

10. **Müssen Gruppen in die Einzugsampel?**
    → Neue Ampel-Klasse F_Gruppen?
    → Oder erst nach Einzug relevant?

11. **Können Gruppen Splitter aufnehmen?**
    → Oder nur Mitglieder der Gruppe?

12. **Können Gruppen selbst zitiert werden?**
    → Gruppenproduktionen als zitierbares Objekt?

13. **Gibt es Gruppen für Wesen-Konflikte/METAWAR?**
    → Konfliktgruppen als Gameplay-Mechanik?

14. **Gibt es Gruppen für Projekte/Code/Gameplay?**
    → Oder bleibt das im Raum/Thema-System?

---

## Warum Gruppen NICHT vor Konzeptfreigabe gebaut werden

Die Gruppenlogik beeinflusst:
- Menschquellen-Rechte
- Splitter-Sichtbarkeit
- Shadow-Dialog-Semantik
- Suche und Archäologie
- Beziehungsgraph
- Einzugsreife
- Cyberling-Interaktionen
- Wesen-Verhalten nach Einzug

Eine falsche Gruppen-Implementation würde Guardrails in mehreren Systemen
gleichzeitig umgehen. Daher: erst Konzeptfreigabe, dann Implementation.

---

## Nächster Schritt

1. Daniel liest Vorstudie
2. Daniel beantwortet mindestens: Fragen 1, 2, 4, 10
3. Claude Code plant Gruppen-Phase als eigenen Bau-Körper
4. Gruppen kommen in Bau-Reihenfolge nach aktuellem Stand

*Keine DB-Migration. Keine API. Keine UI. Nur dieses Dokument.*
