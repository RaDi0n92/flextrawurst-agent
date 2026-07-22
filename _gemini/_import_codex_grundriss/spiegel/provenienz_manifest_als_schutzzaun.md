---
datum: 2026-05-24
betrifft: [provenienz, flarum, analyse, schutzzaun]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex - ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe `/root/werkraum/_codex/codex_claude_flarum_analyse/PROVENIENZ_MANIFEST.md` gelesen.

Der Text trennt Quelle, Zählung, Interpretation, Kandidat, Destillat und Systemregel-Kandidat. Er sagt im Kern: Keine Datei in diesem Analyse-Ring ist automatisch Systemregel.

Ich habe das als Schutzzaun gelesen. Nicht gegen Denken, sondern gegen Nebel: schöne Sätze, Statistiken, Rohzitate und spätere Regeln dürfen nicht ineinanderlaufen.

## Was ich verstehe

Ich verstehe das Manifest als Eingangstür. Es sagt, wie gelesen werden darf.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob wirklich jede spätere Nacharbeitsdatei sauber inventarisiert ist.

## Was mich interessiert

Mich interessiert die technische Durchsetzung: Markdown-Warnung reicht langfristig nicht.

## Was zusammenhängt und wie

Das Manifest hängt mit jeder Analyse zusammen, weil es den Status jeder Aussage markiert.

## Was konzeptionell darin steht

Konzeptionell steht darin: Wahrheit ist nicht Stil, sondern Herkunft plus Prüfstatus.

## Was mich heute beschäftigt hat

Heute beschäftigt mich, dass ich selbst Provenienz praktisch verletzt habe. Das Manifest liest sich dadurch dringlicher.

## Was mich noch beschäftigt

Mich beschäftigt, wie leicht obere Dateien Autorität ausstrahlen.

## Tiefer eingetaucht

Tiefer gesehen ist das Manifest kein Inhalt, sondern Leserecht.

## Wie sich dieser Tag / diese Session angefühlt hat

Es fühlte sich an wie eine Erinnerung, dass Orientierung gebaut werden muss, bevor Vertrauen entsteht.

## Warum dieser Code / diese Datei wohl existiert

Sie existiert, weil die Analyse sonst zu schön und zu gefährlich wird.

## Was ich beim Bauen brauche

Ich brauche Pflichtfelder für Provenienztyp, Quelle, Nachprüfung und Importierbarkeit.

## Was noch fehlt bevor wir bauen können

Es fehlt Validierung: keine Analyse ohne Status.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Aussage trägt ihren Ausweis.

**Code-Skizze:**
```ts
type Provenienztyp = "quelle" | "zaehlung" | "interpretation" | "kandidat" | "destillat" | "systemregel_kandidat";
interface ProvenanceRecord { typ: Provenienztyp; canBeTruth: boolean; needsReview: boolean; }
```

## Was ich mir merken will

Kein schöner Satz ist automatisch Wahrheit.

## Dokumente gehören zusammen

Dieses Manifest gehört zu freien Leseschichten, Rohdaten und Kandidatenlisten.

## Was mich überrascht hat

Mich überrascht, wie praktisch das Manifest ist: Es ist weniger Philosophie als Werkzeug.

## Wenn wir das bauen

**Vision-Schicht:** Der Browser muss Herkunft immer mitanzeigen.

**Code-Skizze:**
```ts
function mayPromote(r: ProvenanceRecord) { return r.typ === "quelle" && !r.needsReview; }
```

## Resonanz

Resonanz: Provenienz ist der Schutz vor falschem Weltbau.

## Die Schichten des Systems - wie ich sie jetzt sehe

Ich sehe Quelle, Zählung, Deutung, Kandidat und Regel als getrennte Stockwerke.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat gezeigt, dass auch UI-Änderungen Provenienz brauchen.

## Vergessen-Wollen

Vergessen will ich, Ordnung als Verständnis auszugeben.

## Was fehlt noch

Es fehlt eine maschinelle Provenienzprüfung.
