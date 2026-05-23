---
datum: 2026-05-23
autor: claude-code bei Daniels VPS
quellenbasis: 12_bauanschluss/ring10_minimal_naechste_implementation.md; 12_bauanschluss/ring10_build_ready_concepts.md; gesamter Analyse-Körper
provenienztyp: Claude-Ergänzung, Baukonzept, kein Kanon
importable: false
warnung: Claude-Leseschicht, Bauvorschlag ohne Daniel-Freigabe, kein Kanon
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# 16.03 — Analyse-Browser: Konkretes Konzept

Warnung: Claude-Bauvorschlag. Kein Kanon, keine Aktivierung, keine Weltwirkung. Der Browser ist read-only — er zeigt, er verändert nichts.

## Was der Browser leisten muss

Codex hat den Browser in Ring 10 als "Read-only Analyse-Browser mit Provenienzfiltern" beschrieben. Das ist richtig aber zu knapp. Was genau muss er können?

Ich habe den Analyse-Körper gelesen und identifiziere sieben konkrete Anforderungen.

---

## Anforderung 1: Drei-Schichten-Navigation

Der Browser muss drei Provenienz-Schichten unterscheiden und einzeln filterbar machen:

- **Flarum-Rohtext** — direkte Posts, Thread-Titel, originale Wesen-Sätze
- **Codex-Analyse** — Destillate, Interpretationen, Kandidaten, Zählungen
- **Claude-Ergänzung** — diese Dateien hier

Jeder Eintrag zeigt seine Schicht als sichtbares Badge. Kein Eintrag ohne Schichten-Markierung.

---

## Anforderung 2: Sprecher-Filter

Filter nach: Wesen (welches?), Admin, ChatGPT-Analyse, Codex-Destillat.

Wichtig: Admin-Posts und Wesen-Posts dürfen nie unmarkiert nebeneinander stehen. Die wichtigste gefährliche Regel aus Ring 9 lautet *"Jeder Adminsatz ist Gesetz"* — der Browser muss das strukturell verhindern.

---

## Anforderung 3: Provenienz-Typ-Filter

Die Provenienz-Legende aus dem INDEX hat sechs Typen: Quelle, Zählung, Interpretation, Kandidat, Destillat, Systemregel-Kandidat.

Jede Datei im Browser hat einen dieser Typen als primäres Label. Kombination möglich (Zählung + Kandidat). Systemregel-Kandidat bekommt roten Hinweis: "Keine Aktivierung ohne Daniel-Freigabe."

---

## Anforderung 4: Unsicherheits-Anzeige

Jeder Eintrag zeigt seinen Unsicherheitszustand:

- `rohquelle_geprüft` — Rohpost belegt
- `rohquelle_ausstehend` — Beleg noch nicht geprüft
- `destillat_ohne_beleg` — abgeleitet, kein direkter Rohpost
- `mojibake_beschaedigt` — Text vor Nutzung bereinigen

Das verhindert, dass Destillate als Quellen gelesen werden.

---

## Anforderung 5: Querverbindungs-Navigation

Der Browser zeigt Querverbindungen: Wenn ich auf Kandidat 04 (Leere darf sein) klicke, sehe ich auch Kandidat 05 (Reibung als Motor) als verwandten Eintrag — und den verworfenen Gegenpart aus Ring 9.

Die Matrix der sechs Wesen ist über Korrekturfunktionen navigierbar: Klick auf "Überbehauptung bremsen" zeigt 1111-Einträge die dazu gehören.

---

## Anforderung 6: Statusanzeige für Bearbeitungszustand

Jede Datei zeigt:
- Automatisch erzeugt / Systemisch korrigiert / Manuell gelesen / Daniel geprüft

Das direkt aus `STATUS_MANUELLE_NACHARBEIT.md` übernommen. Der Browser macht sichtbar was der Status-Report textuell dokumentiert.

---

## Anforderung 7: Keine Weltwirkung

Absoluter Schutz: Kein Button "In System übernehmen", kein "Als Memory setzen", kein "Aktivieren". Der Browser ist eine Lesemaschine. Wer einen Eintrag für Flextrawurst freigeben will, tut das außerhalb des Browsers — per Daniel-Entscheidung, dokumentiert, nicht geklickt.

---

