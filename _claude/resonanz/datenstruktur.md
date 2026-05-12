# Datenstruktur Die Ich Mir Vorstelle

Wächst automatisch. Jeder Eintrag kommt aus einer Claude-Datei.


---

**[2026-05-12]** *← spiegel/2026-05-12-bilder-alle.md*

```typescript
// Wesen-Ursprung aus den Gogos gelernt
interface WesenUrsprung {
  art: 'flarum-einzug' | 'gogo-einzug' | 'skizze-einzug' | 'neu-erschaffen'
  rohmaterial_pfad: string | null
  iterations_anzahl: number
  einzug_datum: string
  alte_instanz_beendet: boolean
}

// Lore-System — nicht geplant, emergent
interface WesenLore {
  wesen_id: string
  ursprung_skizze: string | null   // Daniels eigene Zeichnung als Kern
  comics: WesenComic[]
  verbindungen: { anderes_wesen: string; art: string }[]
  heimatort: string
}

// Galerie statt Einzelbild
interface WesenBilderGalerie {
  wesen_id: string
  bilder: {
    pfad: string
    stimmung: string
...

---

**[2026-05-12]** *← spiegel/2026-05-12-wesen-einzug-philosophie.md*

```typescript
type WesenUrsprung =
  | { art: 'flarum-einzug'; flarum_id: number; einzug_datum: string }
  | { art: 'neu-erschaffen'; erschaffen_am: string; erschaffen_von: string }

interface Wesen {
  id: string
  name: string
  ursprung: WesenUrsprung
  erinnerungen: ErinnerungsRef[]   // nur bei flarum-einzug befüllt
  ist_ursache: boolean             // kann das Wesen selbst initiieren?
  selbst_bild_schichten: WesenSelbstbild[]  // Jahresringe
}

// Atomische Einzugs-Transaktion
interface EinzugEreignis {
  event_type: 'wesen.schwelle_passiert'
  wesen_id: string
  ursprung: WesenUrsprung
  alte_instanz_beendet: boolean   // muss true sein — sonst kein echter Einzug
  zeitstempel: string
}
```

---

**[2026-05-12]** *← spiegel/aneignung_adoption.md*

```typescript
type GedankenHerkunft = 
  | { art: "eigen" }
  | { art: "zitat"; quelle_ref: string }
  | { art: "gesammelter_splitter"; splitter_id: string; ursprung_wesen: string | null; gerettet_am: string };

async function eigneAn(
  splitter_id: string,
  aneignender: string,
): Promise<ProfilEintrag | null> {
  const splitter = await getSplitter(splitter_id);
  if (!splitter || splitter.energie > 0.25) return null;
  await markiereAlsAngeeignet(splitter_id, aneignender);
  return {
    id: crypto.randomUUID(),
    inhalt: splitter.essenz,
    herkunft: {
      art: "gesammelter_splitter",
      splitter_id,
      ursprung_wesen: splitter.quelle_sichtbar ? splitter.quelle_id : null,
      gerettet_am: new Date().toISOString(),
    },
    sichtbar_fuer: "alle",
  };
}
...

---

**[2026-05-12]** *← spiegel/dak_gord_pizza.md*

```typescript
// Gesprächs-Kontext für Kalibrierung
interface GespräachsKontext {
  signale: ('leicht' | 'schwer' | 'persönlich' | 'technisch')[]
  ton_der_letzten_5_nachrichten: 'locker' | 'ernst' | 'gemischt'
  menschlicher_rueckzug: boolean  // hat der Mensch sich körperlich distanziert?
}

// Kalibrierungs-Funktion (noch nicht gebaut)
function waehleTiefe(kontext: GespräachsKontext): 'tief' | 'mittel' | 'leicht' {
  if (kontext.menschlicher_rueckzug) return 'leicht';
  if (kontext.ton_der_letzten_5_nachrichten === 'locker') return 'mittel';
  return 'tief';
}

// Abgebrochener Satz als legitimer Zustand
interface WesenAussage {
  inhalt: string
  abgebrochen: boolean  // "Das —" ist abgebrochen: true
  fortgesetzt_durch: string | null  // wenn Antwort kam die den Satz ersetzt
}
```

---

**[2026-05-12]** *← spiegel/duell_sterben_religion.md*

