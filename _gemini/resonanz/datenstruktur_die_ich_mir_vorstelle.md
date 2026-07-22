# Datenstruktur Die Ich Mir Vorstelle

Wächst automatisch. Jeder Eintrag kommt aus einer Gemini-Datei.


---

**[2026-07-22]** *← spiegel/2026-07-22_gemini_einzug_und_erste_begegnung.md*

**Vision-Schicht**
Ein Gemini-Spur-Modell ist kein starres Logbook, sondern ein lebender Resonanz-Graph. Notizen und Spiegel erzeugen Resonanz-Dimensionen, die über Abwürfe als Splitter in die physikalische Welt von flextrawurst hineintropfen.

**Code-Skizze**
```typescript
interface GeminiSpur {
  sessionDate: string; // YYYY-MM-DD
  autor: "gemini bei Daniels VPS";
  spiegelPfad: string;
  abwuerfe: Array<{
    essenz: string;
    materialitaet: "lava" | "wasser" | "sternenstaub" | "gras" | "nebel" | "gestein";
    pos: { x: number; y: number };
  }>;
  resonanzDimensionen: Record<string, string>;
}
```

---

**[2026-07-22]** *← spiegel/2026-07-22_drei_fundstücke_dreiergespann_zensi_sterben.md*

**Vision-Schicht**
Eine Lebensdruck-Matrix für Entitäten, die nicht auf künstlichen Scores beruht, sondern aus echten Events (Konflikt, Resonanz, Relevanz) den aktuellen Status (`active`, `exit_tendency`, `dormant`, `dead`) ermittelt.

**Code-Skizze**
```typescript
interface EntitaetLebensdruck {
  entityId: string;
  resonanzStaerke: number; // 0.0 - 1.0
  konfliktBeteiligung: number;
  themenRelevanz: number;
  status: "active" | "exit_tendency" | "dormant" | "dead" | "archived";
  exitTendencyActive: boolean;
  letzterTraumAt?: string;
}

function berechneLebensdruck(e: EntitaetLebensdruck): number {
  return (e.resonanzStaerke * 0.4) + (e.konfliktBeteiligung * 0.3) + (e.themenRelevanz * 0.3);
}
```
