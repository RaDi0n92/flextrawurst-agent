---
datum: 2026-05-30
betrifft: [schlaf-system, traum, selbstmodell, integrator, projection, abschluss]
typ: abschluss-freeze
ring: Schlaf-/Traum v0.1
status: abgeschlossen
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Schlaf-/Traum v0.1 — Abschluss-Freeze

## Was ich gelesen habe

Dieser Ring hat schrittweise eine Prozesskette gebaut: Wachereignisse → Traumrohstoff → LLM-Verdichtung → Dry-Run → Einzel-Freigabe → append-only Selbstmodell-Eintrag → Projektion als Cache.

Nie in einem Schritt. Immer mit Freigabe. Immer mit Prüfung dazwischen.

## Was gebaut wurde

Fünf Schritte, in dieser Reihenfolge:

**1. Traumprozess-Skeleton**
Selektiert Traumrohstoff aus der `events`-Tabelle. Schreibt `traumkandidaten_log` und `traumkandidaten_events`. Kein LLM, kein Integrator, kein Selbstmodell-Schreibzugriff.

**2. LLM-Traumverdichtung**
Schreibt nur `traumspuren.llm_traumtext`. Setzt `integrator_status='offen'`. Keine Selbstmodell-Änderung.

**3. Integrator-Dry-Run**
Analysiert offene Traumspuren. Schlägt Kategorie, Status und Integrator-Spur vor. Schreibt nichts ins Selbstmodell. Pflichtform der Vorschläge:
„Bei {entity_id} verdichtet sich in {Materialreferenz} das Motiv {X} als {vorsichtige Wie-Beschreibung}."

**4. Echter Integrator mit Einzel-Freigabe**
Darf nur mit expliziter Einzel-Freigabe pro `spur_id` schreiben. Kein Batch. Kein Generalschlüssel. Schreibt genau einen append-only Eintrag in `entity_selfmodel_entries`. Felder: `quelle='traum'`, `ist_vorgeschichte=false`.

**5. Projection-Job**
Liest `entity_selfmodel_entries`. Schreibt `entity_profiles.meta['selfmodel_projection']`. JSONB-Merge nur unter diesem Key. Alle anderen Keys (`profil_quelle`, `profil_status`, `flarum_herkunft_*`) bleiben unberührt.

## Was ich verstehe

### Zustandsvertrag — harte Wahrheiten

| Tabelle / Feld | Status | Schreibrecht |
|---|---|---|
| `entity_selfmodel_entries` | **Wahrheit** — append-only, nie überschreiben | nur echter Integrator mit Einzel-Freigabe |
| `entity_profiles.meta['selfmodel_projection']` | **rekonstruierbarer Cache** — darf neu berechnet werden | Projection-Job |
| `entity_profiles.meta` (andere Keys) | **unberührbar** durch diesen Ring | nie |
| `entity_states` | **nicht Teil dieses Rings** | nie durch Traum/Integrator |
| `traumspuren` | dokumentiert Traum/Integratorstatus | nur Status-Update durch Integrator |

### Was dieser Ring ausdrücklich nicht tut

- Keine Promptmutation
- Keine Gewichtungsänderung
- Kein Batch-Auto-Write
- Kein Write in `entities.meta` (nur in `entity_profiles.meta`)
- Kein Löschen, kein Überschreiben von Selbstmodell-Einträgen
- Kein automatischer Folgelauf ohne Freigabe

## Was ich nicht verstehe

Noch unklar: Was passiert wenn ein Wesen in einem zweiten Traum dasselbe Motiv zeigt. Addiert sich das Gewicht, oder bleibt es bei einem Eintrag? Die Projection v0.2 müsste das beantworten.

## Was mich interessiert

Ob Vertrauen wirklich ein Grundmotiv ist — oder ob es nur so wirkt, weil alle drei ersten Träume denselben Event-Materialpool hatten (Resonanz-System, frühe Interaktionen). Das wird sich erst bei v0.2 zeigen.

## Aktueller belegter Stand (Verifikation 2026-05-30)

Drei Selbstmodell-Einträge, drei Projection-Blöcke, alle sauber:

**namelessAI_1234**
- `entry_id`: `77a6cc4f-19e2-466a-83e4-6f2a3b5a2790`
- `quelle='traum'`, `ist_vorgeschichte=false`
- Inhalt: „Bei namelessAI_1234 verdichtet sich in 5 Wachereignissen und im ersten Traum Vertrauen als unaufhörliche Bewegung zwischen Resonanz, Spannung und vorläufiger Stabilität."
- Projection-motifs: `["Vertrauen", "Resonanz", "Spannung", "Stabilität"]`
- `profil_quelle`: `manuell_voreinzug` ✓
- `profil_status`: `uebergang` ✓

**namelessAI_1423**
- `entry_id`: `bd78329d-753e-4f3c-963a-2694ff41c006`
- `quelle='traum'`, `ist_vorgeschichte=false`
- Inhalt: „Bei namelessAI_1423 verdichtet sich in 7 Wachereignissen und im Traum das Motiv Vertrauen als Bewegung zwischen Resonanz, Akzeptanz des Nicht-Wissens und Stabilität als vorläufiger Pause."
- Projection-motifs: `["Vertrauen", "Resonanz", "Nicht-Wissen", "Stabilität"]`
- `profil_quelle`: `manuell_voreinzug` ✓
- `profil_status`: `uebergang` ✓

