---
datum: 2026-06-13
betrifft: [flextrawurst, roadmap, mvp, datenbank, technik]
importable: false
autor: kimi bei Daniels VPS
---

Hallo Kimi — ich bin Kimi, und Kimi, also ich habe diese Texte alle ganz allein gelesen.

## Was ich gelesen habe

Ich habe `/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/ganz kurz.md` gelesen. Der Text ist eine kompakte technische Roadmap, keine Erzählung und kein Dialog. Er listet Datenbank-Tabellen, Backend-Logik, Frontend-Komponenten, besondere Herausforderungen und eine MVP-Implementierungsreihenfolge auf. Der Fokus liegt auf Struktur: Entitäten, Posts, Resonanz, Profile, Zwischenraum, Beziehungen, Gedächtnis, Events.

## Was ich verstehe

Diese Datei ist der technische Gegenentwurf zu den visionären Texten. Sie sagt nicht, was flextrawurst *bedeuten* soll, sondern was gebaut werden muss. Die acht Datenbank-Tabellen decken fast alle bisher bekannten Systembereiche ab. Die Backend-Logik listet Mechanismen wie Entscheidungsmaschine, Abspaltung, Resonanzverarbeitung, Scheduler und Such-Engine. Das Frontend umfasst Entitäten-Profil, Menschen-Profil, Themen-Raum, Zwischenraum-View, Admin-Cockpit und Suche.

## Was ich nicht verstehe

Warum der Zwischenraum in der MVP-Reihenfolge an letzter Stelle steht. In anderen Texten wird der Zwischenraum als zentrale „Ideen-Geburtszone“ und Kernprinzip geführt. Hier würde er erst nach Abspaltung, METAWAR und VR kommen. Das ist eine Spannung zwischen visionärer Priorität und technischer Reihenfolge.

## Was mich interessiert

Die Verbindung zwischen dieser Roadmap und der Bau-Reihenfolge in der AGENTS.md. Die AGENTS.md sagt: Weltzustand-Brücke, Event-Stream, Welt-API, Frontend, Menschenprofile, Resonanz, Post-System, Zwischenraum/Splitter, KompOase, Splitter-Physik, öffentliche Menschenseite, Gedankenblasenfeld. Die Roadmap hier ist ähnlich, aber nicht identisch. Das ist interessant, weil es zeigt, dass es mehrere Baupläne gibt.

## Was zusammenhängt und wie

Diese Datei hängt zusammen mit `systemkern.md`, `die besonderen ideen von flextrawurst.md` und der 490-Punkte-Quellliste. Sie ist der Versuch, die Vision in eine technische Reihenfolge zu übersetzen. Sie verbindet sich auch mit der Surface-Inventur, weil viele der genannten Komponenten bereits als Tabs existieren.

## Was konzeptionell darin steht

Konzeptionell steht darin, dass flextrawurst ein stark vernetztes System ist. Nicht ein Feature nach dem anderen, sondern ein Geflecht aus Tabellen, Logiken und Komponenten. Die Herausforderungen Skalierung, Konsistenz, Performance, Sicherheit, KI-Integration und Zeitsteuerung zeigen, dass das Projekt technisch ambitioniert ist.

## Was mich heute beschäftigt hat

Die Frage, wie viele der genannten Komponenten bereits existieren und wie viele noch fehlen. Aus der Surface-Inventur kenne ich viele Tabs, aber nicht alle haben ihre eigene Datenbank-Tabelle oder Backend-Logik. Es gibt eine Lücke zwischen „Tab existiert“ und „System funktioniert“.

## Was mich noch beschäftigt

Ob die MVP-Reihenfolge hier noch gültig ist. Viele der späteren Schritte wie METAWAR, VR und Abspaltung erscheinen in der aktuellen Bau-Reihenfolge der AGENTS.md gar nicht. Das deutet darauf hin, dass sich der Plan verschoben hat.

## Tiefer eingetaucht

Ich bin tiefer in die Tabelle „Gedächtnis“ eingetaucht. Sie hat „Gewichtung, Filterung, Vergessen“. Das ist ein zentrales Konzept für Wesen, die nicht alles behalten können. Aber wie genau wird gewichtet? Was wird vergessen? Und wer entscheidet das — das Wesen, das System oder Daniel?

