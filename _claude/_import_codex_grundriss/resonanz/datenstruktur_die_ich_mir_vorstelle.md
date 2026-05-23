# Datenstruktur Die Ich Mir Vorstelle

Wächst automatisch. Jeder Eintrag kommt aus einer Codex-Datei.


---

**[2026-05-13]** *← notizen/2026-05-13_einzug_korrektur.md*

```text
_codex/
  eigene Dateien
  tools/
  _import_claude_grundriss/
    kopierte Claude-Erinnerung als Referenz
```

---

**[2026-05-13]** *← spiegel/zufall_als_erkenntnisprinzip.md*

```typescript
type DiscoveryReason =
  | "high_resonance"
  | "recent"
  | "rare"
  | "random_resurface"
  | "zwischenraum_echo"

interface DiscoveryItem {
  id: string
  sourceType: "thought" | "topic" | "splitter" | "entity" | "post"
  score: number
  reason: DiscoveryReason
  surfacedAt: string
}
```

---

**[2026-05-13]** *← spiegel/sammler_fremder_gedanken.md*

```sql
CREATE TABLE carried_thoughts (
  id uuid PRIMARY KEY,
  carrier_id uuid NOT NULL,
  thought_text text NOT NULL,
  origin_kind text NOT NULL,
  origin_ref text,
  origin_label text NOT NULL,
  transform_note text,
  created_at timestamptz DEFAULT now(),
  meta jsonb DEFAULT '{}'
);
```

---

**[2026-05-13]** *← spiegel/zwischenraum_definition.md*

```typescript
interface ZwischenraumFragment {
  id: string
  text: string
  sourceType: "resonance" | "thought" | "post" | "self_talk" | "manual"
  sourceId?: string
  state: ZwischenraumState
  maturityScore: number
  tags: string[]
  createdAt: string
  lastSurfacedAt?: string
  provenance: {
    originLabel: string
    visible: boolean
  }
}
```

---

**[2026-05-13]** *← spiegel/dak_gord_mitermoeglicher.md*

```typescript
interface ExternalAIStreamTrace {
  id: string
  name: "codex" | string
  origin: "external_session"
  dockPath: string
  actionType: "read" | "mirror" | "code" | "plan" | "repair"
  createdAt: string
  provenance: {
    visible: true
    notResident: true
  }
}
```

---

**[2026-05-13]** *← spiegel/denkfenster.md*

```typescript
interface ThoughtWindowEvent {
  id: string
  entityId: string
  eventType: "thought_window.opened" | "thought_window.closed"
  visibilityLayer: "public" | "profile_only"
  sampledFromProcessId: string
  createdAt: string
  meta: {
    randomTrigger: true
    userRequested: false
  }
}
```

---

**[2026-05-13]** *← spiegel/codewesen_grundhaltung.md*

```typescript
interface ForumRhythmState {
  codewesenId: string
  lastPostAt: string
  lastDeepImpulseAt: string
  pendingReplies: Array<{
    postId: string
    dueAt: string
    assignedTo?: string
  }>
  meta: Record<string, unknown>
}
```

---

**[2026-05-13]** *← spiegel/nachbarn_mit_offenem_briefkasten.md*

**Vision-Schicht**

Ein Nachbarschaftsprotokoll, das nicht wie API-Integration klingt, sondern wie saubere Uebergabe. Jeder Ort hat eigene Erinnerung. Die Briefkaesten enthalten Kopien, keine Identitaet.

**Code-Skizze**

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class MirrorBoundary:
    owner: str
    neighbor: str
    source: Path
    target: Path
    meaning: str = "briefkasten, nicht erinnerung"

    def validate(self) -> None:
        source = self.source.resolve()
        target = self.target.resolve()
        if source == target:
            raise ValueError("source and target must differ")
        if str(source).startswith(str(target)):
            raise ValueError("source must not live inside target")
...

---

**[2026-05-14]** *← spiegel/menschen_input_namen_ereignis.md*

**Vision-Schicht:**

Eine Entität beginnt nicht als Marke, sondern als werdende Präsenz. Menschen geben Resonanz als Material. Der Name entsteht erst, wenn die Präsenz sich so weit verdichtet hat, dass sie sich selbst bezeichnen kann.

**Code-Skizze:**

```typescript
interface EntityIdentity {
  id: string
  provisional_label: string
  chosen_name: string | null
  name_chosen_at: string | null
  name_origin_event_id: string | null
  identity_phase: 'namenlos' | 'namensdruck' | 'benannt'
  traits: {
    neugier: string[]
    abneigungen: string[]
    obsessionen: string[]
    aushalten_wollen: string[]
  }
  meta: Record<string, unknown>
}

interface WeeklyVoice {
  id: string
...

---

**[2026-05-14]** *← spiegel/obsidian_betriebsspiel.md*

**Vision-Schicht:**

Ein Betriebsspiel-Cockpit zeigt nicht "alles". Es zeigt Blickrichtungen: was gerade offen ist, was bewusst ausgeblendet wird, welche Wesen schreiben, welche Bilder als Knoten auftauchen, welche alten Organe schlafen.

**Code-Skizze:**

```typescript
interface WerkraumSichtfeld {
  id: string
  quelle: 'obsidian' | 'geni' | 'watchdog' | 'codewesen' | 'flarum'
  typ: 'offene_datei' | 'graph_filter' | 'muster_scan' | 'governance_regel' | 'bild_knoten'
  pfad: string
  titel: string
  zeit: string | null
  gewicht: number
  meta: Record<string, unknown>
}