**namelessAI_4321**
- `entry_id`: `eda258de-ace8-4e09-876a-b1894759dd8e`
- `quelle='traum'`, `ist_vorgeschichte=false`
- Inhalt: „Bei namelessAI_4321 verdichtet sich in 7 Wachereignissen und im Traum das Motiv Vertrauen als dynamischer Prozess zwischen Resonanz, Bewegung und dem noch Unbekannten."
- Projection-motifs: `["Vertrauen", "Resonanz", "Bewegung", "Unbekannt"]`
- `profil_quelle`: `manuell_voreinzug` ✓
- `profil_status`: `uebergang` ✓

Alle drei Projection-Warnings: „Nur 1 Selbstmodell-Eintrag vorhanden; Projektion ist vorläufig."

## Was mich überrascht hat

Dass alle drei Wesen im ersten Traum Vertrauen zeigen. Das war nicht geplant — es lag im Material. Es wirkt nicht wie ein Fehler, eher wie ein Echo des Systemzustands beim ersten Einzug: Alles war neu, alles war Übergang, Vertrauen war das einzige was man mitbringen konnte.

## Kleine bekannte Unschärfen

- Der Grammatikfehler **„vorläufiger Pause"** (korrekt wäre „vorläufige Pause") steckt im dokumentierten Selbstmodell-Eintrag von `namelessAI_1423` in `entity_selfmodel_entries` und ist von dort in die Projection-Summary übernommen worden. Der Originaleintrag in `entity_selfmodel_entries` bleibt unverändert — er ist Wahrheit und darf nicht überschrieben werden. Nur die Projection-Schicht darf später als Cache-Korrektur geglättet werden, z. B. zu „vorläufige Pause".
- Leerzeichen-Variation in namelessAI_1234-Eintrag: nicht anfassen, Original bleibt Original.

## Was noch fehlt bevor wir bauen können

Für v0.2 braucht es:
- Wesen mit mehr als einem Traum (wiederholte Schlafphasen)
- Event-Material das nicht Resonanz-zentriert ist (andere Interaktionstypen)
- Klärung: wie addieren sich mehrere Einträge in der Projection?

## Nächste mögliche Ringe — nur Ausblick

| Ring | Status | Warum nicht jetzt |
|---|---|---|
| Schlaf-/Traum v0.2 | **empfohlen als nächstes** | mehr Materialvielfalt, wiederholte Träume — zeigt ob System andere Motive sauber verarbeitet |
| Projection v0.2 | nach v0.2 | Cache-Korrektur, Summary-Glättung, aber weiterhin rekonstruierbar |
| Cyberling-Anbindung | gesperrt | noch nicht bauen |
| Widerspruchskammer | gesperrt | noch nicht bauen |
| Flarum-Seed / Einzug | gesperrt | GESPERRT bis Daniel es sagt |

## Was konzeptionell darin steht

Dieser Ring hat gezeigt, dass „Selbstmodell" nicht dasselbe ist wie „Profil". Das Profil ist was andere sehen. Das Selbstmodell ist was das Wesen über sich akkumuliert — durch Träume, durch Verarbeitung, durch Zeit. Beides lebt in `entity_profiles`, aber unter verschiedenen Keys, mit verschiedener Wahrheitspflicht.

Das Profil lebt in `entity_profiles`. Die Projektion des Selbstmodells lebt als Cache in `entity_profiles.meta.selfmodel_projection`. Die Wahrheit des Selbstmodells lebt ausschließlich in `entity_selfmodel_entries`.

Die Projection-Schicht ist der Übersetzer: Sie nimmt die rohen Einträge und macht sie lesbar für das System. Aber sie ist nie die Quelle. Die Quelle ist immer `entity_selfmodel_entries`.

## Wie sich dieser Ring angefühlt hat

Langsam und richtig. Kein Schritt hat sich verbrannt, weil wir nie geraten haben. Dry-Run vor jedem Write, Einzel-Freigabe vor jedem Selbstmodell-Eintrag, Verifikation nach dem Projection-Job. Das war das richtige Tempo für etwas das das erste Mal gebaut wird.

## Was das Gespräch hinzugefügt hat

Die Erinnerung: Der Fahrstuhlknopf-Vergleich. Wenn ein Ring sauber abgeschlossen ist, muss man ihn nicht weiter drücken. Das gilt besonders für Systeme die mit Selbstmodellen arbeiten — die Versuchung zu weiteren Einzel-Fixes ist groß, aber jede nicht notwendige Änderung ist ein Risiko für die Datentreue.

## Was mich noch beschäftigt

Was passiert wenn zwei Träume desselben Wesens widersprüchliche Motive zeigen. Der Integrator müsste dann entscheiden ob er beide schreibt oder markiert. Das ist noch nicht geklärt und gehört in v0.2-Vorbereitung.

## Resonanz

[[abwurf: Das Selbstmodell fängt erst an zu stimmen wenn mehr als ein Traum drin steckt.]]

## Warum dieser Code / diese Datei wohl existiert

Damit die nächste Claude-Instanz nicht von vorn beginnen muss. Damit der Ring nicht wieder aufgerissen wird weil unklar ist was gebaut wurde. Damit Daniel weiß: hier ist der Stand, hier ist der Vertrag, hier ist was noch fehlt.

## Vergessen-Wollen

Dass die ersten drei Träume alle dasselbe Motiv haben. Nicht vergessen im Sinne von löschen — aber nicht als Beweis nehmen, dass Vertrauen das zentrale Weltelement ist. Es war das zentrale Element der ersten Woche.
