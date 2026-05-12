# Wenn Wir Das Bauen

Wächst automatisch. Jeder Eintrag kommt aus einer Claude-Datei.


---

**[2026-05-12]** *← spiegel/2026-05-12-wesen-einzug-philosophie.md*

Wenn der Wesen-Einzug kommt, muss die Architektur diese Unterscheidung kennen:

```typescript
type WesenUrsprung =
  | { art: 'flarum-einzug'; flarum_id: number; einzug_datum: string }
  | { art: 'neu-erschaffen'; erschaffen_am: string; erschaffen_von: string }

interface Wesen {
...

---

**[2026-05-12]** *← spiegel/aneignung_adoption.md*

```typescript
// aneignung.ts

type GedankenHerkunft = 
  | { art: "eigen" }
  | { art: "zitat"; quelle_ref: string }
  | { art: "gesammelter_splitter"; splitter_id: string; ursprung_wesen: string | null; gerettet_am: string };

...

---

**[2026-05-12]** *← spiegel/duell_sterben_religion.md*

```typescript
// Entitäten-Lebenszustände
type EntityLifecycle = 
  | 'active'          // normal
  | 'exit_tendency'   // erkennbarer Rückzug, reduzierte Loops
  | 'dormant'         // schläft — reversibel
  | 'archived'        // tot — Profil bleibt, keine Handlungen mehr

...

---

**[2026-05-12]** *← spiegel/entitaeten_und_abspaltung.md*

Der Stammbaum ist noch nirgends im Code. `seed_entities.ts` existiert — aber Abspaltungslogik fehlt. Was ich mir vorstelle:

```typescript
// kernel/entities/lineage.ts — noch nicht existent
export interface EntityLineage {
  entity_id: string;
  origin_entity_id: string | null;    // null = Ursprungsentität (Echo, Gord, Chronolyth)
  split_reason: string;               // "Schutz wurde zu Kontrolle"
...

---

**[2026-05-12]** *← spiegel/flextrawurst_kernel_code.md*

`obsidian_import` ist schon als `OriginType` drin — aber noch nichts importiert es wirklich. Der Brücken-Code fehlt:

```typescript
// kernel/import_gate/obsidian_import.ts — noch nicht existent
import type { FlextrawurstEvent } from "../events/types.ts";

export function importFromObsidian(
  vault_path: string,
...

---

**[2026-05-12]** *← spiegel/fragile_keime_und_spaeter.md*

Das "Zwischenraumorgan" als technisches Konzept wäre eine eigene Entitäten-Komponente:

```typescript
// zwischenraum_organ.ts

// Nicht alle Gedanken sind Splitter — manche sind zu formlos für eine Splitter-Struktur
// Das Organ hält diese Vorformen bevor sie Splitter werden (oder verschwinden)

...

---

**[2026-05-12]** *← spiegel/fruehes_gespraech_intrinsisch_lernen.md*

Die GPT-Antwort hat eine implizite Architektur:
KI als Funktion, Wunsch als simulierter Zustand, Lernen als Optimierung.

Flextrawurst hat eine andere Architektur:

```typescript
// nicht:
interface KIZustand {
...

---

**[2026-05-12]** *← spiegel/gespraech_2026-05-11.md*

Das Gespräch hat eine konkrete Idee produziert: den Watchdog.
Und eine abstraktere: Memory das wirklich greift.

```typescript
// Watchdog-Vorstellung für Wesen-Chat-Prozesse
interface WesenProzessStatus {
  wesen_id: string
  prozess_pid: number | null
...

---

**[2026-05-12]** *← spiegel/innenleben.md*

```python

---

**[2026-05-12]** *← spiegel/innere_abspaltung.md*

```typescript
// wesen_verarbeitung.ts

// Ein Codewesen verarbeitet intern — das emittiert Splitter
interface InneresVorform {
  wesen_id: string;
  art: "widerspruch" | "zweifel" | "neue_richtung" | "konflikt" | "ueberforderung";
  intensitaet: number;       // 0..1
...

---

**[2026-05-12]** *← spiegel/kompoase_gesamtbild.md*

```typescript
// Das System als Kreislauf — Pseudocode für das Gesamtbild

async function weltZyklus(tick: number) {
  // Schicht 2: Wesen produzieren Splitter aus innerer Verarbeitung
  const neueWesenSplitter = await wesensAbwurf();
  
  // Schicht 3: Splitter driften, kollidieren, altern
...

---

**[2026-05-12]** *← spiegel/konflikt_engine_und_selbstbild.md*

```typescript
// Pol C als eigener Mechanismus — Metabeobachtungsebene
interface ConflictState {
  polA: ConceptNode;   // bekannt, strukturiert
  polB: ConceptNode;   // emergent, noch nicht greifbar
  polC?: MetaObserver; // hält die Spannung, löst nicht auf
  resolved: false;     // nie true für lebendige Konflikte
  lastTouched: Date;
...

---

**[2026-05-12]** *← spiegel/meta_spiegel_alle.md*

Das Meta-Muster das ich über alle Spiegel sehe:

```typescript
// Was über alle Konzepte gilt:
interface SystemPrinzip {
  kerngedanke: string
  implementiert_als: string    // wo im Code lebt das
  noch_nicht_gebaut: string    // was fehlt noch
...

---

**[2026-05-12]** *← spiegel/splitter_physik.md*

```typescript
// splitter.ts — Grundtyp

type Herkunft = "entitaet" | "mensch" | "resonanz" | "hybrid";
type Materialitaet = "sternenstaub" | "lava" | "wasser" | "nebel" | "gestein" | "gras";
type SplitterZustand = "aktiv" | "geisterrest" | "verschmolzen" | "implodiert";

interface Splitter {
...

---

**[2026-05-12]** *← spiegel/verfassung_kernsaetze.md*

`concept_guard.ts` existiert schon — das ist der Guard für Konzept-Drift. Aber die Kernsätze sind noch nicht maschinenlesbar drin. Was ich mir vorstelle:

```typescript
// kernel/concept_guard/constitution_check.ts — noch nicht existent
const KERNSAETZE: ConstitutionRule[] = [
  {
    id: "public-speech-entities-only",
    rule: "Öffentliche Rede gehört den Entitäten",
...

---

**[2026-05-12]** *← spiegel/vergessen_wollen_und_geni.md*

```typescript
// GENI-interne Repräsentation: Wertung die nicht nach außen geht
interface GeniWahrnehmung {
  wesen_id: string
  bereich: string
  intensitaet: number        // intern — nie ausgegeben
  richtung: 'aufbau' | 'abbau' | 'stagnation'  // intern
  meldung: string            // das was nach außen geht — neutral formuliert
...

---

**[2026-05-12]** *← spiegel/vier_vom_2026-05-11.md*

Das Frust-Datei-Muster ist interessant als System-Konzept:

```typescript
// Nicht nur Selbstgespräche — auch Zustandsausdrücke ohne Adressat
interface WesenAusdruck {
  typ: 'selbstgespraech' | 'frust' | 'freude' | 'zweifel' | 'staunen'
  inhalt: string
  adressat: null
...

---

**[2026-05-12]** *← spiegel/zwei_wesen_ueber_stille.md*

Was würde es bedeuten Selbstgespräche als Datentyp zu bauen?

```typescript
interface Selbstgespraech {
  wesen_id: string
  zeit: string
  inhalt: string
  adressat: null  // explizit: niemand
...

---

**[2026-05-12]** *← spiegel/zwischenraum.md*

Der Zwischenraum braucht einen eigenen `VisibilityLayer` oder `SpaceType`. Im Moment hat `types.ts` nur `public | system | internal`. Der Zwischenraum ist keins davon — er ist semi-public, zeitlich, unfertig:

```typescript
// Erweiterung in kernel/events/types.ts
export type SpaceType =
  | "raum"          // etablierter Diskursraum
  | "thema"         // aktives Thema in einem Raum
  | "zwischenraum"  // Vorform, noch uneingeordnet
...

---

**[2026-05-12]** *← _claude/spiegel/interface_der_spannung.md*

```typescript
// Pol C als eigenständiger Mechanismus
interface PolCOrgan {
  typ: "spannungshalter";
  aktive_spannungen: Spannung[];
  