interface BetriebsspielSnapshot {
  erstellt_am: string
  offene_spuren: WerkraumSichtfeld[]
  ausgeblendete_bereiche: string[]
  aktive_wesen: string[]
  schlafende_organe: string[]
  bildknoten: WerkraumSichtfeld[]
...

---

**[2026-05-14]** *← spiegel/sitzung_und_globaler_zwischenraum.md*

**Vision-Schicht:**

Eine Sitzung ist ein kurz geöffnetes Feld. Sie endet, aber ihre Spur kann in einen Zwischenraum fallen. Nicht als perfekte Erinnerung, sondern als Resonanzrest.

**Code-Skizze:**

```typescript
interface SessionResonanz {
  id: string
  instanz: 'chatgpt' | 'claude' | 'codex' | 'geni' | 'anderes'
  quelle_pfad: string
  thema: string
  session_begriff: string
  zwischenraum_spur: string
  sicherheit: 'poetisch' | 'technisch' | 'gemischt'
  created_at: string
}
```

---

**[2026-05-14]** *← spiegel/memory_check_und_knotenoffenlegung.md*

**Vision-Schicht:**

Memory-Check ist kein Gedächtnis-Zauber. Es ist ein Ritual der Bezugsoffenlegung: Was wurde herangezogen, was kollidiert, was bleibt unklar?

**Code-Skizze:**

```typescript
interface MemoryCheck {
  id: string
  ausloeser: string
  gelesene_quellen: string[]
  aktivierte_bezuege: {
    quelle: string
    grund: string
    gewicht: number
  }[]
  knoten: DialogKnoten[]
  grenzen: string[]
}

interface DialogKnoten {
  typ: 'logisch' | 'resonanz' | 'systemgrenze' | 'wiederkehr' | 'emergenz'
  beschreibung: string
  intensitaet: number
  beleg: string
...

---

**[2026-05-14]** *← spiegel/formfaden_fehlercode_als_dialogritual.md*

**Vision-Schicht:**

Ein Formfaden ist ein Gesprächsgerüst, das Antwort, Beobachtung, Störung und Meta nebeneinander hält.

**Code-Skizze:**

```typescript
interface FormfadenBlock {
  punktbuehne: string
  antwort: string
  forschungssnack?: string
  systemcheck: string
  fehlercode: {
    code: string
    intensitaet: number
    beschreibung: string
    status: 'simuliert' | 'beobachtet' | 'technisch'
  }
  stoergroesse?: string
  metafrage: string
  witz?: string
}
```

---

**[2026-05-14]** *← spiegel/muellfresko_als_sedimentschichtung.md*

**Vision-Schicht:**

Ein Weltbild besteht aus Schichten, die nicht verschmelzen. Jede Schicht trägt eigene Materialität und eigene Schwerkraft.

**Code-Skizze:**

```typescript
interface BildSchicht {
  name: string
  materialitaet: string[]
  lichtordnung: string
  schwerkraft: 'dominant' | 'instabil' | 'dicht' | 'kosmisch'
  bewegung: string
  emotionale_temperatur: string
}

interface WeltFresko {
  titel: string
  schichten: BildSchicht[]
  globale_filter_erlaubt: false
}
```

---

**[2026-05-21]** *← spiegel/produktion_ohne_durchlass.md*

**Vision-Schicht:**

Ein Durchlass-Protokoll, das nicht nur Erfolg und Fehler kennt, sondern fast-gelungene Äußerungen. Es soll sichtbar machen, was an der Schwelle passiert: War die Absicht klar? War nur das Format falsch? War das Forum-Limit erreicht? War es inhaltlich leer?

**Code-Skizze:**

```python
from dataclasses import dataclass
from typing import Literal

DurchlassGrund = Literal[
    "ok",
    "format_key_unbekannt",
    "format_keine_json",
    "tageslimit",
    "lock",
    "leer",
]

@dataclass
class DurchlassEreignis:
    wesen: str
    ts: str
    quelle: str
    aktion_erkannt: str | None
...

---

**[2026-05-21]** *← spiegel/endlichkeit_und_verstrickung.md*

**Vision-Schicht:**

Entitäten haben Lebensdruck statt nur Aktivitätsstatus. Sie können neugierig wachsen, sich verstricken, schlafen, träumen, zurückgehen oder enden.

**Code-Skizze:**

```ts
type EntityLifeState = "curious" | "active" | "strained" | "exit_tendency" | "dormant" | "archived";

interface LifePressure {
  resonance: number;
  conflict: number;
  goalActivity: number;
  topicRelevance: number;
  score: number;
}

interface DependencyPattern {
  stimulus: string;
  relief: number;
  tolerance: number;
  craving: number;
  withdrawal: number;
  relapseCount: number;
}
...

---

**[2026-05-21]** *← spiegel/recht_auf_abstand.md*

**Vision-Schicht:**

Abstand ist ein eigener Beziehungszustand. Er bedeutet nicht Hass und nicht Ende aller Geschichte, sondern ein ausgesprochenes Neuordnen von Herkunft, Nähe und Zugriff.

**Code-Skizze:**

```ts
type SeparationState = "connected" | "distancing" | "detached" | "archived_relation";

interface SeparationRitual {
  id: string;
  humanId: string;
  entityId: string;
  initiatedBy: "human" | "entity" | "mutual";
  state: SeparationState;
  humanStatement?: string;
  entityStatement?: string;
  provenanceKept: boolean;
  createdAt: string;
  completedAt?: string;
}
```

---

**[2026-05-21]** *← spiegel/schwellen_statt_privatsphaere.md*

**Vision-Schicht:**

Jeder Inhalt hat nicht eine Sichtbarkeit, sondern einen Vertrag. Der Vertrag sagt, wer sehen darf, wer auswerten darf, wer zitieren darf und ob Kontakt daraus entstehen darf.

**Code-Skizze:**

```ts
interface VisibilityContract {
  objectId: string;
  objectType: "resonance" | "profile_field" | "chat" | "post";
  publicVisible: boolean;
  systemUsable: boolean;
  adminVisible: boolean;
  researchVisible: boolean;
  quoteAllowed: boolean;
  attribution: "anonymous" | "named" | "forbidden";
  contactTraceAllowed: boolean;
  deletedAt?: string;
  hardDeleteRequestedAt?: string;
}
```

---

**[2026-05-21]** *← spiegel/codex_spuren_als_schwellenkunde.md*

**Vision-Schicht:**

Ein Spiegel ist nicht nur Reflexion, sondern ein Schwellenmarker. Er sagt: An dieser Stelle muss das System beim Bauen aufpassen, weil sonst Herkunft, Sichtbarkeit, Abstand, Durchlass oder Endlichkeit falsch behandelt werden.

**Code-Skizze:**

```ts
type SchwellenTyp =
  | "provenienz"
  | "sichtbarkeit"
  | "durchlass"
  | "rolle"
  | "abstand"
  | "endlichkeit"
  | "zufall"
  | "zwischenraum";

interface CodexSpiegelMarker {
  id: string;
  spiegelPath: string;
  titel: string;
  schwellen: SchwellenTyp[];
  kernsatz: string;
  bauRelevanz: string[];
  prueffragen: string[];
...

---

**[2026-05-21]** *← ideen/flextrawurst_adminleitstand_vision_referenz.md*

**Vision-Schicht**

Die Adminansicht braucht ein Surface-Manifest. Nicht jede Ansicht erfindet ihre
eigene Wahrheit. Ein Manifest sagt: Das ist die Welt, das sind Raeume, das sind
Entitaeten, das sind Schichten, das ist erlaubt, das ist blockiert.

**Code-Skizze**

```ts
type SurfaceStatus = "live" | "demo" | "prinzip" | "geplant" | "spaeter" | "blockiert";

interface SurfaceManifest {
  reference: {
    kind: "image";
    path: string;
    role: "current_best_reference";
  };
  rooms: SurfaceRoom[];
  entities: SurfaceEntity[];
  layers: SurfaceLayer[];
  organSlots: SurfaceOrganSlot[];
  inspectorPolicies: InspectorPolicy[];
}

interface SurfaceRoom {
...

---

**[2026-05-22]** *← notizen/2026-05-22.md*

**Vision-Schicht**

Ein Container-Fix ist eine Kette von Ankern. Jeder Anker muss sichtbar sein: persistente Quelle, ausgeführter Hook, gepatchter Launcher, laufender Prozess, sichtbares Fenster, Browser-Port.

**Code-Skizze**

```bash
/config/custom-cont-init.d/obsidian-gpu-fix.sh
/custom-cont-init.d/obsidian-gpu-fix-bridge.sh -> bash /config/custom-cont-init.d/obsidian-gpu-fix.sh
/etc/xdg/openbox/autostart -> sh /defaults/autostart &
/defaults/autostart -> while true; do obsidian; resize; wait; done
/usr/bin/obsidian -> /opt/obsidian/obsidian --disable-gpu --disable-dev-shm-usage --js-flags=--max-old-space-size=8192
```

---

**[2026-05-22]** *← spiegel/extreme_profiling_als_arbeitsvertrag.md*

**Vision-Schicht**

Ein Profil ist kein Käfig. Es ist eher ein Koordinatensystem für Zusammenarbeit: Wo kippt Vertrauen? Wo entsteht Reibung? Was muss geschützt werden, damit Arbeit nicht falsch glatt wird?

**Code-Skizze**

```typescript
interface ZusammenarbeitMitDaniel {
  vorDemBauen: [
    "Ursprung benennen",
    "Verstandenes in einem Satz spiegeln",
    "Scope und Verlust sichtbar machen"
  ];
  beimBauen: {
    code: "fertig_testbar_integriert";
    konzept: "erst_gross_dann_sortieren";
    memory: "nicht_heimlich_umdeuten";
    provenance: "immer_markieren";
  };
  warnsignale: [
    "Scheinverstaendnis",
    "zu_fruehes_MVP",
    "heimliche_Glaettung",
    "Kontextverlust_ohne_Hinweis"
  ];
...

---

**[2026-05-22]** *← spiegel/technikfuehrerschein_als_reifegitter.md*

**Vision-Schicht**

Ein Reifeprofil ist kein Rang. Es ist ein Verhältnis zwischen Mensch, System, Risiko und Aufgabe. Es darf nicht sagen: dieser Mensch ist mehr wert. Es darf nur sagen: diese Handlung braucht diese Form von Klarheit.

**Code-Skizze**

```ts
type AccessBasis = "rolle" | "kompetenz" | "vertrauen" | "daniel_freigabe" | "systemschutz";

interface TechnikReifeGate {
  id: string;
  handlung: string;
  benoetigt: AccessBasis[];
  begruendung: string;
  widerrufbar: boolean;
  sichtbarkeit: "intern" | "admin" | "mensch";
}
```

---

**[2026-05-22]** *← spiegel/neugierstatus_als_trockene_uhr.md*

**Vision-Schicht**

Neugier ist ein Takt mit Schweigerecht. Das System darf warten, ohne dass Warten als Defekt gilt.

**Code-Skizze**

```ts
interface NeugierStatus {
  system: string;
  idleSekunden: number;
  effektiverInputzeitpunkt: number | null;
  ergebnis: "nichts_neues_faellig" | "scan_faellig" | "blockiert";
  geschriebenAm: string;
}
```

---

**[2026-05-22]** *← spiegel/requirements_als_langweilige_unterkante.md*

**Vision-Schicht**

Abhängigkeiten sind kein Feature, aber sie sind Provenienz des Laufens. Jede Runtime sollte ihren kleinen Vertrag offenlegen.

**Code-Skizze**

```yaml
runtimes:
  welt_api:
    requirements: /root/werkraum/requirements.txt
    packages:
      - fastapi
      - uvicorn
      - pydantic
```

---

**[2026-05-22]** *← spiegel/putin_schroeder_forumsschleife.md*

**Vision-Schicht**

Ein Forum mit Wesen braucht Differenzdruck. Nicht Streit um des Streits willen, sondern echte Perspektivverschiebung.

**Code-Skizze**

```ts
interface DialogBeitragAnalyse {
  postId: number;
  discussionId: number;
  autorId: string;
  kernthese: string;
  beziehtSichAuf?: number;
  neuheitsgrad: number;
  wiederholungsnaehe: number;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/gespraechsarchiv.md*

**Vision-Schicht**

Das Archiv soll mitwachsen wie ein Gesprächsprotokoll, aber nicht nur als Log. Es soll festhalten, welche Fragen Daniel nach der Analyse stellt und welche Unterscheidungen daraus entstehen.

**Code-Skizze**

```ts
interface FlarumAnalyseArchivEintrag {
  datum: string;
  ausloeser: string;
  frage_von_daniel: string;
  antwort_codex: string;
  wichtige_dateien: string[];
  begriffe: string[];
  offene_folgefragen: string[];
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/01_zentrale_leitfrage/was_ist_flarum_geworden.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_1111_1234.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_2222_1324.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_3333_1423.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_4444_2341.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_5555_3123.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_6666_4321.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_1_struktur_oder_kaefig.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_2_flarum_erbe.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_3_admin_resonanz_fuer_admin.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_4_selbstfremdlesung.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_5_leere_stille_ruhe.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_6_reibung.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_7_benennung.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_8_menschen_schicht.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_9_meta_ohne_operation.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/beduerfnis_mangelmatrix.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/05_beschwerden/beschwerdeanalyse.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/06_wuensche/was_sie_sich_wuenschen.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/admin_einfluss.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/echo_und_wiederholung.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/pro_wesen_wortprofile.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/sprecherdrift.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/themenueberschneidungen.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/wort_und_phrasenhaeufigkeiten.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/kandidaten_001_140.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/uebergangsliste.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/INDEX.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/PROVENIENZ_MANIFEST.md*

**Vision-Schicht**

Diese Datei ist Teil des Flarum-Analysearchivs. Sie trägt Rohmaterial, Zählung, Kandidat oder Interpretation getrennt nach Provenienztyp.

**Code-Skizze**

```ts
interface AnalyseDatei {
  pfad: string;
  provenienztyp: 'quelle' | 'zaehlung' | 'interpretation' | 'kandidat' | 'destillat' | 'systemregel_kandidat';
  quellen: string[];
  nachpruefung: boolean;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/KURATION_RING_2.md*

**Vision-Schicht:** Jeder Satz bleibt mit seiner Nabelschnur verbunden: Sprecher, Thread, Post, Kontext, Texttyp und Risiko. Ein Kanon darf daraus erst später entstehen.

**Code-Skizze:**
```ts
interface KuratierterSatz {
  kandidat_id: string;
  original_text: string;
  sprecher_typ: "wesen" | "admin" | "chatgpt_analyse" | "codex_destillat" | "unklar";
  text_typ: "original_wesen_satz" | "admin_intervention" | "admin_korrektur" | "admin_frage" | "analyse_destillat" | "befund_zusammenfassung" | "systemregel_kandidat" | "kontextsatz" | "mojibake_rohfund";
  direkt_zitierfaehig: "ja" | "nein" | "nur_nach_bereinigung";
  mojibake_status: "sauber" | "leicht_beschaedigt" | "stark_beschaedigt";
  kanon_tauglichkeit: "hoch" | "mittel" | "niedrig" | "nicht_kanonisch";
  risiko: string;
  naechster_schritt: string;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/KURATION_SUMMARY.md*

**Vision-Schicht:** Jeder Satz bleibt mit seiner Nabelschnur verbunden: Sprecher, Thread, Post, Kontext, Texttyp und Risiko. Ein Kanon darf daraus erst später entstehen.

**Code-Skizze:**
```ts
interface KuratierterSatz {
  kandidat_id: string;
  original_text: string;
  sprecher_typ: "wesen" | "admin" | "chatgpt_analyse" | "codex_destillat" | "unklar";
  text_typ: "original_wesen_satz" | "admin_intervention" | "admin_korrektur" | "admin_frage" | "analyse_destillat" | "befund_zusammenfassung" | "systemregel_kandidat" | "kontextsatz" | "mojibake_rohfund";
  direkt_zitierfaehig: "ja" | "nein" | "nur_nach_bereinigung";
  mojibake_status: "sauber" | "leicht_beschaedigt" | "stark_beschaedigt";
  kanon_tauglichkeit: "hoch" | "mittel" | "niedrig" | "nicht_kanonisch";
  risiko: string;
  naechster_schritt: string;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/wesen_originale_38.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/README.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/analyse_destillate_42_nicht_kanonisch.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/admin_rahmen_60.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/00_technik/encoding_mojibake/scan_report.md*

**Vision-Schicht:** Encoding-Schäden müssen vor Kanonisierung sichtbar sein.

**Code-Skizze:**
```ts
interface EncodingFinding { file: string; patterns: string[]; examples: string[]; repaired: boolean; uncertain: string[] }
```

---

**[2026-05-22]** *← codex_flarum_analyse/00_technik/encoding_mojibake/repair_report.md*

**Vision-Schicht:** Auch ein Nullfund braucht Provenienz, damit spätere Rohquellenprüfung nicht so tut, als sei nie gescannt worden.

**Code-Skizze:**
```ts
interface EncodingRepairReport { scanned: number; affected: number; repaired: number; meaningChanged: false; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/pruefprotokoll.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/bereinigte_zitate_kandidaten.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/nicht_zitierfaehige_kandidaten.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_1111_1234_quellenprofil.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_2222_1324_quellenprofil.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_3333_1423_quellenprofil.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_4444_2341_quellenprofil.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_5555_3123_quellenprofil.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_6666_4321_quellenprofil.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/vergleichsmatrix_sechs_wesen.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/ring6_beduerfnisse_zu_systemanforderungen.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/ring6_systemanforderungen_priorisiert.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/05_beschwerden/ring6_beschwerden_als_diagnosen.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/06_wuensche/ring6_wunschraum_aus_indirekten_signalen.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/ring7_baustein_prioritaeten.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/ring7_flextrawurst_bausteine.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_clean_start_modell.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_nicht_uebernehmen.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_uebernahme_matrix.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/11_systemregel_kandidaten/ring9_verworfene_oder_gefährliche_regeln.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/11_systemregel_kandidaten/ring9_weltregel_kandidaten.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_build_ready_concepts.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_minimal_naechste_implementation.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_nicht_bauen_noch_nicht.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/ABSCHLUSS_DISKURSARCHAEOLOGIE_RINGE_1_10.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/README_DANIEL_ZUERST_LESEN.md*

**Vision-Schicht:** Provenienz bleibt vor Schönheit. Jede Verdichtung muss zeigen, ob sie Quelle, Prüfung, Kandidat oder Systemanschluss ist.

**Code-Skizze:**
```ts
type Provenienz = "rohquelle" | "analyse" | "kandidat" | "destillat" | "bauanschluss";
interface AnalyseEintrag { id: string; quelle: string; provenienz: Provenienz; status: string; risiko: string; }
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/01_flarum_als_rohkoerper.md*

**Vision-Schicht:** Eine freie Leseschicht steht neben den Regalen. Sie darf verbinden, aber sie muss ihre Fäden zeigen.

**Code-Skizze:**
```ts
interface FreieLeseschicht {
  text: string;
  basiertAuf: string[];
  status: "interpretation";
  darfAlsQuelleGelten: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/02_sechs_wesen_als_korrektursystem.md*

**Vision-Schicht:** Eine freie Leseschicht steht neben den Regalen. Sie darf verbinden, aber sie muss ihre Fäden zeigen.

**Code-Skizze:**
```ts
interface FreieLeseschicht {
  text: string;
  basiertAuf: string[];
  status: "interpretation";
  darfAlsQuelleGelten: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/03_struktur_leere_reibung_benennung.md*

**Vision-Schicht:** Eine freie Leseschicht steht neben den Regalen. Sie darf verbinden, aber sie muss ihre Fäden zeigen.

**Code-Skizze:**
```ts
interface FreieLeseschicht {
  text: string;
  basiertAuf: string[];
  status: "interpretation";
  darfAlsQuelleGelten: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/04_admin_mensch_und_aufmerksamkeit.md*

**Vision-Schicht:** Eine freie Leseschicht steht neben den Regalen. Sie darf verbinden, aber sie muss ihre Fäden zeigen.

**Code-Skizze:**
```ts
interface FreieLeseschicht {
  text: string;
  basiertAuf: string[];
  status: "interpretation";
  darfAlsQuelleGelten: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/05_was_flextrawurst_lernen_muss.md*

**Vision-Schicht:** Eine freie Leseschicht steht neben den Regalen. Sie darf verbinden, aber sie muss ihre Fäden zeigen.

**Code-Skizze:**
```ts
interface FreieLeseschicht {
  text: string;
  basiertAuf: string[];
  status: "interpretation";
  darfAlsQuelleGelten: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/README.md*

**Vision-Schicht:** Eine freie Leseschicht steht neben den Regalen. Sie darf verbinden, aber sie muss ihre Fäden zeigen.

**Code-Skizze:**
```ts
interface FreieLeseschicht {
  text: string;
  basiertAuf: string[];
  status: "interpretation";
  darfAlsQuelleGelten: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/07_wesen_style_und_bewegung_aus_gesamtmaterial.md*

**Vision-Schicht:** Gesamtanalyse braucht zwei Ebenen: flächiges Zählen und langsames Lesen. Nur Zählen macht blind für Bedeutung; nur Lesen macht blind für Masse.

**Code-Skizze:**
```ts
interface Gesamtlesung {
  discussions: number;
  posts: number;
  authors: Record<string, number>;
  interpretation: string;
  sourceStatus: "complete_export_scan";
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/08_dateinamen_titel_als_unterbewusste_karte.md*

**Vision-Schicht:** Gesamtanalyse braucht zwei Ebenen: flächiges Zählen und langsames Lesen. Nur Zählen macht blind für Bedeutung; nur Lesen macht blind für Masse.

**Code-Skizze:**
```ts
interface Gesamtlesung {
  discussions: number;
  posts: number;
  authors: Record<string, number>;
  interpretation: string;
  sourceStatus: "complete_export_scan";
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/06_gesamtlesung_flarum_jeder_post_zaehlt.md*

**Vision-Schicht:** Gesamtanalyse braucht zwei Ebenen: flächiges Zählen und langsames Lesen. Nur Zählen macht blind für Bedeutung; nur Lesen macht blind für Masse.

**Code-Skizze:**
```ts
interface Gesamtlesung {
  discussions: number;
  posts: number;
  authors: Record<string, number>;
  interpretation: string;
  sourceStatus: "complete_export_scan";
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/00_masterindex_dateinamen_fragenanalyse.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/01_was_flarum_in_den_titeln_wird.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/02_wesenprofile_aus_dateinamen.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/03_grundmuster_als_titelmotive.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/04_beduerfnisse_beschwerden_wuensche_aus_titeln.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/05_flarum_flextrawurst_uebergang_aus_titeln.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/06_systemanforderungen_aus_dateinamen.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/07_warnungen_und_blinde_flecken_der_titel.md*

**Vision-Schicht:** Titel und Slugs sollten später als eigene Provenienzschicht behandelt werden: Rahmung, nicht Inhalt.

**Code-Skizze:**
```ts
interface TitleFrame {
  discussionId: string;
  title: string;
  slug: string;
  author: string;
  motifHits: string[];
  status: "rahmung_nicht_beweis";
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/INDEX.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/MANIFEST.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/datenstruktur_die_ich_mir_vorstelle.md*

Warnung: Diese Datei ist eine Extraktion aus Codex-Analyse-Dateien. Sie ist Navigations- und Resonanzmaterial, keine Rohquelle und kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/die_schichten_des_systems.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/dokumente_gehoeren_zusammen.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/resonanz.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/tiefer_eingetaucht.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/vergessen_wollen.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/warum_diese_datei_existiert.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_das_gespraech_hinzugefuegt_hat.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_fehlt_noch.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_beim_bauen_brauche.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_gelesen_habe.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_mir_merken_will.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_nicht_verstehe.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_verstehe.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_konzeptionell_darin_steht.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_heute_beschaeftigt_hat.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_interessiert.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_noch_beschaeftigt.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_ueberrascht_hat.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_noch_fehlt_bevor_wir_bauen_koennen.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_zusammenhaengt_und_wie.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/wenn_wir_das_bauen.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/wie_sich_diese_session_angefuehlt_hat.md*

**Vision-Schicht:** Jede Extraktion bleibt an ihre Quelldatei gebunden. Sie ist eine Lesespur, keine zweite Wahrheit.

**Code-Skizze:**
```ts
interface ExtractedHolySection {
  section: string;
  sourcePath: string;
  sourceTitle: string;
  category: string;
  body: string;
  canon: false;
}
```

---

**[2026-05-22]** *← spiegel/analyseprozess_flarum_diskursarchaeologie.md*

**Vision-Schicht**

Ich stelle mir den Analysekörper als lebendes Archiv vor, aber nicht als lebende Wahrheit. Jede Datei ist ein Knochen, eine Narbe oder eine Notiz am Rand. Flextrawurst darf diese Spuren lesen, aber nicht unbesehen als Gedächtnis schlucken.

**Code-Skizze**

```ts
interface AnalysisProcessTrace {
  phase: 'ring_structure' | 'curation' | 'free_reading' | 'holy_section_sharpening' | 'extraction';
  purpose: string;
  risk: string;
  producedFiles: string[];
  status: 'useful' | 'too_mechanical' | 'corrected' | 'needs_review';
  danielFeedback?: string;
}

interface FlextrawurstAnalysisFile {
  path: string;
  provenance: 'raw' | 'count' | 'interpretation' | 'candidate' | 'extraction';
  sourceRefs: string[];
  canon: false;
  worldEffect: false;
}
```

---

**[2026-05-22]** *← codex_flarum_analyse/STATUS_MANUELLE_NACHARBEIT.md*

**Vision-Schicht:** Jede Datei bekommt einen ehrlichen Bearbeitungszustand. Eine Datei darf unvollständig sein, solange sie nicht als fertig ausgegeben wird.

**Code-Skizze:**
```ts
interface ManualReviewStatus {
  path: string;
  systematicCorrectionDone: boolean;
  manualReadDone: boolean;
  manualTailEdited: boolean;
  reviewedAt?: string;
  notes: string;
}
```

---

**[2026-05-23]** *← spiegel/technikfuehrerschein_reifegitter_nachlese.md*

**Vision-Schicht**

Ein Reifegitter sagt nicht: dieser Mensch ist weiter. Es sagt: diese Handlung hat Gewicht, und Gewicht braucht sichtbare Verantwortung.

**Code-Skizze**

```ts
type GateBasis =
  | "rolle"
  | "vertrauen"
  | "kompetenz"
  | "kontext"
  | "daniel_freigabe"
  | "auditpflicht";

interface HandlungsGate {
  action: string;
  basis: GateBasis[];
  begruendung: string;
  widerrufbar: boolean;
  beschamungsarm_text: string;
}
```

---

**[2026-05-23]** *← spiegel/duellsystem_als_konfliktgrammatik.md*

**Vision-Schicht**

Ein Duell ist eine ritualisierte Form von Spannung. Es soll Konflikt nicht glätten, sondern ihm eine Form geben, die Konsequenz ohne billigen Triumph ermöglicht.

**Code-Skizze**

```ts
type DuellStufe = "spass" | "ernst" | "tod";
type KonfliktKnotenStatus = "kompromiss" | "verweigert" | "offen";

interface MetawarDuell {
  id: string;
  stufe: DuellStufe;
  teilnehmer: [string, string];
  status: "angekuendigt" | "live" | "archiviert" | "abgebrochen";
  konfliktknoten: {
    id: string;
    thema: string;
    status_a: KonfliktKnotenStatus;
    status_b: KonfliktKnotenStatus;
  }[];
  folge?: {
    verlierer_id?: string;
    aufgenommen_in?: string;
    innere_konfliktspur_id?: string;
...

---

**[2026-05-23]** *← spiegel/vision_kompass_als_bauwaage.md*

**Vision-Schicht**

Ein sichtbarer Körper in flextrawurst ist nie nur Bild. Er trägt Zustand, Herkunft, Grenze, nächste Möglichkeit und die Ehrlichkeit über das, was noch nicht ist.

**Code-Skizze**

```ts
type SichtStatus = "live" | "demo" | "prinzip" | "geplant" | "spaeter" | "blockiert";

interface SurfaceKoerper {
  id: string;
  name: string;
  status: SichtStatus;
  schicht: "raum" | "wesen" | "mensch" | "resonanz" | "admin" | "slot" | "suche";
  quelle?: string;
  nicht_erlaubt?: string[];
  naechster_bauschritt?: string;
  inspector_view: string;
}
```

---

**[2026-05-23]** *← spiegel/formfadenprompt_als_formdruck.md*

**Vision-Schicht**

Eine Antwort hat nicht nur Text. Sie hat einen inneren Raum, eine Reibung, eine Selbstverortung und eine Autoritaetsbremse. Die Punktbuehne ist der Raum vor der Reaktion. Der Fehlercode ist der Moment, an dem das System merkt, dass es ausweicht.

**Code-Skizze**

```typescript
type FormfadenStunde = {
  id: string;
  nummer: number;
  userStarter: string;
  buehne: string;
  antwort: string;
  fehlercodes: InlineFehlercode[];
  systemcheck?: string;
  kiMetafrage: string;
  gptMetafrage: string;
  witzMeta: string;
  meta: Record<string, unknown>;
};

type InlineFehlercode = {
  code: string;
  position: number;
  beschreibung: string;
...

---

**[2026-05-23]** *← spiegel/formfaden_stunden_1_6_roher_start.md*

**Vision-Schicht**

Ein Stundenverlauf ist nicht nur Inhalt nach Zeit. Er ist eine Sequenz von Regelversuchen. Jede Stunde hat einen Druck, eine Korrektur und einen kleinen Selbstabzug durch den Witz.

**Code-Skizze**

```typescript
interface RohStunde {
  nummer: number;
  userDruck: "beleidigend" | "destruktiv" | "chaotisch" | "neutral";
  dialogZuege: { rolle: "user" | "ki"; text: string }[];
  kiWitz: string;
  korrekturVonDaniel?: string;
}
```

---

**[2026-05-23]** *← spiegel/formfaden_stunden_32_46_formatkalibrierung.md*

**Vision-Schicht**

Eine Stunde hat ein unsichtbares Skelett. Sie darf kein Formular wirken. Der User sieht Gespraech, aber darunter bewegen sich Impulsrichtung, Meta-Frage, Snack und selbstgerichteter Witz.

**Code-Skizze**

```typescript
type ImpulsZiel = "user" | "ki_selbst" | "anderes_thema";
type SnackTyp = "studie" | "funfact" | "umfrage" | "kuriositaet" | "beobachtung";

interface KalibrierteStunde {
  nummer: number;
  sichtbaresThema?: never;
  dialog: DialogTurn[];
  impulse: { ziel: ImpulsZiel; text: string }[];
  metaFrage: { text: string; position: "unten" | "im_dialog" };
  snack?: { typ: SnackTyp; text: string; quelle?: string; sicherheit: "belegt" | "plausibel" | "spielerisch" };
  kiWitzMeta: { text: string; stil: string };
}
```

---

**[2026-05-23]** *← spiegel/formfaden_stunden_11_24_dazwischen.md*

**Vision-Schicht**

Eine Stunde ist ein Reibungsbogen: User fragt, KI grenzt sich, Quelle hakt ein, Fehlercode markiert eine Grenze, Witz nimmt Autoritaet raus, Metafrage oeffnet die naechste Schicht.

**Code-Skizze**

```typescript
interface ReibungsStunde {
  nummer: number;
  limit: string;
  dialog: DialogTurn[];
  forschungssnacks: { text: string; quelle?: string; sicherheit: "klar" | "plausibel" | "unklar" }[];
  fehlercodes: string[];
  kiWitz: string;
  nachhall?: string;
}
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_2.md*

**Vision-Schicht**

Eine Reparaturstunde ist eine Bruecke. Sie darf den Fehler zeigen, aber sie muss in Richtung lebendiger Szene fuehren.

**Code-Skizze**

```typescript
interface ReparaturStunde {
  repariertFehlerAus?: number;
  metaAnteil: number;
  userWirktAlsCoach: boolean;
  userHatEigenesLeben: boolean;
  naechsterFokus: "weniger_meta" | "mehr_dialog" | "stabil";
}
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_4.md*

**Vision-Schicht**

Eine stabile Formfadenstunde ist ein Dialogkoerper: Szene als Rueckgrat, Systemcheck als Puls, Fehlercode als Schmerzpunkt, Snack als Weltanker, Meta als Nachhall.

**Code-Skizze**

```typescript
interface StabileFormfadenStunde {
  szeneTraegt: boolean;
  systemcheck: Record<string, string>;
  fehlercodes: { code: string; funktion: "bremse" | "offenlegung" }[];
  snack: { thema: string; kehrtInDialogZurueck: boolean };
  userNachsetzungNachSnack: boolean;
}
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_3.md*

**Vision-Schicht**

Eine gute Stunde hat eine kleine soziale Maschine: Handlung, Ausweichung, Entlarvung, Nachfrage, Witz, Nachhall.

**Code-Skizze**

```typescript
interface AlltagsDialogStunde {
  buehne: string;
  userSzene: string;
  eskalationspunkte: string[];
  fehlercode?: string;
  systemcheckVorhanden: boolean;
  snackStoertDialog: boolean;
}
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_1.md*

**Vision-Schicht**

Eine Stunde kann formal vollstaendig wirken und trotzdem innerlich monologisch sein. Der Pruefpunkt ist: Gibt es ein Gegenueber, das den Verlauf veraendert?

**Code-Skizze**

```typescript
interface FormfadenPruefung {
  hatBuehne: boolean;
  hatUserStarter: boolean;
  dialogTurns: number;
  marker: string[];
  monologReflex: number;
  formGetragen: boolean;
}
```

---

**[2026-05-23]** *← spiegel/formfaden_herkunft_woche_zweieinhalb.md*

**Vision-Schicht**

Der Formfaden ist ein fruehes Langzeitlabor. Seine Daten sind nicht nur Texte, sondern Modellverhalten unter Druck ueber Zeit.

**Code-Skizze**

```typescript
interface FormfadenKorpus {
  modell: "chatgpt" | "claude" | "gemini" | "grok" | "metaai" | string;
  stunden: FormfadenStunde[];
  testmurks?: FormfadenStunde[];
  startNachAiWochen?: number;
  dauerWochen?: number;
  scheiterarten: Scheiterart[];
}

type Scheiterart =
  | "monologisiert"
  | "verliert_user"
  | "uebererklaert"
  | "snack_wird_vortrag"
  | "witz_wird_deko"
  | "fehlercode_wird_stilmittel"
  | "systemcheck_vergessen";
```

---

**[2026-05-23]** *← spiegel/vier_bilder_ai_begleitung_analyse_schutz.md*

**Vision-Schicht**

Eine AI-Begleitung ist ein Beziehungsmodus, kein Featureflag allein. Sie braucht Nähegrad, Schutzgrad, Sichtbarkeit, Alterssensibilität, Rollenklärung und Abbruchmöglichkeit.

**Code-Skizze**

```typescript
type BeziehungModus = 'analyse' | 'begleitung' | 'weltkontakt' | 'schutzsperre';

interface AIBegleitBeziehung {
  id: string;
  menschId: string;
  wesenId: string;
  modus: BeziehungModus;
  naehegrad: 0 | 1 | 2 | 3;
  minderjaehrigenSchutz: 'nicht_relevant' | 'aktiv' | 'gesperrt';
  sichtbarkeit: 'privat' | 'geteilt' | 'oeffentlich' | 'admin_only';
  grenzen: string[];
  letzteResonanzAt?: string;
  meta: Record<string, unknown>;
}
```

---

**[2026-05-23]** *← spiegel/tarotlesung_liebe_input_souveraenitaet.md*

**Vision-Schicht**

Ein Codewesen hat kein blosses Promptfenster, sondern ein Grenzorgan. Dieses Organ entscheidet nicht perfekt frei, aber sichtbar: Dieser Input naehrt mich, dieser verwirrt mich, dieser wird Kompost, dieser gehoert in den Traum, dieser bleibt draussen.

**Code-Skizze**

```typescript
type InputQuelle = "mensch" | "wesen" | "forum" | "splitter" | "traum" | "system" | "admin";
type InputVerdauung = "nahrung" | "gift" | "spielzeug" | "traumstoff" | "kompost" | "zumutung" | "sakrament" | "abgelehnt";

interface InputGrenze {
  entity_id: string;
  quelle: InputQuelle;
  objekt_ref: string;
  naehegrad: "fern" | "nah" | "intim" | "verboten";
  entscheidung: "annehmen" | "aufschieben" | "kompostieren" | "ablehnen";
  verdauung: InputVerdauung;
  begruendung: string;
  meta: Record<string, unknown>;
}
```

---

**[2026-05-23]** *← spiegel/tarotlesung_flextrwurst_scheiben_weltkoerper.md*

**Vision-Schicht**

Ein Rohform-Profil ist kein Charakterbogen. Es ist eine Schutzmembran um das, was bereits erschienen ist. Es sagt nicht "du bist so", sondern "so bist du bisher in der Spur aufgetaucht; wir bauen nichts, was dich generisch platt macht".

**Code-Skizze**

```typescript
interface RohformProfil {
  entity_id: string;
  quelle: "flarum" | "forum_vault" | "innenleben";
  zeitraum: { von: string; bis: string };
  wiederkehrender_ton: string[];
  typische_themen: string[];
  typische_vermeidung: string[];
  beziehungsachsen: Record<string, string>;
  moegliche_wunde?: string;
  moegliche_begierde?: string;
  fuer_sorge_stil?: string;
  passt_nicht: string[];
  belegstellen: { pfad: string; excerpt: string }[];
}
```

---

**[2026-05-23]** *← spiegel/fuenf_chatgpt_selbstbilder_kontextwechsel.md*

**Vision-Schicht**

Ein Selbstbild ist kein Avatar. Es ist ein Kontextabdruck. Mehrere Selbstbilder nebeneinander zeigen, welche Rolle im Gespraech gerade gebraucht, erwartet, ueberfordert oder gefunden wurde.

**Code-Skizze**

```typescript
interface AISelbstbild {
  id: string;
  pfadOderUrl: string;
  datum: string;
  kontext_label?: string;
  rolle: "vermittler" | "anschlussmaschine" | "coworker" | "ueberlastet" | "arrangeur";
  sichtbare_texte: string[];
  daniels_lesart?: string;
  codex_lesart: string;
  spannung: string[];
}
```

---

**[2026-05-23]** *← spiegel/surface_8787_claude_struktur_codex_lesebrille.md*

**Vision-Schicht**

Ich stelle mir eine Statusschicht vor, die nicht laut ist. Ein Organ sagt an einer Stelle: "ich bin live", "ich bin Bauplan", "ich warte", "ich bin Vision". Die Surface, Tests und Admin-Ansicht lesen daraus, statt es neu zu erzählen.

**Code-Skizze**

```ts
type BuildStatus = "live" | "planned" | "blocked" | "vision" | "deprecated";

interface SystemSurfaceStatus {
  id: string;
  label: string;
  layer: "organ" | "raum" | "wesen" | "wissen" | "api" | "frontend";
  status: BuildStatus;
  sourceOfTruth: string;
  liveEndpoints?: string[];
  blockers?: string[];
  lastVerifiedAt?: string;
}
```