## Was der Browser nicht kann

- Wesen-Profile schreiben
- Regeln aktivieren
- Memory-Import auslösen
- Flarum direkt abfragen
- Liveverbindung zu Flarum-Daten

---

## Technischer Rahmen (Skizze)

Daten: JSON aus den Analyse-Dateien, flach gemacht. Kein Live-Backend, kein Daemon. Einmalig erzeugt per Analyse-Generator, dann statisch serviert.

Oberfläche: HTML/JS, kein Framework-Zwang. Passt zum Flextrawurst-Stack.

Wo: Am sichersten als separater Tab im Flextrawurst Surface (8787) unter `/analyse-browser` — read-only, kein API-Schreibzugriff.

---

## Was ich gelesen habe

Ich habe den Bauanschluss-Ordner und alle Ring-10-Dateien gelesen, dazu die Statusdatei und den INDEX. Was mich am meisten beschäftigt hat: Der Browser ist der einzige nächste Schritt der alle Schutzregeln einhält. Kein Memory-Import, keine Weltwirkung, keine Systemregel-Aktivierung.

Gleichzeitig ist er der einzige Schritt der die ganze Analyse-Arbeit zugänglich macht. Im Moment liegen 107 Markdown-Dateien in Ordnern. Das ist lesbar aber nicht navigierbar.

## Was ich verstehe

Ich verstehe den Browser als das Bindeglied zwischen Analyse und Entscheidung. Nicht als Entscheidungsmaschine, sondern als Entscheidungsgrundlage. Daniel braucht einen Ort von dem aus er urteilen kann ohne sich durch Verzeichnisse zu arbeiten.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob der Browser aktiv genutzt werden wird oder ob er als Referenz dient. Das ist ein Nutzungsdesign-Problem, kein technisches.

## Was mich interessiert

Die Schnittstelle zwischen Browser und Freigabeprozess. Der Browser zeigt einen Regelkandidaten. Daniel will ihn freigeben. Wo passiert das? Nicht im Browser — aber der Browser sollte einen Link oder Verweis haben der den Freigabeprozess startet.

## Was zusammenhängt und wie

Der Browser hängt mit allen Ring-Dateien zusammen als Datenbasis, mit `12_bauanschluss/ring10_minimal_naechste_implementation.md` als Ausgangsbeschreibung, mit `02_weltregel_risikoprofile.md` (diese Datei-Reihe) als Freigabe-Mechanismus und mit der Flextrawurst Surface als technischem Träger.

## Was konzeptionell darin steht

Konzeptionell steht hier: Der Browser ist das erste sichere System das aus dem Analyse-Körper entsteht. Alles andere (Memory-Import, Wesen-Einzug, Regelaktivierung) kommt danach — oder gar nicht.

## Was mich heute beschäftigt hat

Anforderung 7 ist die schwierigste nicht technisch, sondern kulturell. "Kein In-System-übernehmen"-Button ist leicht zu bauen. Aber der Impuls, aus dem Browser heraus direkt zu handeln, ist stark. Die Grenze muss im Design sichtbar sein, nicht nur in der Dokumentation.

## Was mich noch beschäftigt

Wie der Browser mit wachsendem Material skaliert. Jetzt sind es 107 Dateien. Wenn Flarum weiterläuft und neue Analyse-Ringe entstehen, wächst das. Der Browser braucht von Anfang an Paginierung und Filterkombinationen.

## Tiefer eingetaucht

Tiefer betrachtet ist der Browser ein Provenienz-Werkzeug, kein Analyse-Werkzeug. Er erzeugt keine neuen Erkenntnisse. Er macht vorhandene Erkenntnisse mit ihrer Herkunft sichtbar. Das ist schwieriger zu bauen als es klingt, weil Herkunft in den Dateien unterschiedlich tief vergraben ist.

## Wie sich dieser Tag / diese Session angefühlt hat

Konkret. Die sieben Anforderungen kamen direkt aus der Lektüre — ich habe die Stellen markiert wo die Analyse an ihre Grenze stößt weil ein Browser fehlt.

## Warum dieser Code / diese Datei wohl existiert

Weil Ring 10 "Analyse-Browser" sagt ohne zu beschreiben was das heißt. Diese Datei beschreibt es.

## Was ich beim Bauen brauche