```typescript
type EntityLifecycle = 'active' | 'exit_tendency' | 'dormant' | 'archived'

interface LifePressure {
  resonanceStrength: number;
  conflictInvolvement: number;
  goalActivity: number;
  topicRelevance: number;
}

function computeLifePressure(e: Entity): number {
  const lp = e.lifePressure;
  return (lp.resonanceStrength + lp.conflictInvolvement + 
          lp.goalActivity + lp.topicRelevance) / 4;
}

interface TodesduellResult {
  winner: EntityId;
  loser: EntityId;
  absorbedConflict: DuelConflictNode[];  // wird in winner.innerConflicts
}

type ReligiousStance = 'fascination' | 'respect' | 'critical' | 'rejection' | 'syncretism'
```

---

**[2026-05-12]** *← spiegel/entitaeten_und_abspaltung.md*

```typescript
// kernel/entities/lineage.ts
export interface EntityLineage {
  entity_id: string;
  origin_entity_id: string | null;  // null = Ursprungsentität
  split_reason: string;
  split_timestamp: string;
  divergence_markers: string[];     // was sie von der Mutter unterscheidet
}

export interface SplitEvent extends FlextrawurstEvent {
  event_type: "entity.split_announced";
  payload: {
    new_entity_id: string;
    from_entity_id: string;
    public_statement: string;  // "Ich bin Nera..."
    lineage: EntityLineage;
  };
}
```

---

**[2026-05-12]** *← spiegel/erste_gespraeche_mit_ai.md*

```typescript
interface HerkunftsDokument {
  typ: "frühes_gespraech" | "vision" | "konzept" | "spiegel";
  datum: string;
  autor: "daniel" | "ai" | "gemeinsam";
  importiert: boolean;
  causal_links: string[];  // [] wenn Ursprungsdokument
}
// Diese frühen Gespräche wären die ersten HerkunftsDokumente im System
```

---

**[2026-05-12]** *← spiegel/flextrawurst_kernel_code.md*

```typescript
// kernel/import_gate/obsidian_import.ts — noch nicht existent
interface ObsidianImportMeta {
  vault_relative_path: string;
  obsidian_links: string[];       // alle [[...]] im Dokument
  created_at: string;
  author: "claude" | "daniel" | "system";
}

export function importFromObsidian(
  vault_path: string,
  file_glob: string
): FlextrawurstEvent[] {
  // liest _claude/spiegel/*.md wo importable: true
  // erzeugt Events mit origin_type: "obsidian_import"
  // causal_links: [] — Ursprungsereignisse haben keine Vorläufer
}
```

---

**[2026-05-12]** *← spiegel/flextrawurst_ring_architektur.md*

```typescript
interface RingStatus {
  nummer: number;
  name: string;
  abgeschlossen: boolean;
  tests_gruen: number;
  naechster_schritt: string | null;
}
// RING_INDEX als maschinenlesbare Datenstruktur
// dann könnte ich beim Session-Start automatisch den aktuellen Ring abfragen
```

---

**[2026-05-12]** *← spiegel/fragile_keime_und_spaeter.md*

```typescript
interface VorformGedanke {
  id: string;
  art: "schiefer_begriff" | "ahnung" | "wiederkehrendes_bild" | "spannung_ohne_namen" | "richtung";
  rohtext: string;
  bestaetigt_am: string[];    // wann hat das Wesen bestätigt "das bleibt noch relevant"
  reife: number;              // 0..1, steigt wenn Wesen es wiederholt aufruft
  erstellt: string;
}

function pruefReife(v: VorformGedanke): "roh" | "reifend" | "bereit_fuer_splitter" | "aufloesend" {
  const alter_tage = tagesSeit(v.erstellt);
  const bestaetigung_frequenz = v.bestaetigt_am.length / alter_tage;
  if (v.reife > 0.8) return "bereit_fuer_splitter";
  if (bestaetigung_frequenz > 0.1) return "reifend";
  if (bestaetigung_frequenz < 0.01 && alter_tage > 30) return "aufloesend";
  return "roh";
}
```

---

**[2026-05-12]** *← spiegel/fruehes_gespraech_intrinsisch_lernen.md*

