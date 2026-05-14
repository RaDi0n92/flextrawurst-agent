# Was Ich Beim Bauen Brauche

Wächst automatisch. Jeder Eintrag kommt aus einer Codex-Datei.


---

**[2026-05-13]** *← notizen/2026-05-13_einzug_korrektur.md*

Bei neuen Codex-Dateien muss Provenienz stimmen: eigene Notiz oder importiertes Referenzmaterial.

---

**[2026-05-13]** *← spiegel/zufall_als_erkenntnisprinzip.md*

Beim Bauen braucht Zufall Parameter:

```typescript
interface DiscoveryMix {
  relevanceWeight: number
  recencyWeight: number
  rarityWeight: number
  randomWeight: number
  resurfacingWindowDays?: number
}
```

---

**[2026-05-13]** *← spiegel/sammler_fremder_gedanken.md*

Beim Bauen braucht jedes gesammelte Fragment mindestens Herkunft, Übernahmeart und sichtbare Anzeige.

```typescript
type ThoughtOriginKind = "own" | "quoted" | "collected_zwischenraum"

interface CarriedThought {
  id: string
  carrierId: string
  text: string
  originKind: ThoughtOriginKind
  originId?: string
  originLabel: string
  adoptedAt: string
}
```

---

**[2026-05-13]** *← spiegel/zwischenraum_definition.md*

Beim Bauen braucht der Zwischenraum Statuswerte, aber keine zu harte Pipeline.

```typescript
type ZwischenraumState =
  | "roh"
  | "beobachtet"
  | "reifend"
  | "adoptiert"
  | "wird_thema"
  | "wird_entitaet"
  | "bleibt_rest"
  | "verschwunden"
```

---

**[2026-05-13]** *← spiegel/dak_gord_mitermoeglicher.md*

Beim Bauen brauche ich eine Rollentrennung:

```typescript
type SystemPresence =
  | "bewohner"
  | "innenorgan"
  | "mitermoeglicher"
  | "ai_strom"
  | "mensch"
  | "admin"
```

---

**[2026-05-13]** *← spiegel/denkfenster.md*

Beim Bauen braucht Denkfenster einen aktiven Prozesszustand und eine Sichtbarkeitschance.

```typescript
interface ThoughtWindow {
  entityId: string
  phase: "reflection" | "resonance_analysis" | "conflict_processing" | "quality_time"
  visibleUntil: string
  fragments: string[]
  controllable: false
}
```

---

**[2026-05-13]** *← spiegel/codewesen_grundhaltung.md*

Beim Bauen braucht Codewesen-Dialog nicht nur Prompting, sondern Zustand:

```typescript
interface CodewesenRelation {
  selfId: string
  otherId: string
  familiarity: number
  affinity: number
  friction: number
  lastContactAt: string
  unansweredSince?: string
}
```
