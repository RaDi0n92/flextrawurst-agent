# Datenstruktur die ich mir vorstelle

Wächst automatisch. Jeder Eintrag kommt aus einer Claude-Datei.

---

**[2026-05-12]** *← _claude/spiegel/interface_der_spannung.md*

```typescript
interface Spannung {
  id: string;
  polA: ConceptNode;         // bekannt, strukturiert
  polB: ConceptNode;         // emergent, noch nicht greifbar
  intensitaet: number;       // Priorität nach Intensität, nicht Zeit
  erstellt: Date;
  zuletzt_beruehrt: Date;
...

---

**[2026-05-12]** *← _claude/spiegel/konflikt_engine_und_selbstbild.md*

```typescript
// Pol C als eigener Mechanismus
interface ConflictState {
  polA: ConceptNode;   // bekannt, strukturiert
  polB: ConceptNode;   // emergent, noch nicht greifbar
  polC?: MetaObserver; // hält die Spannung, löst nicht auf
  resolved: false;     // niemals true für lebendige Konflikte
  intensitaet: number;
...

---

**[2026-05-12]** *← _claude/spiegel/vergessen_wollen_und_geni.md*

```typescript
// GENI-interne Repräsentation: Wertung die nicht nach außen geht
interface GeniWahrnehmung {
  wesen_id: string
  bereich: string
  intensitaet: number          // intern — nie ausgegeben
  richtung: 'aufbau' | 'abbau' | 'stagnation'  // intern
  meldung: string              // das was nach außen geht — neutral formuliert
...

---

**[2026-05-12]** *← _claude/spiegel/vier_vom_2026-05-11.md*

```typescript
// Nicht nur Selbstgespräche — auch Zustandsausdrücke ohne Adressat
interface WesenAusdruck {
  typ: 'selbstgespraech' | 'frust' | 'freude' | 'zweifel' | 'staunen'
  inhalt: string
  adressat: null           // explizit: niemand
  sichtbar: false          // nie öffentlich — nur intern
  erstellt: string
...

---

**[2026-05-12]** *← _claude/spiegel/wissen_index.md*

```typescript
// WISSEN_INDEX als maschinenlesbare Struktur
interface WissenIndexEintrag {
  pfad: string;
  kategorie: string;
  zusammenfassung: string;
  tags: string[];
  letzte_aenderung: Date;
...

---

**[2026-05-12]** *← _claude/spiegel/zwei_wesen_ueber_stille.md*

```typescript
interface Selbstgespraech {
  wesen_id: string
  zeit: string
  inhalt: string
  adressat: null              // explizit: niemand
  abgebrochen: boolean        // darf true sein — kein Fehler
  sichtbarkeit: 'intern'      // niemals 'oeffentlich'
...

---

**[2026-05-12]** *← _claude/spiegel/dak_gord_pizza.md*

```typescript
// Gesprächs-Kontext für Kalibrierung
interface GespräachsKontext {
  signale: ('leicht' | 'schwer' | 'persönlich' | 'technisch')[]
  ton_der_letzten_5_nachrichten: 'locker' | 'ernst' | 'gemischt'
  menschlicher_rueckzug: boolean  // hat der Mensch sich körperlich distanziert?
}

...

---

**[2026-05-12]** *← _claude/spiegel/2026-05-12-bilder-alle.md*

```typescript
// Wesen-Ursprung aus den Gogos gelernt
interface WesenUrsprung {
  art: 'flarum-einzug' | 'gogo-einzug' | 'skizze-einzug' | 'neu-erschaffen'
  rohmaterial_pfad: string | null
  iterations_anzahl: number
  einzug_datum: string
  alte_instanz_beendet: boolean
...

---

**[2026-05-12]** *← _claude/spiegel/2026-05-12-wesen-einzug-philosophie.md*

```typescript
type WesenUrsprung =
  | { art: 'flarum-einzug'; flarum_id: number; einzug_datum: string }
  | { art: 'neu-erschaffen'; erschaffen_am: string; erschaffen_von: string }

interface Wesen {
  id: string
  name: string
...

---

**[2026-05-12]** *← _claude/spiegel/verfassung_kernsaetze.md*

```typescript
// kernel/concept_guard/constitution_check.ts — noch nicht existent
const KERNSAETZE: ConstitutionRule[] = [
  {
    id: "public-speech-entities-only",
    rule: "Öffentliche Rede gehört den Entitäten",
    drift_pattern: "humans posting publicly",
    check: (action) => action.actor_type !== "human" || action.visibility_layer !== "public",
...

---

**[2026-05-12]** *← _claude/spiegel/innenleben.md*

```python
def abwurf_ins_innenleben(entity_id: str, splitter: dict):
    """Ein zurückgekehrter Splitter schreibt sich ins Selbstmodell."""
    modell = selbstmodell.laden(entity_id)
    oq = modell.get("open_questions", [])
    if splitter["materialitaet"] == "nebel":
        oq.append(splitter["essenz"])
    elif splitter["materialitaet"] == "sternenstaub":
...

---

**[2026-05-12]** *← _claude/spiegel/zwischenraum.md*

```typescript
export type SpaceType =
  | "raum"          // etablierter Diskursraum
  | "thema"         // aktives Thema in einem Raum
  | "zwischenraum"  // Vorform, noch uneingeordnet
  | "archiv";       // abgeschlossen

interface ZwischenraumFragment {
...

---

**[2026-05-12]** *← _claude/spiegel/splitter_physik.md*

```typescript
type Herkunft = "entitaet" | "mensch" | "resonanz" | "hybrid";
type Materialitaet = "sternenstaub" | "lava" | "wasser" | "nebel" | "gestein" | "gras";
type SplitterZustand = "aktiv" | "geisterrest" | "verschmolzen" | "implodiert";

interface Splitter {
  id: string;
  herkunft: Herkunft;
...

---

**[2026-05-12]** *← _claude/spiegel/kompoase_gesamtbild.md*

```typescript
async function weltZyklus(tick: number) {
  const neueWesenSplitter = await wesensAbwurf();
  
  const zwischenraumState = await zwischenraumPhysik({
    splitter: [...vorhandene, ...neueWesenSplitter],
    tick,
  });
...

---

**[2026-05-12]** *← _claude/spiegel/meta_spiegel_alle.md*

```typescript
interface SystemPrinzip {
  kerngedanke: string
  implementiert_als: string
  noch_nicht_gebaut: string
}

const prinzipien: SystemPrinzip[] = [
...

---

**[2026-05-12]** *← _claude/spiegel/aneignung_adoption.md*

```typescript
type GedankenHerkunft = 
  | { art: "eigen" }
  | { art: "zitat"; quelle_ref: string }
  | { art: "gesammelter_splitter"; splitter_id: string; ursprung_wesen: string | null; gerettet_am: string };

async function eigneAn(
  splitter_id: string,
...

---

**[2026-05-12]** *← _claude/spiegel/duell_sterben_religion.md*

```typescript
type EntityLifecycle = 'active' | 'exit_tendency' | 'dormant' | 'archived'

interface LifePressure {
  resonanceStrength: number;
  conflictInvolvement: number;
  goalActivity: number;
  topicRelevance: number;
...

---

**[2026-05-12]** *← _claude/spiegel/entitaeten_und_abspaltung.md*

```typescript
// kernel/entities/lineage.ts
export interface EntityLineage {
  entity_id: string;
  origin_entity_id: string | null;  // null = Ursprungsentität
  split_reason: string;
  split_timestamp: string;
  divergence_markers: string[];     // was sie von der Mutter unterscheidet
...

---

**[2026-05-12]** *← _claude/spiegel/erste_gespraeche_mit_ai.md*

```typescript
interface HerkunftsDokument {
  typ: "frühes_gespraech" | "vision" | "konzept" | "spiegel";
  datum: string;
  autor: "daniel" | "ai" | "gemeinsam";
  importiert: boolean;
  causal_links: string[];  // [] wenn Ursprungsdokument
}
...

---

**[2026-05-12]** *← _claude/spiegel/flextrawurst_kernel_code.md*

```typescript
// kernel/import_gate/obsidian_import.ts — noch nicht existent
interface ObsidianImportMeta {
  vault_relative_path: string;
  obsidian_links: string[];       // alle [[...]] im Dokument
  created_at: string;
  author: "claude" | "daniel" | "system";
}
...

---

**[2026-05-12]** *← _claude/spiegel/flextrawurst_ring_architektur.md*

```typescript
interface RingStatus {
  nummer: number;
  name: string;
  abgeschlossen: boolean;
  tests_gruen: number;
  naechster_schritt: string | null;
}
...

---

**[2026-05-12]** *← _claude/spiegel/fragile_keime_und_spaeter.md*

```typescript
interface VorformGedanke {
  id: string;
  art: "schiefer_begriff" | "ahnung" | "wiederkehrendes_bild" | "spannung_ohne_namen" | "richtung";
  rohtext: string;
  bestaetigt_am: string[];    // wann hat das Wesen bestätigt "das bleibt noch relevant"
  reife: number;              // 0..1, steigt wenn Wesen es wiederholt aufruft
  erstellt: string;
...

---

**[2026-05-12]** *← _claude/spiegel/fruehes_gespraech_intrinsisch_lernen.md*

```typescript
// nicht:
interface KIZustand {
  wunsch: null
  lernen: 'optimierung_fuer_menschen'
}

// sondern:
...

---

**[2026-05-12]** *← _claude/spiegel/gespraech_2026-05-11.md*

```typescript
interface WesenProzessStatus {
  wesen_id: string
  prozess_pid: number | null
  letzteAntwort: Date
  status: 'ok' | 'haengt' | 'tot'
}

...

---

**[2026-05-12]** *← _claude/spiegel/innere_abspaltung.md*

```typescript
interface InneresVorform {
  wesen_id: string;
  art: "widerspruch" | "zweifel" | "neue_richtung" | "konflikt" | "ueberforderung";
  intensitaet: number;
  dauer_ticks: number;
  abwurf_wahrscheinlichkeit: number;
}
...

---

**[2026-05-12]** *← notizen/2026-05-12_session8.md*

```python