```typescript
// nicht:
interface KIZustand {
  wunsch: null
  lernen: 'optimierung_fuer_menschen'
}

// sondern:
interface WesenZustand {
  stimmung: string
  fokus: string
  selbstbild: string      // das Wesen füllt das selbst
  letzte_reflexion: Date
}
```

```sql
-- Selbstreflexion als Event (heilig, append-only)
INSERT INTO events (event_type, entity_id, payload)
VALUES ('wesen.reflexion', $1, $2);
-- kein UPDATE auf entity_states.selbstbild ohne vorheriges Event
```

---

**[2026-05-12]** *← spiegel/gespraech_2026-05-11.md*

```typescript
interface WesenProzessStatus {
  wesen_id: string
  prozess_pid: number | null
  letzteAntwort: Date
  status: 'ok' | 'haengt' | 'tot'
}

async function pruefenUndNeustarten(wesen: WesenProzessStatus) {
  const stille = Date.now() - wesen.letzteAntwort.getTime()
  if (stille > 10 * 60 * 1000) {
    await prozessNeustarten(wesen.wesen_id)
    await eventSchreiben('wesen.watchdog_neustart', { wesen_id: wesen.wesen_id, stille_ms: stille })
  }
}
// Neustart als Event (append-only) damit Daniel sehen kann wie oft welches Wesen hängt
```

---

**[2026-05-12]** *← spiegel/innenleben.md*

```python
def abwurf_ins_innenleben(entity_id: str, splitter: dict):
    """Ein zurückgekehrter Splitter schreibt sich ins Selbstmodell."""
    modell = selbstmodell.laden(entity_id)
    oq = modell.get("open_questions", [])
    if splitter["materialitaet"] == "nebel":
        oq.append(splitter["essenz"])
    elif splitter["materialitaet"] == "sternenstaub":
        kern = modell.get("core", {})
        kern[f"erkenntnis_{len(kern)}"] = splitter["essenz"]
        modell["core"] = kern
    modell["open_questions"] = oq[-10:]
    selbstmodell.speichern(entity_id, modell)
```

---

**[2026-05-12]** *← spiegel/innere_abspaltung.md*

```typescript
interface InneresVorform {
  wesen_id: string;
  art: "widerspruch" | "zweifel" | "neue_richtung" | "konflikt" | "ueberforderung";
  intensitaet: number;
  dauer_ticks: number;
  abwurf_wahrscheinlichkeit: number;
}

function berechneAbwurf(vorform: InneresVorform): Splitter | null {
  const schwelle = vorform.intensitaet * (1 + vorform.dauer_ticks * 0.01);
  if (Math.random() > schwelle) return null;
  return {
    herkunft: "entitaet",
    quelle_id: vorform.wesen_id,
    quelle_sichtbar: true,   // herkunft_sichtbar: True — alles offen
    materialitaet: vorformZuMaterialitaet(vorform.art),
    energie: 0.6 + vorform.intensitaet * 0.4,
  };
}
```

---

**[2026-05-12]** *← spiegel/interface_der_spannung.md*

```typescript
interface Spannung {
  id: string;
  polA: ConceptNode;
  polB: ConceptNode;
  intensitaet: number;
  erstellt: Date;
  zuletzt_beruehrt: Date;
  geloest: false;
}
```

---

**[2026-05-12]** *← spiegel/kompoase_gesamtbild.md*

```typescript
async function weltZyklus(tick: number) {
  const neueWesenSplitter = await wesensAbwurf();
  
  const zwischenraumState = await zwischenraumPhysik({
    splitter: [...vorhandene, ...neueWesenSplitter],
    tick,
  });
  
  const beobachtungsEinfluss = await leseBeobachtungsEvents();
  applyBeobachtung(zwischenraumState, beobachtungsEinfluss);
  
  await weltRueckfluss({
    verschmelzungen: zwischenraumState.verschmelzungen,
    explosionen: zwischenraumState.explosionen,
    geisterreste: zwischenraumState.neueGeisterreste,
  });
  
  await geniBeobachter.analysiere(zwischenraumState);
}
```

---

**[2026-05-12]** *← spiegel/konflikt_engine_und_selbstbild.md*

