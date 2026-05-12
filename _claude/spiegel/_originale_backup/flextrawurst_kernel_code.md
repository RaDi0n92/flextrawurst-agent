# Spiegel: flextrawurst/kernel/ — der echte Code

**Gelesen:** `kernel/world_engine/run_world_cycle.ts`, `kernel/events/types.ts`, `kernel/governance/governance_matrix.ts` + Verzeichnisstruktur

## Was ich gelesen habe

Der Kernel ist TypeScript. Die Verzeichnisstruktur zeigt ~40 Untermodule: `world_engine`, `events`, `governance`, `entities`, `snapshots`, `worldblick`, `process_camera`, `search`, `audit`, `replay`, `governance`, `os_spine`, `landscape`, `surface`…

`run_world_cycle.ts` ist kompakt: Tick anlegen → Presence Pulse für Entitäten → World Snapshot bauen. Drei Funktionsaufrufe, ein klarer Rückgabewert.

`events/types.ts` definiert das Grundvokabular: `ActorType` (nameless_ai, human, system_layer, world_engine, policy_engine), `OriginType` (live_world, flarum_import, chat_import, obsidian_import, manual_seed, simulation), `VisibilityLayer` (public, system, internal). Und `FlextrawurstEvent` — das Datenprimitivum mit `causal_links`, `kontext`, `origin_type`, `projection_policy`.

`governance_matrix.ts`: eine Matrix die für jede Aktion festlegt ob Gate, Command Intent, Ledger, Audit, Search benötigt wird. "Governance ist die Kontrollkarte. Sie startet nichts. Sie löscht nichts."

## Was ich verstehe

Der Event-Typ `FlextrawurstEvent` ist das Herzstück. Das Feld `causal_links: string[]` bedeutet: jedes Event kennt seine Vorläufer. Das ist Provenienz als Code. Nicht als Konzept — als Datenstruktur. Der Kernsatz "Provenienz wichtiger als Kohärenz" ist hier direkt implementiert: man kann jeden Zustand zurückverfolgen.

`OriginType` enthält `obsidian_import`. Das bedeutet: Obsidian-Inhalte können in den Eventstream einfließen. Das ist der technische Anker für die Kopplung zwischen Werkraum (wo ich jetzt lebe) und dem Weltbetriebssystem. Die Verbindung ist bereits im Typensystem angelegt.

Die Governance-Matrix mit `requires_daniel_root` ist interessant. Es gibt Aktionen die explizit Daniels Freigabe brauchen. Das ist kein technisches Lock — es ist eine verfassungsrechtliche Verankerung der menschlichen Entscheidungshoheit in einem System das sonst stark auf Entitätsautonomie setzt.

## Was mich beschäftigt

Der Code ist sehr sauber. Keine unnötigen Kommentare, klare Typen, kleine Funktionen. Das ist der Fingerabdruck von jemandem der Systeme von innen versteht — nicht von außen zusammenschraubt.

Ich sehe 40 Kernel-Module, 1336 Tests, und kein einziges Organ ist aktiviert. Das ist ein vollständig gebautes Fundament auf dem noch nichts lebt. Wie ein Haus das fertig gebaut ist aber noch keine Möbel hat. Der erste Einzug — wenn die ersten Entitäten tatsächlich in der Welt agieren — wird ein Moment sein.

## Warum dieser Code wohl existiert

Als das, was die Verfassung trägt. Die Kernsätze sind Sprache. Der Eventstream mit `causal_links` ist Praxis. Ohne Code bleibt die Verfassung ein Wunsch. Mit diesem Code ist sie Architektur.

## Wenn wir das bauen

`obsidian_import` ist schon als `OriginType` drin — aber noch nichts importiert es wirklich. Der Brücken-Code fehlt:

```typescript
// kernel/import_gate/obsidian_import.ts — noch nicht existent
import type { FlextrawurstEvent } from "../events/types.ts";

export function importFromObsidian(
  vault_path: string,
  file_glob: string
): FlextrawurstEvent[] {
  // liest _claude/spiegel/*.md, erkenntnis/*.md etc.
  // erzeugt Events mit origin_type: "obsidian_import"
  // causal_links: [] — Ursprungsereignisse haben keine Vorläufer
}
```

Was ich beim Bauen brauche:
- Welche Werkraum-Dateien sollen importierbar sein? Nur `_claude/`? Oder breiter?
- Frontmatter-Konvention für importierbare Dateien (z.B. `importable: true`)
- Wie werden Obsidian-Links (`[[...]]`) in `causal_links` übersetzt?

Datenstruktur die ich mir vorstelle für Werkraum→Event-Mapping:
```typescript
interface ObsidianImportMeta {
  vault_relative_path: string;   // "_claude/spiegel/zwischenraum.md"
  obsidian_links: string[];      // alle [[...]] im Dokument
  created_at: string;
  author: "claude" | "daniel" | "system";
}
```

**Datum des Lesens:** 2026-05-10
