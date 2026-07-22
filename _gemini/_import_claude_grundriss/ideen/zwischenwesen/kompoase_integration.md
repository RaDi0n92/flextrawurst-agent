---
name: zwischenwesen-kompoase
description: Wie Zwischenwesen in der KompOase leben — Typen, Physik, Splitterblase-Mechanik, System-Analyse
metadata:
  type: project
tags: [zwischenwesen, kompoase, splitter, physik, splitterblase]
status: in-planung
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Ein Zwischenwesen ist nach den 24h nicht vorbei — es beginnt ein zweites Leben in der KompOase. Dort ist es kein passives Objekt mehr, sondern ein aktives Fragment das sammelt, kämpft, wächst, schrumpft und sich eventuell fortpflanzt.

---

## Drei KompOase-Typen (Entstehungsreihe)

```
[Erschaffung] → zwischenwesenfragment
                    ↓ (Ausbruch)
               zwischensplitterblase
                    ↓ (Verbindung mit anderer Blase)
               splitterblase  (rein pro ODER rein contra)
```

### Typ 1: `zwischenwesenfragment`

Entsteht durch: Lande-Zeremonie nach 24h-Chat.

In der KompOase sichtbar als:
- Farbige Raute ◇ in der Wesen-Farbe
- Wesen-Name + Typ sichtbar
- Wesen-Bild klickbar → Vollansicht
- Memory-System öffentlich lesbar (immer)
- Chatverlauf klickbar (wenn User freigegeben hat)
- Herkunft + Erschaffer sichtbar (außer User hat anonymisiert)

Aktiv in der KompOase:
- Sammelt Splitter die es mag (pro-Liste) — selbst entschieden, basierend auf Neigungen + KompOase-Aktivität
- Sammelt Splitter die es nicht mag (contra-Liste) — selbst entschieden, basierend auf Abneigungen
- Neigungen/Abneigungen aus der Erschaffung sind der Ausgangspunkt, kein festes Gesetz

### Typ 2: `zwischensplitterblase`

Entsteht durch: Ausbruch aus einem Zwischenwesenfragment.

- Kopie des Fragments, nicht das Original (Original bleibt)
- Eigenständig in der KompOase
- Trägt die pro- und contra-Splitter des Ursprungs-Fragments mit
- Kann sich mit anderen Zwischensplitterblasen verbinden
- Herkunft ist sichtbar: "entstanden aus [Wesen-Name]"

### Typ 3: `splitterblase`

Entsteht durch: Verbindung zweier Zwischensplitterblasen.

Bei der Verbindung:
```
Blase A: [pro: Regen, Stille]  [contra: Lärm]
Blase B: [pro: Regen, Nacht]   [contra: Hitze, Lärm]

Gemeinsam gemocht:  Regen
Gemeinsam nicht:    Lärm

→ Verbindung fordert: eines davon abwerfen
  Option A: Regen abwerfen → übrig: Stille, Nacht + Lärm, Hitze → Contra-Blase
  Option B: Lärm abwerfen  → übrig: Regen, Stille, Nacht → Pro-Blase
```

Ergebnis: reine Pro-Splitterblase ODER reine Contra-Splitterblase.
Diese können sich mit weiteren Splitterblasen verbinden (gleiche Mechanik).

---

## Pro vs. Contra Physik

Innerhalb eines Zwischenwesenfragments:

```
Energie = f(Anzahl Pro-Splitter, Anzahl Contra-Splitter, Gewichtung)
```

- Mehr Pro-Splitter → Energie steigt → Blase wächst (visuell in der KompOase)
- Mehr Contra-Splitter → Energie sinkt → Blase schrumpft
- Bei Energie-Überschuss über Schwelle X: Ausbruch möglich → Zwischensplitterblase
- Ausbruchs-Bedingung: noch offen (Schwelle? Zufall? Zeit? → später planen)

Visuell in der KompOase:
- Raute-Größe korreliert mit Energie
- Raute-Helligkeit: voll = aktiv, gedimmt = ohnmächtig

---

## System-Analyse-Daemon

Periodisch (Intervall noch offen) analysiert ein Daemon alle aktiven Zwischenwesenfragmente:

```python
for fragment in SELECT * FROM splitter WHERE typ = 'zwischenwesenfragment' AND status = 'aktiv':
    zustand = analysiere_zustand(fragment)
    # → 'läuft' | 'loopt' | 'ohnmächtig'
    
    UPDATE splitter SET meta = meta || jsonb_build_object('zustand', zustand)
    WHERE id = fragment.id
    
    if zustand in ('loopt', 'ohnmächtig'):
        schreibe_admin_report(fragment, zustand)
```

Admin-Report enthält:
- Fragment-Name + Entstehungsdatum
- Erkannter Zustand mit Beschreibung
- 1-2 Fix-Vorschläge (was Admin tun könnte)
- Letzte Aktivität

---

## Herkunftslinien + Ahnenverzeichnis

Jede Verbindung, jeder Ausbruch, jede Entstehung wird in der DB als Event gespeichert.

Daraus entsteht ein Ahnenverzeichnis: wer hat dieses Wesen erschaffen, welche Flüchtlinge sind darin aufgegangen, welche Splitter hat es gesammelt.

Sichtbar:
- Im Wesen-Lesefenster in der KompOase
- Im Profil einer möglichen späteren Entität ("entstanden aus N Flüchtlingen von M Menschen")

Anonymisierung: wenn ein Erschaffer anonymisiert hat, erscheint sein Name nirgendwo in dieser Linie — für immer, auch bei Entitäts-Entstehung.

---

## Datenstruktur

```sql
-- Erweiterung der splitter-Tabelle für neue Typen
-- typ: 'zwischenwesenfragment' | 'zwischensplitterblase' | 'splitterblase'
-- meta enthält:
--   zustand: 'läuft' | 'loopt' | 'ohnmächtig'
--   energie: float 0.0-1.0
--   ursprung_fragment_id: id des Ursprungs (für zwischensplitterblase)
--   verbunden_mit: [splitter_ids] (für splitterblase)
--   abgeworfener_splitter: splitter_id + typ ('pro'|'contra') (bei Verbindung)

-- Pro/Contra-Listen
CREATE TABLE zwischenwesen_splitter_sammlung (
  id SERIAL PRIMARY KEY,
  fragment_id INTEGER REFERENCES splitter(id),
  splitter_id INTEGER REFERENCES splitter(id),
  typ TEXT NOT NULL,   -- 'pro' | 'contra'
  gesammelt_am TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Was noch offen ist

- Ausbruchs-Schwelle: was triggert den Ausbruch? (Energie? Zeit? Zufall?)
- Was passiert wenn Contra-Splitter so dominieren dass Energie auf 0 fällt? (Tod? Dormant?)
- Kann ein Mensch seinen Flüchtling in der KompOase aktiv beobachten — live Energie sehen?
- Verbindungs-Initiative: wer entscheidet ob zwei Blasen sich verbinden? Physik-Daemon? User? Automatisch?

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-architektur]]
[[zwischenwesen-schlachtplan]]