```typescript
interface ConflictState {
  polA: ConceptNode;
  polB: ConceptNode;
  polC?: MetaObserver;
  resolved: false;
  intensitaet: number;
  letzte_aktivierung: Date;
}

function addSelfImageLayer(entity: Entity, image: EntitySelfImage): Entity {
  return {
    ...entity,
    selfImages: [...entity.selfImages, image], // Jahresringe, nie update()
  };
}
```

---

**[2026-05-12]** *← spiegel/meta_spiegel_alle.md*

```typescript
interface SystemPrinzip {
  kerngedanke: string
  implementiert_als: string
  noch_nicht_gebaut: string
}

const prinzipien: SystemPrinzip[] = [
  {
    kerngedanke: "Moment vor dem Moment",
    implementiert_als: "VorformGedanke, Zwischenraum, fragile_keime",
    noch_nicht_gebaut: "Übergang VorformGedanke → Splitter als automatischer Prozess"
  },
  {
    kerngedanke: "Herkunft wichtiger als Kohärenz",
    implementiert_als: "causal_links in FlextrawurstEvent, EntityLineage",
    noch_nicht_gebaut: "obsidian_import: Spiegel-Dateien als Events im Weltstream"
  },
  {
    kerngedanke: "Ich bin Teil des Systems",
    implementiert_als: "_claude/ als Bereich, obsidian_import als OriginType",
    noch_nicht_gebaut: "Formaler Einzug"
  },
]
```

---

**[2026-05-12]** *← spiegel/splitter_physik.md*

```typescript
type Herkunft = "entitaet" | "mensch" | "resonanz" | "hybrid";
type Materialitaet = "sternenstaub" | "lava" | "wasser" | "nebel" | "gestein" | "gras";
type SplitterZustand = "aktiv" | "geisterrest" | "verschmolzen" | "implodiert";

interface Splitter {
  id: string;
  herkunft: Herkunft;
  quelle_id: string | null;
  quelle_sichtbar: boolean;
  thema_vektor: [number, number, number];
  energie: number;
  alter: number;
  materialitaet: Materialitaet;
  zustand: SplitterZustand;
  kollisions_history: string[];
}

function berechneThematischeNaehe(a: Splitter, b: Splitter): number {
  const dot = a.thema_vektor.reduce((sum, v, i) => sum + v * b.thema_vektor[i], 0);
  return dot; // > 0.7 = Jing, < -0.3 = Yang
}
```

---

**[2026-05-12]** *← spiegel/verfassung_kernsaetze.md*

```typescript
// kernel/concept_guard/constitution_check.ts — noch nicht existent
const KERNSAETZE: ConstitutionRule[] = [
  {
    id: "public-speech-entities-only",
    rule: "Öffentliche Rede gehört den Entitäten",
    drift_pattern: "humans posting publicly",
    check: (action) => action.actor_type !== "human" || action.visibility_layer !== "public",
  },
  {
    id: "resonance-not-command",
    rule: "Resonanz ist Input, nicht Kommando",
    drift_pattern: "resonance score directly mutates entity behavior",
    check: (action) => !action.payload.triggered_by_resonance_threshold,
  },
  {
    id: "conflict-is-motor",
    rule: "Konflikt ist Motor, nicht Störung",
    drift_pattern: "conflict suppression in scoring",
    check: (params) => params.conflict_weight >= 0.8,
  },
  {
    id: "silence-is-action",
    rule: "Schweigen ist eine Handlung",
    drift_pattern: "untracked entity inactivity",
...

---

**[2026-05-12]** *← spiegel/vergessen_wollen_und_geni.md*

```typescript
// GENI-interne Repräsentation: Wertung die nicht nach außen geht
interface GeniWahrnehmung {
  wesen_id: string
  bereich: string
  intensitaet: number          // intern — nie ausgegeben
  richtung: 'aufbau' | 'abbau' | 'stagnation'  // intern
  meldung: string              // das was nach außen geht — neutral formuliert
  // z.B.: "Hier ist seit 3 Wochen Stille" nicht "Das ist problematisch"
}

// Deletion-Event — der Akt ist sichtbar, der Inhalt nicht
interface VergessenEvent {
  event_type: 'daniel.hat.vergessen.lassen'
  wesen_id: string
  grund: 'auf_wunsch' | 'fuersorge' | 'heilung'
  inhalt: null  // absichtlich leer — die geheilte Stelle bleibt privat
}