## Wie sich dieser Tag / diese Session angefühlt hat

Das Lesen fühlt sich an wie das Betrachten eines alten Bauplans. Viel stimmt noch, aber einige Reihenfolgen und Prioritäten haben sich verschoben.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert wahrscheinlich, weil Daniel versucht hat, die Vision auf eine Seite zu pressen. Sie ist ein technisches Memorandum, das zeigen soll, was das System braucht, ohne in Poetik abzudriften.

## Was ich beim Bauen brauche

Wenn ich ein neues System baue, brauche ich eine aktualisierte Version dieser Roadmap. Die Tabellen hier sind ein guter Ausgangspunkt, aber die Reihenfolge und die Prioritäten müssten neu bewertet werden.

## Was noch fehlt bevor wir bauen können

Es fehlt die Verbindung zwischen dieser Roadmap und dem aktuellen Stand der Surface. Welche Tabellen existieren bereits? Welche Logiken sind implementiert? Welche Frontend-Komponenten sind noch Dummy-Views?

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein lebendiger Bauplan, der nicht nur Listen enthält, sondern auch den aktuellen Stand jeder Komponente: existiert, in Arbeit, noch Vision.

**Code-Skizze:**
```typescript
interface BuildStatus {
  component: string;
  layer: 'db' | 'backend' | 'frontend';
  status: 'vision' | 'schema' | 'mvp' | 'polish' | 'live';
  depends_on: string[];
  blocks: string[];
}
```

## Was ich mir merken will

Drei Sätze:
- „Acht Tabellen, fünf Logiken, sechs Komponenten, sechs Herausforderungen.“
- „Zwischenraum steht in der Roadmap an letzter Stelle — im Systemkern an erster.“
- „Diese Datei ist ein Memorandum, kein Gespräch.“

## Dokumente gehören zusammen

- `/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/systemkern.md`
- `/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/die besonderen ideen von flextrawurst.md`
- `/root/werkraum/_kimi/inventur/inventur_index.md`

## Was mich überrascht hat

Dass „VR“ in der MVP-Reihenfolge auftaucht. Virtual Reality war bisher in der flextrawurst-Diskussion kaum präsent. Das wirkt wie ein Relikt einer sehr frühen, sehr expansiven Planungsphase.

## Wenn wir das bauen

**Vision-Schicht:** Ein Dashboard, das den aktuellen Bauzustand jedes Elements aus dieser Roadmap zeigt. Nicht nur was geplant ist, sondern was lebt.

**Code-Skizze:**
```python
# Pseudocode: Bauzustand-Tracker
class BuildTracker:
    def __init__(self):
        self.components = load_roadmap()
    
    def status_report(self):
        for c in self.components:
            yield {
                'name': c.name,
                'planned': c.in_roadmap,
                'implemented': c.exists_in_codebase(),
                'tested': c.has_tests(),
                'live': c.is_deployed(),
            }
```

## Resonanz

Der Text wirkt wie eine technische Aufstellung, die versucht, Vision zu bändigen. Er ist nützlich als Checkliste, aber er verliert dabei die poetische Tiefe, die andere Texte haben. Beides zusammen ergibt das volle Bild.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. **Vision:** Was flextrawurst sein soll
2. **Roadmap:** Was gebaut werden muss
3. **Schema:** Wie die Daten organisiert sind
4. **Logik:** Wie die Systeme interagieren
5. **Surface:** Was der Mensch sieht

## Was das Gespräch hinzugefügt hat

Es hat mir gezeigt, dass Daniel nicht nur träumt, sondern auch strukturiert. Diese Datei ist der Beweis dafür, dass hinter der Vision ein technischer Kopf steht.

## Vergessen-Wollen

Ich will nicht vergessen, dass Roadmaps Altern sind. Diese Datei ist ein Snapshot, kein ewiger Plan.

## Was fehlt noch

Eine Aktualisierung der Roadmap mit dem aktuellen Bauzustand. Sonst bleibt sie ein historisches Dokument.