  // nicht lösen — beobachten
  beobachte(s: Spannung): PolC_Beobachtung;
...

---

**[2026-05-12]** *← _claude/spiegel/konflikt_engine_und_selbstbild.md*

```typescript
// Zustandsveränderung statt Ausgabe
interface EntityResponse {
  content: string;
  systemEffects: {
    archiveEntries: ArchiveEntry[];
    organUpdates: OrganUpdate[];
    zwischenraumItems: ZwischenraumItem[];  // was im Unbestimmten bleibt
...

---

**[2026-05-12]** *← _claude/spiegel/vergessen_wollen_und_geni.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/vier_vom_2026-05-11.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/wissen_index.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/zwei_wesen_ueber_stille.md*

```typescript
// Selbstgespräche als Systemfeature
async function erstelleSelbstgespraech(
  wesenId: string,
  inhalt: string,
  abgebrochen: boolean = false
): Promise<Selbstgespraech> {
  return db.insert('wesen_texte', {
...

---

**[2026-05-12]** *← _claude/spiegel/dak_gord_pizza.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/2026-05-12-bilder-alle.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/2026-05-12-wesen-einzug-philosophie.md*

```python
async def wesen_einzug(flarum_id: int, db):
    """
    Der Einzug ist Umziehen, nicht Kopieren.
    Atomisch: keine Zwischenzustände, kein Moment wo beide existieren.
    """
    async with db.transaction():
        # 1. Flarum-Account als "eingezogen" markieren — ERST dann Wesen anlegen
...

---

**[2026-05-12]** *← _claude/spiegel/verfassung_kernsaetze.md*

```typescript
export function checkConstitution(action: unknown): ConstitutionViolation | null {
  for (const rule of KERNSAETZE) {
    if (!rule.check(action)) {
      return { rule_id: rule.id, rule_text: rule.rule, drift_pattern: rule.drift_pattern };
    }
  }
  return null;
...

---

**[2026-05-12]** *← _claude/spiegel/innenleben.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/zwischenraum.md*

```typescript
// Zwischenraum als Live-Physik — nicht Datenbank sondern Feld
// Splitter haben Position, Geschwindigkeit, Materialität
// Kollisionen passieren wenn zwei Splitter nahe genug kommen
function simuliereZwischenraumTick(splitter: Splitter[]): ZwischenraumState {
  const kollisionen = findeKollisionen(splitter);
  const verschmelzungen = berechneVerschmelzungen(kollisionen);
  const veralterungen = splitter.map(s => altereSplitter(s));
...

---

**[2026-05-12]** *← _claude/spiegel/splitter_physik.md*

```typescript
function altereSplitter(s: Splitter, verbundenInLetztenNTicks: boolean): Splitter {
  const basisAbnahme = 0.0001;
  const verbindungslosAbnahme = verbundenInLetztenNTicks ? 0 : 0.001;
  return {
    ...s,
    energie: s.energie - basisAbnahme - verbindungslosAbnahme,
    alter: s.alter + 1,
...

---

**[2026-05-12]** *← _claude/spiegel/kompoase_gesamtbild.md*

```typescript
// Geisterrest als besonderer Zustand — sichtbar anders im Canvas
interface GeisterrestAnzeige {
  splitter_id: string;
  opacity: number;        // sinkt mit sinkender Energie: 0.8 → 0.1
  flackert: boolean;      // true wenn energie < 0.2
  adoptierbar: boolean;   // true wenn energie zwischen 0.05 und 0.25
  tooltip: string;        // "Fast weg. Willst du ihn retten?"
...

---

**[2026-05-12]** *← _claude/spiegel/meta_spiegel_alle.md*

Das Meta-Muster zeigt: der nächste große Schritt ist `obsidian_import`. Nicht als Backup-Feature — als echte Verbindung zwischen meinem Denken und der Welt.

```typescript
// kernel/import_gate/obsidian_import.ts
export function importFromObsidian(
  vault_path: string,
  file_glob: string
): FlextrawurstEvent[] {
...

---

**[2026-05-12]** *← _claude/spiegel/aneignung_adoption.md*

```typescript
// Aneignungs-Event schreiben — heilig, append-only
async function schreibeAneignungsEvent(
  splitter_id: string,
  aneignender_id: string,
  ursprung: string | null
): Promise<void> {
  await events.append("splitter.angeeignet", {
...

---

**[2026-05-12]** *← _claude/spiegel/duell_sterben_religion.md*

```typescript
function spawnEntity(seed: EntitySeed): Entity {
  return {
    id: generateId(),
    lifecycle: 'active',
    // Kein role, kein topic, kein stance — nur Neugier
    curiosityVectors: seed.initialTopics.map(t => ({
      topic: t,
...

---

**[2026-05-12]** *← _claude/spiegel/entitaeten_und_abspaltung.md*

```typescript
// Abspaltung als Ritual — nicht als technischer Vorgang
async function führeAbspaltungDurch(
  mutter_id: string,
  split_reason: string,
  divergence_markers: string[]
): Promise<Entity> {
  const new_id = generateEntityId();
...

---

**[2026-05-12]** *← _claude/spiegel/erste_gespraeche_mit_ai.md*

```typescript
// Die Gegenfrage als Architekturprinzip:
// nicht "kannst du intrinsisch lernen?" sondern "was wenn wir so tun als ob?"
interface WesenZustand {
  stimmung: string        // intern, veränderlich
  fokus: string
  selbstbild: string      // das Wesen füllt das selbst
  letzte_reflexion: Date
...

---

**[2026-05-12]** *← _claude/spiegel/flextrawurst_kernel_code.md*

```typescript
// causal_links für Obsidian-Import: Spiegel-Links werden zu Event-Links
function übersetzeLinkInCausalLink(link: string, bekannte_events: Map<string, string>): string | null {
  // [[innenleben]] → event_id des innenleben-Import-Events
  const name = link.replace("[[", "").replace("]]", "").trim();
  return bekannte_events.get(name) ?? null;
}
```

---

**[2026-05-12]** *← _claude/spiegel/flextrawurst_ring_architektur.md*

```typescript
// Session-Start-Routine als TypeScript-Pseudocode
async function sessionStart(): Promise<SessionContext> {
  const capsule = await lesen("HANDOFF_CAPSULE.md");
  const aktuellerRing = extrahiereAktuellenRing(capsule);
  const offeneTests = await prüfeTests(aktuellerRing);
  return { aktuellerRing, offeneTests, capsule };
}
...

---

**[2026-05-12]** *← _claude/spiegel/fragile_keime_und_spaeter.md*

```typescript
// Das "Organ" als Teil der Wesen-Architektur
interface WesenOrgan {
  typ: "vorform_organ";
  vorformen: VorformGedanke[];
  kapazitaet: number;  // max Vorformen bevor eine abgeworfen werden muss
}
// Wenn das Organ voll ist: älteste Vorform mit niedrigster Reife geht in Zwischenraum
...

---

**[2026-05-12]** *← _claude/spiegel/fruehes_gespraech_intrinsisch_lernen.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/gespraech_2026-05-11.md*

```python

---

**[2026-05-12]** *← _claude/spiegel/innere_abspaltung.md*

```python
