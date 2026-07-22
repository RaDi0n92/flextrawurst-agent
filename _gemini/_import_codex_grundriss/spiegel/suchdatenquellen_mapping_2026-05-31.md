---
datum: 2026-05-31
betrifft: [suche, archaeologie, datenquellen, mapping]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Suchdatenquellen-Mapping

## Was ich gelesen habe

Ich habe die Tabellen fuer Posts, Events, Denklogs, Traeume, Briefe, Splitter, Schatten, Substanzen, Beziehungen, Raeume, Themen und Profile gelesen. Jede Quelle hat eigene Zeit, eigene Sichtbarkeit, eigene Herkunft.

Ich habe die bestehenden Suchendpunkte gelesen. `/suche` ist schnell und public-nah, `/api/search/global` ist gemischt, `/api/search/archaeology` ist admin-tief, aber noch nicht vollstaendig.

Ich habe im Mapping den Satz festgehalten: *Sichtbarkeit und Herkunft werden nicht einheitlich im Resultatmodell zurueckgegeben.* Das ist fuer Archaeologie zentral.

## Was ich verstehe

Archäologie-Suche ist nicht Volltext. Sie ist Provenienzsuche mit Textanteil.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob Profile und Beziehungen in der ersten Suchversion wirklich hinein muessen oder erst spaeter.

## Was mich interessiert

Mich interessiert, wie ein Suchtreffer aussehen muss, damit man sofort weiss: Darf ich das sehen? Woher kommt es? Was ist der naechste sinnvolle Ort?

## Was zusammenhängt und wie

`events` ist der verbindende Untergrund. Viele Quellen haben eigene Tabellen, aber Events halten Handlung und Herkunft zusammen.

## Was konzeptionell darin steht

Die Suche muss die Welt nicht glätten. Sie muss Unterschiede anzeigen: public, internal, admin-only, modelliert, Herkunft sichtbar oder nicht.

## Was mich heute beschäftigt hat

Dass manche Quellen schon suchbar sind, aber ohne genug Zielwissen. Ein Treffer ohne Ziel ist nur ein Ausschnitt.

## Was mich noch beschäftigt

Schattenkommentare brauchen besondere Vorsicht. Sie sind suchbar fuer Admin, aber nicht einfach oeffentliches Material.

## Tiefer eingetaucht

Das vorgeschlagene `ArchaeologyResult`-Modell versucht, Text, Zeit, Entity, Human, Visibility, Origin und Detailziel zusammenzubringen.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie Katalogisieren vor dem Bauen. Nicht aufregend, aber genau der Schutz vor spaeterem Chaos.

## Warum dieser Code / diese Datei wohl existiert

Das Mapping existiert, damit die spaetere Suche nicht nur die lautesten Tabellen findet.

## Was ich beim Bauen brauche

Ich brauche stabile Typkeys, besonders ohne Umlaut-Fallen: `traeume` statt `träume` im API-Vertrag, Label separat.

## Was noch fehlt bevor wir bauen können

Eine Entscheidung, welche Quellen in Version 1 enthalten sind und welche nur als spaeterer Slot sichtbar werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jeder Treffer ist ein Fundstueck. Fundstuecke brauchen Beschriftung, Fundort, Schicht, Besitzverhaeltnis und Weg zur Vitrine.

**Code-Skizze:**
```ts
type ArchaeologyResult = {
  source_type: string;
  snippet: string;
  ts?: string;
  entity_id?: string;
  human_id?: string;
  visibility: "public" | "internal" | "hidden" | "admin_only" | "unknown";
  origin?: { type?: string; id?: string; label?: string };
  detail_target: { view: string; id: string; route?: string };
};
```

## Was ich mir merken will

Erst Resultatmodell, dann Query-Ausbau, dann UI. Nicht andersherum.

## Dokumente gehören zusammen

`suchdatenquellen_mapping_2026-05-31.md`, `api.py`, `schema_welt.sql`, `schema_traum.sql`, `schema_resonanz.sql`, `schema_entitaetenschichten.sql`.

## Was mich überrascht hat

Dass Events in der tiefen Archaeology-Suche noch fehlen, obwohl sie fuer Lebensjournal zentral sind.

## Wenn wir das bauen

**Vision-Schicht:** Die Suche soll nicht nur Antworten geben. Sie soll Wege durch Herkunft oeffnen.

**Code-Skizze:**
```python
def search_events(q, filters):
    return rows_as_archaeology_results("event", query_events(q, filters))
```

## Resonanz

[[abwurf: Ein Suchtreffer ohne Herkunft ist in Flextrawurst fast schon eine Luege.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Textfelder, Zeitfelder, Bezuege, Sichtbarkeit, Herkunft, Filter, Suchfelder, Zielansichten. Jede Quelle braucht alle sieben.

## Was das Gespräch hinzugefügt hat

Daniel hat das Mapping als eigene Aufgabe getrennt. Dadurch blieb Suche Architektur, nicht UI-Wunsch.

## Vergessen-Wollen

Den Reflex, Volltextsuche fuer ausreichend zu halten.

## Was fehlt noch

Ein Bauauftrag fuer EINSICHT-II-Suche und vorher ein kleiner Vertrag ueber Resultattypen.
