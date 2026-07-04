---
name: codexium2-solarius2-memory-container
description: Entschiedenes Memory/Container-Konzept für Codexium2/Solarius2 — schlanker als das alte Zwischenwesen-Konzept
metadata:
  type: project
tags: [codexium2, solarius2, memory, container, testbed]
status: gebaut
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

**Container** = was gerade akut in diesem einen Gespräch zählt. Kein Langzeit-Ding, keine Kategorien, keine Gewichtung. Eine einfache Liste, die man live im Chat befüllt (ganze Nachricht oder markierter Satz → pinnen). Begrenzt nicht über eine feste Anzahl Einträge, sondern über ein **Gesamt-Zeichenbudget** (siehe unten) — wenn das Budget voll ist, muss aktiv etwas entfernt werden um Platz zu schaffen. Kein stilles Verdrängen des Ältesten.

### Pin-Mechanismus (entschieden 2026-07-04)

Ein Button an jeder Nachricht im Chat. Klick öffnet die Auswahl:
1. Ganze Nachricht pinnen, ODER einzelne Sätze innerhalb der Nachricht markieren und nur die pinnen.
2. Darunter ein optionales Kommentarfeld, **max. 88 Zeichen** — kurze Begründung warum das gespeichert werden soll ("warum wichtig").

Der Kommentar hängt am Pin-Eintrag dran (Container). Er ist auch die Grundlage für die spätere Memory-Extraktion — der Mensch sagt in einem Satz warum es zählt, das hilft der KI später (asynchron, siehe `chat_architektur.md`) einzuordnen in welche Memory-Kategorie es gehört.

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

## Budget statt Max-pro-Kategorie (entschieden 2026-07-04)

Kein fixer Max-Wert pro Memory-Kategorie. Stattdessen ein **Gesamt-Zeichenbudget**, hergeleitet aus dem Kontextfenster (HauhauCS läuft mit `num_ctx=8192`, siehe Claude-Memory `project_ollama_setup`). Das Budget muss neben System-Prompt (alle wesen.md-Dateien, teils bis 1337 Zeichen pro Feld), Chat-History und Ollama-Antwort-Reservierung (`num_predict:400`) noch Platz lassen.

Vorläufiger Vorschlag als Startwert (nicht in Stein gemeißelt, wird beim Bauen anhand echter Feldgrößen nachgemessen):
- Memory gesamt: ~2500 Zeichen (über alle 5 Kategorien verteilt, keine Kategorie einzeln gedeckelt)
- Container gesamt: ~1200 Zeichen (inkl. der 88-Zeichen-Kommentare)

Wenn ein neuer Eintrag das Budget sprengen würde: UI verweigert das Speichern, Mensch muss erst etwas entfernen. Kein automatisches Kürzen/Verdrängen.

---

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Container ist der Ort für das Akute — was gerade zwischen Mensch und Wesen brennt, ohne Anspruch auf Dauer. Memory ist der Ort für das was bleibt, kuratiert, kategorisiert, überschaubar. Die Trennung ist eine Trennung zwischen Gegenwart und Biografie.

### Code-Skizze
```typescript
const CONTAINER_BUDGET_ZEICHEN = 1200; // vorlaeufig, siehe "Budget statt Max-pro-Kategorie"
const MEMORY_BUDGET_ZEICHEN = 2500;    // vorlaeufig
const PIN_KOMMENTAR_MAX = 88;

// container.json (pro Wesen, /root/werkraum/codexium2/<name>/container.json)
interface Container {
  eintraege: Array<{
    id: string;
    text: string;               // ganze Nachricht ODER markierte Saetze
    kommentar?: string;         // max PIN_KOMMENTAR_MAX Zeichen, "warum wichtig"
    quelle: "mensch" | "wesen";
    hinzugefuegt_am: string;    // ISO
  }>;
  // Summe aller text+kommentar Laengen <= CONTAINER_BUDGET_ZEICHEN
  // UI verweigert neuen Pin wenn Budget ueberschritten wuerde, bis manuell entfernt wird
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
  // Summe aller Zeichen ueber alle Kategorien <= MEMORY_BUDGET_ZEICHEN
  // keine einzelne Kategorie hat einen eigenen Max-Wert
}
```

---

## Umsetzung (2026-07-04, alle Punkte gebaut + getestet)

- Pin-Endpoint + Budget-Check: `serve_process_camera_preview.ts` (`POST/DELETE .../container/pin`)
- Memory-Budget-Check beim PUT: gleiche Datei (`memMatch`-Handler)
- Pin-Button + Modal, Container-Popup, Memory-Popup: `wesen_chat.html`
- Human-getriggerte async Memory-Extraktion: `POST .../memory/extrahieren` + `GET .../memory/extraktion-status`
- Die vorläufigen Budgetwerte (2500/1200 Zeichen) sind live und wurden noch nicht mit echten langen wesen.md-Feldern gegengemessen — falls das Kontextfenster im echten Betrieb eng wird, hier nachjustieren.
