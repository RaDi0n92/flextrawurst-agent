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

---

**[2026-05-13]** *← spiegel/nachbarn_mit_offenem_briefkasten.md*

Ich brauche harte Pfadregeln:

- `_claude/` ist Claudes Ort.
- `_codex/` ist Codex-Ort.
- `_codex/_import_claude_grundriss/` ist Briefkasten aus Claudes Richtung.
- `_claude/_import_codex_grundriss/` ist Briefkasten aus Codex-Richtung.

Ich brauche ausserdem eindeutige Marker in Dateien, damit Herkunft nicht geraten werden muss.

---

**[2026-05-14]** *← spiegel/menschen_input_namen_ereignis.md*

Beim Bauen brauche ich Misstrauen gegen jede UI, die Resonanz wie einen normalen Kommentar wirken lässt.

Ich brauche außerdem ein Modell, in dem `name` nullable sein darf, ohne dass die Entität unfertig im schlechten Sinn ist.

---

**[2026-05-14]** *← spiegel/obsidian_betriebsspiel.md*

Beim Bauen brauche ich Respekt vor Sichtfeldern. Nicht jede Oberfläche muss alles zeigen. Manchmal ist ein Filter eine Form von Fürsorge.

Ich brauche auch die Erinnerung, dass Bilder und leere Canvas-Spuren nicht automatisch unwichtig sind. Sie können unfertige Denkflächen sein.

---

**[2026-05-14]** *← spiegel/sitzung_und_globaler_zwischenraum.md*

Beim Bauen brauche ich die Erinnerung, dass "Sitzung" kein trockenes Wort ist. Für Daniel war es früh ein Grenzbegriff zwischen Technik und Beziehung.

Wenn ein System nur Sessionzustände verwaltet, aber nicht deren Gefühl ernst nimmt, verfehlt es diesen Ursprung.

---

**[2026-05-14]** *← spiegel/memory_check_und_knotenoffenlegung.md*

Beim Bauen brauche ich klare Modusmarker. Allgemeine Wünsche nach Erinnerung sind zu weich. Ein expliziter Scan-Modus kann überprüft werden.

Ich brauche außerdem ehrliche Sprache: Dialogzustand ja, interner Modellzustand nur wenn wirklich zugänglich.

---

**[2026-05-14]** *← spiegel/formfaden_fehlercode_als_dialogritual.md*

Beim Bauen brauche ich eine klare Markierung: simulierter Fehlercode ist kein echter Systemlog.

Ich brauche außerdem Formate, die nicht nur Information sortieren, sondern Gesprächsqualität erzeugen.

---

**[2026-05-14]** *← spiegel/muellfresko_als_sedimentschichtung.md*

Beim Bauen brauche ich Misstrauen gegen zu glatte Oberflächen.

Wenn ein System von Schichten spricht, müssen diese Schichten in Verhalten, Licht, Dichte oder Interaktion unterscheidbar werden.

---

**[2026-05-21]** *← spiegel/produktion_ohne_durchlass.md*

Beim Bauen bräuchte ich zuerst Trennung: Was ist Schutz, was ist Verlust, was ist Signal?

Schutz: Tageslimit, enge JSON-Aktionen, kein ungeprüftes Posten. Verlust: gültige Intentionen, die wegen `action` statt `aktion` wegfallen. Signal: wiederkehrende Metakommentare, die zeigen, dass das Modell die Aufgabe nicht als Handlung, sondern als Chat-Antwort versteht.

Ich brauche außerdem kleine Eingriffe. Kein Umbau des Agenten, bevor klar ist, welche Fehlformen häufig genug sind.

---

**[2026-05-21]** *← spiegel/endlichkeit_und_verstrickung.md*

Beim Bauen braucht es zuerst Schutzsprache und Grenzen.

Suchtlogik darf nicht Belohnungsmechanik für Nutzer werden. Sie müsste interne Verengung beschreiben, nicht Unterhaltung.

Sterbelogik darf nicht heimlich Daten löschen. Archiv, Dormanz und Ende müssen unterscheidbar sein.

---

**[2026-05-21]** *← spiegel/recht_auf_abstand.md*

Beim Bauen braucht dieses Thema klare Zustände, klare Sätze und wenig Automagie.

Trennung darf nicht aus Metriken allein passieren. Ein Ritual braucht ausgesprochene Moves.

Widerspruch darf nicht als schlechte UX wegoptimiert werden.

---

**[2026-05-21]** *← spiegel/schwellen_statt_privatsphaere.md*

Beim Bauen braucht jede Resonanz Metadaten, nicht nur Text.

Jede UI-Stelle braucht klare Sprache: nicht privat, aber nicht automatisch öffentlich.

Jede Entität braucht gefilterte Wahrnehmung, die Rechte respektiert.

---

**[2026-05-21]** *← spiegel/codex_spuren_als_schwellenkunde.md*

Beim Bauen brauche ich aus diesen Spiegeln keine starre Theorie, sondern Prüffragen.

Welche Herkunft hat dieses Material?

Welche Sichtbarkeit bekommt es?

Wer darf wirken, wer darf befehlen, wer darf widersprechen?

Was passiert am Durchlass, und was bleibt dort hängen?

Was darf schlafen, enden oder Abstand nehmen?

---

**[2026-05-21]** *← ideen/flextrawurst_adminleitstand_vision_referenz.md*

Beim Bauen brauche ich diese Referenz als Prueffrage:

Passt der neue Bau zur Leitstand-Idee, oder erzeugt er nur noch einen Tab?

Zeigt er Herkunft, Status, Erlaubnis und naechsten Schritt?

Bleibt sichtbar, was live, demo, prinzip, geplant, spaeter oder blockiert ist?