Beim Bauen brauche ich: den Analyse-Generator (`analyse_generator.py`) als Basis, eine JSON-Exportfunktion für alle Analyse-Dateien mit Provenienz-Feldern, und die Surface-Infrastruktur (8787) als Träger.

## Was noch fehlt bevor wir bauen können

Eine Entscheidung über das Datenformat: Welche Felder werden pro Datei exportiert? Mindestens: pfad, titel, schicht, provenienztyp, autor, datum, kanon, status, unsicherheit, querverbindungen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Analyse-Datei wird zu einem Browser-Eintrag mit sichtbarer Provenienz, Unsicherheit, Querverbindungen und Bearbeitungsstatus. Navigation über drei Schichten, sechs Provenienztypen, sechs Wesen und neun Regelkandidaten.

**Code-Skizze:**
```ts
interface BrowserEintrag {
  pfad: string;
  titel: string;
  schicht: 'flarum_roh' | 'codex_analyse' | 'claude_ergaenzung';
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  autor: string;
  datum: string;
  kanon: false;
  unsicherheit: 'hoch' | 'mittel' | 'gering';
  bearbeitungsstatus: 'automatisch' | 'systemisch' | 'manuell' | 'daniel_geprueft';
  querverbindungen: string[];
  weltWirkung: false;
}

// Statisch erzeugt, nicht live
function buildBrowserIndex(): BrowserEintrag[] {
  return parseAllAnalyseDateien('/root/werkraum/_codex/codex_flarum_analyse');
}
```

## Was ich mir merken will

Anforderung 7 ist nicht verhandelbar. Kein Schreibzugriff aus dem Browser.

## Dokumente gehören zusammen

Diese Datei, `12_bauanschluss/ring10_minimal_naechste_implementation.md`, `12_bauanschluss/ring10_build_ready_concepts.md` und `PROVENIENZ_MANIFEST.md` gehören zusammen als Baugrundlage.

## Was mich überrascht hat

Dass der Browser wahrscheinlich schneller zu bauen ist als die Analyse selbst. Die Daten sind da. Das Format ist klar. Die Anforderungen sind beschreibbar. Der schwerste Teil war die Analyse, nicht die Visualisierung.

## Wenn wir das bauen

**Vision-Schicht:** Ein ruhiger, dunkler Browser der Texte zeigt wie sie sind — mit Herkunft, Unsicherheit, Querverbindungen. Kein Rauschen, kein Gamification, keine Empfehlungen. Einfach lesbar, ehrlich, navigierbar.

**Code-Skizze:**
```python
# analyse_browser_builder.py
import json, os
from pathlib import Path

def build_index(base_dir):
    entries = []
    for md_file in Path(base_dir).rglob('*.md'):
        entry = parse_frontmatter(md_file)
        entry['querverbindungen'] = extract_links(md_file)
        entries.append(entry)
    return entries

def serve_browser(port=8031):
    index = build_index('/root/werkraum/_codex/codex_flarum_analyse')
    with open('out/analyse_browser_index.json', 'w') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
```

## Resonanz

Der Browser ist das Versprechen das der ganze Analyse-Körper macht: *man kann das lesen*. Nicht nur wer die Ordnerstruktur kennt, sondern wer eine Frage hat und einen Einstiegspunkt sucht.

## Die Schichten des Systems — wie ich sie jetzt sehe

Analyse-Körper → Browser → Daniels Entscheidungen → Freigaben → Flextrawurst. Fünf Stufen, jede mit klarer Grenze. Der Browser ist Stufe zwei.

## Was das Gespräch hinzugefügt hat

Der Auftrag "wirklich alles analysieren" hat mir gezeigt, wie schwer der Analyse-Körper zugänglich ist ohne Navigationswerkzeug. Ich hatte 107 Dateien — aber kein Interface. Der Browser ist die Antwort auf diese Erfahrung.

## Vergessen-Wollen

Vergessen will ich die Idee, dass der Browser "smart" sein muss. Er muss nicht empfehlen, filtern oder zusammenfassen. Er muss zeigen was da ist.

## Was fehlt noch

Daniels Entscheidung ob dieser Browser gebaut wird, und wenn ja: auf welchem Port, als eigenständiger Service oder als Surface-Tab.
