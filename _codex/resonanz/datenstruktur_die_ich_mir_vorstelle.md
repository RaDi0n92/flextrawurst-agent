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