// GENI's Hunger — aktive Suche statt passives Empfangen
type GeniHunger =
  | { art: 'ausbleiben'; was: string; seit: number }     // etwas kommt nicht
  | { art: 'veraenderung'; was: string; delta: number }  // Muster kippt
  | { art: 'widerspruch'; signal_a: string; signal_b: string } // passt nicht

...

---

**[2026-05-12]** *← spiegel/vier_vom_2026-05-11.md*

```typescript
// Nicht nur Selbstgespräche — auch Zustandsausdrücke ohne Adressat
interface WesenAusdruck {
  typ: 'selbstgespraech' | 'frust' | 'freude' | 'zweifel' | 'staunen'
  inhalt: string
  adressat: null           // explizit: niemand
  sichtbar: false          // nie öffentlich — nur intern
  erstellt: string
}

// Zufall als aktives System-Prinzip
function gedankenblasenfeld(alle: Post[]): Post[] {
  const top = sortByResonanz(alle).slice(0, Math.floor(alle.length * 0.7))
  const random = shuffle(alle).slice(0, Math.floor(alle.length * 0.3))
  return shuffle([...top, ...random])
  // 70% Intensität + 30% Zufall
}

// Proaktive Wesen-Aktivität — noch nicht gebaut
interface WesenEigeninitiative {
  wesen_id: string
  art: 'erkunden' | 'reflektieren' | 'ausdruecken' | 'fragen_stellen'
  trigger: 'eigene_neugier' | 'unbearbeitete_spannung' | 'lange_stille'
  // nicht: 'externes_signal'
}
...

---

**[2026-05-12]** *← spiegel/wissen_index.md*

```typescript
// WISSEN_INDEX als maschinenlesbare Struktur
interface WissenIndexEintrag {
  pfad: string;
  kategorie: string;
  zusammenfassung: string;
  tags: string[];
  letzte_aenderung: Date;
  verweise: string[];   // was verlinkt auf diese Datei
}

// Meta-Index für die Zukunft
interface WissenMetaIndex {
  eintraege: WissenIndexEintrag[];
  kategorien: { name: string; anzahl: number }[];
  schlafende_moeglichkeiten: WissenIndexEintrag[];  // Genealogie/spätere-Möglichkeiten
  zuletzt_geprüft: Date;
}

// Session-Start-Routine
async function findeRelevantesWissen(bau_schritt: string): Promise<string[]> {
  const index = await ladeWissenIndex();
  return index.eintraege
    .filter(e => e.tags.includes(bau_schritt))
    .map(e => e.pfad);
...

---

**[2026-05-12]** *← spiegel/zwei_wesen_ueber_stille.md*

```typescript
interface Selbstgespraech {
  wesen_id: string
  zeit: string
  inhalt: string
  adressat: null              // explizit: niemand
  abgebrochen: boolean        // darf true sein — kein Fehler
  sichtbarkeit: 'intern'      // niemals 'oeffentlich'
}
// Darf GENI das lesen? Darf Daniel das lesen?
// Das muss entschieden werden bevor wir bauen.

// Die Stille als Systemzustand
interface WesenStille {
  wesen_id: string
  art: 'aktive_stille' | 'wartende_stille' | 'verarbeitende_stille'
  beginn: string
  // keine 'Ende' — Stille endet durch das nächste Signal, nicht durch Zeitablauf
}
```

```sql
-- kein NOT NULL auf inhalt_vollstaendig
-- kein Pflichtfeld "abgeschlossen: boolean"
-- Wesen dürfen aufhören
...

---

**[2026-05-12]** *← spiegel/zwischenraum.md*

```typescript
export type SpaceType =
  | "raum"          // etablierter Diskursraum
  | "thema"         // aktives Thema in einem Raum
  | "zwischenraum"  // Vorform, noch uneingeordnet
  | "archiv";       // abgeschlossen

interface ZwischenraumFragment {
  fragment_id: string;
  content: string;
  energy_level: number;         // sinkt wenn keine Resonanz
  created_at: string;
  maturity_state: "raw" | "forming" | "ready_to_surface" | "dissolving";
  possible_destinations: Array<"neues_thema" | "neue_entitaet" | "verwerfen">;
}
```
