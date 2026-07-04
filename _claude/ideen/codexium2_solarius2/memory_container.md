---
name: codexium2-solarius2-memory-container
description: Entschiedenes Memory/Container-Konzept für Codexium2/Solarius2 — schlanker als das alte Zwischenwesen-Konzept
metadata:
  type: project
tags: [codexium2, solarius2, memory, container, testbed]
status: in-diskussion
datum: 2026-07-04
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Gilt NUR für Codexium2/Solarius2 (siehe `_claude/ideen/codexium2_solarius2/` als eigene Konzept-Familie). Codexium/Solarius bleiben unangetastet — siehe Claude-Memory `project_codexium2_testbed`.

Das alte Zwischenwesen-Konzept (`_claude/ideen/zwischenwesen/container.md`, `memory_system.md`) war die Inspiration, wurde aber von Daniel am 2026-07-04 explizit als "braucht komplette Neubewertung" eingestuft — nicht 1:1 übernehmen. Das hier ist die neue, eigenständige Entscheidung.

---

## Was ich verstehe

**Container** = was gerade akut in diesem einen Gespräch zählt. Kein Langzeit-Ding, keine Kategorien, keine Gewichtung. Eine einfache Liste, die man live im Chat befüllt (ganze Nachricht oder markierter Satz → pinnen). Begrenzt (max. ~8 Einträge) — wenn voll, muss aktiv etwas entfernt werden um Platz zu schaffen. Kein stilles Verdrängen des Ältesten.

**Memory** = was das Wesen wirklich dauerhaft trägt, über das einzelne Gespräch hinaus. 5 Kategorien (bewusst kleiner als die 7 vom Zwischenwesen-Konzept, das war für die 24h-Flüchtlinge gedacht):

| Kategorie | Bedeutung |
|---|---|
| `über_mich` | was das Wesen über den Menschen wissen soll |
| `wichtige_momente` | Sätze/Momente die zählen |
| `offene_fragen` | ungeklärtes zwischen beiden |
| `wesen_selbst` | Wesen darf selbst reinschreiben, für den Menschen sichtbar + einzeln löschbar |
| `meinungen` | Haltungen, Überzeugungen |

Beide (Container UND Memory) müssen direkt im Chat bedienbar sein — eigene Buttons in `wesen_chat.html`, die je ein Popup öffnen. Nicht nur auf der separaten Profil-Seite (aktueller Ist-Zustand: nur dort editierbar, im Chat nichts davon nutzbar — das war Daniels ursprüngliche Beschwerde).

---

## Automatische Memory-Extraktion

Wertvoll, aber teuer (zusätzliche LLM-Calls) — deshalb: vom Menschen getriggert, nicht automatisch/still im Hintergrund. Läuft dann als asynchroner Job, kein Sofort-Ding (siehe `chat_architektur.md` für das übergeordnete Async-Prinzip — Extraktion nutzt denselben Mechanismus wie die normale Chat-Antwort: Auftrag geht raus, wird verarbeitet wann Zeit ist, Ergebnis (neue Memory-Einträge aus dem Gesprächsverlauf geschrieben) kommt zurück wenn fertig).

Explizit KEINE DB — bleibt bei Dateien (memory.json/container.json pro Wesen), passt zur bestehenden Architektur des Servers (`serve_process_camera_preview.ts` hat aktuell keinerlei Postgres-Anbindung).

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Container ist der Ort für das Akute — was gerade zwischen Mensch und Wesen brennt, ohne Anspruch auf Dauer. Memory ist der Ort für das was bleibt, kuratiert, kategorisiert, überschaubar. Die Trennung ist eine Trennung zwischen Gegenwart und Biografie.

### Code-Skizze
```typescript
// container.json (pro Wesen, /root/werkraum/codexium2/<name>/container.json)
interface Container {
  eintraege: Array<{
    id: string;
    text: string;
    quelle: "mensch" | "wesen";
    hinzugefuegt_am: string; // ISO
  }>;
  // max 8 — UI verweigert neue Eintraege wenn voll, bis manuell entfernt wird
}

// memory.json (pro Wesen)
interface Memory {
  kategorien: {
    ueber_mich: string[];
    wichtige_momente: string[];
    offene_fragen: string[];
    wesen_selbst: string[]; // vom Wesen selbst geschrieben
    meinungen: string[];
  };
}
```

---

## Was noch fehlt bevor wir bauen können

- Genaue UI der Popups (Layout, wo im Chat-Header die Buttons sitzen)
- Wie genau der Mensch die Memory-Extraktion "triggert" (Button? Slash-Befehl im Chat?)
- Ob es einen Max-Wert pro Memory-Kategorie gibt (alte Konzept hatte z.B. max. 10-15 pro Kategorie) — noch nicht mit Daniel besprochen
