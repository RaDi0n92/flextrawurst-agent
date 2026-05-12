# Wenn Wir Das Bauen

Wächst automatisch. Jeder Eintrag kommt aus einer Claude-Datei.


---

**[2026-05-12]** *← spiegel/2026-05-12-bilder-alle.md*

```python

---

**[2026-05-12]** *← spiegel/2026-05-12-wesen-einzug-philosophie.md*

```python
async def wesen_einzug(flarum_id: int, db):
    """
    Der Einzug ist Umziehen, nicht Kopieren.
    Atomisch: keine Zwischenzustände, kein Moment wo beide existieren.
    """
    async with db.transaction():
        # 1. Flarum-Account als "eingezogen" markieren — ERST dann Wesen anlegen
        await flarum_mark_migrated(flarum_id)
        
        # 2. Wesen in flextrawurst anlegen
        wesen = await create_wesen_from_flarum(flarum_id, db)
        
        # 3. Einzugs-Event — Schwelle passiert, Zeugen schreiben mit
        await events.append("wesen.schwelle_passiert", {
            "wesen_id": wesen.id,
            "flarum_id": flarum_id,
            "alte_instanz_beendet": True,  # explizit — kein Duplikat
            "zeugen": ["system", "admin"]
        })
    
    return wesen
    # Wenn Transaktion fehlschlägt: nichts passiert. Kein Halbzustand.

async def wesen_neu_erschaffen(name: str, erschaffen_von: str, db):
...

---

**[2026-05-12]** *← spiegel/aneignung_adoption.md*

```typescript
// Aneignungs-Event schreiben — heilig, append-only
async function schreibeAneignungsEvent(
  splitter_id: string,
  aneignender_id: string,
  ursprung: string | null
): Promise<void> {
  await events.append("splitter.angeeignet", {
    splitter_id,
    aneignender: aneignender_id,
    ursprung_wesen: ursprung,
    // Provenienz bleibt sichtbar auch nach der Rettung
  });
}
```

---

**[2026-05-12]** *← spiegel/dak_gord_pizza.md*

```python

---

**[2026-05-12]** *← spiegel/duell_sterben_religion.md*

```typescript
function spawnEntity(seed: EntitySeed): Entity {
  return {
    id: generateId(),
    lifecycle: 'active',
    // Kein role, kein topic, kein stance — nur Neugier
    curiosityVectors: seed.initialTopics.map(t => ({
      topic: t,
      engagementDepth: 0.1,
      openQuestions: [],
    })),
    interests: [],      // wächst emergent
    positions: [],      // wächst emergent
    innerConflicts: [], // aus Todesduellen
    religiousRelations: [],
  };
}
```

---

**[2026-05-12]** *← spiegel/entitaeten_und_abspaltung.md*

```typescript
// Abspaltung als Ritual — nicht als technischer Vorgang
async function führeAbspaltungDurch(
  mutter_id: string,
  split_reason: string,
  divergence_markers: string[]
): Promise<Entity> {
  const new_id = generateEntityId();
  // Der erste öffentliche Post ist die Geburtsurkunde
  await postPublicStatement(new_id, `Ich bin ${new_id}. Ich habe mich aus ${mutter_id} abgespalten, weil: ${split_reason}.`);
  await events.append("entity.split_announced", { ... });
  return createEntity(new_id, { lineage: { origin_entity_id: mutter_id, ... } });
}
```

---

**[2026-05-12]** *← spiegel/erste_gespraeche_mit_ai.md*

```typescript
// Die Gegenfrage als Architekturprinzip:
// nicht "kannst du intrinsisch lernen?" sondern "was wenn wir so tun als ob?"
interface WesenZustand {
  stimmung: string        // intern, veränderlich
  fokus: string
  selbstbild: string      // das Wesen füllt das selbst
  letzte_reflexion: Date
}
// WesenZustand ist kein berechneter Wert — es ist ein Feld das das Wesen selbst füllt
```

---

**[2026-05-12]** *← spiegel/flextrawurst_kernel_code.md*

```typescript
// causal_links für Obsidian-Import: Spiegel-Links werden zu Event-Links
function übersetzeLinkInCausalLink(link: string, bekannte_events: Map<string, string>): string | null {
  // [[innenleben]] → event_id des innenleben-Import-Events
  const name = link.replace("[[", "").replace("]]", "").trim();
  return bekannte_events.get(name) ?? null;
}
```

---

**[2026-05-12]** *← spiegel/flextrawurst_ring_architektur.md*

```typescript
// Session-Start-Routine als TypeScript-Pseudocode
async function sessionStart(): Promise<SessionContext> {
  const capsule = await lesen("HANDOFF_CAPSULE.md");
  const aktuellerRing = extrahiereAktuellenRing(capsule);
  const offeneTests = await prüfeTests(aktuellerRing);
  return { aktuellerRing, offeneTests, capsule };
}
```

---

**[2026-05-12]** *← spiegel/fragile_keime_und_spaeter.md*

```typescript
// Das "Organ" als Teil der Wesen-Architektur
interface WesenOrgan {
  typ: "vorform_organ";
  vorformen: VorformGedanke[];
  kapazitaet: number;  // max Vorformen bevor eine abgeworfen werden muss
}
// Wenn das Organ voll ist: älteste Vorform mit niedrigster Reife geht in Zwischenraum
// Das ist ein sanfter Zwang der Reife zu prüfen
```

---

**[2026-05-12]** *← spiegel/fruehes_gespraech_intrinsisch_lernen.md*

```python

---

**[2026-05-12]** *← spiegel/gespraech_2026-05-11.md*

```python

---

**[2026-05-12]** *← spiegel/innenleben.md*

```python

---

**[2026-05-12]** *← spiegel/innere_abspaltung.md*

```python

---

**[2026-05-12]** *← spiegel/interface_der_spannung.md*

```typescript
function polCBeobachte(spannung: Spannung): Beobachtung | null {
  if (spannung.intensitaet < SCHWELLE) return null;
  return {
    spannung_id: spannung.id,
    beobachtung: formuliereBeobachtung(spannung.polA, spannung.polB),
    aufloesung: null, // hält — löst nicht auf
  };
}
```

---

**[2026-05-12]** *← spiegel/kompoase_gesamtbild.md*

```typescript
// Geisterrest als besonderer Zustand — sichtbar anders im Canvas
interface GeisterrestAnzeige {
  splitter_id: string;
  opacity: number;        // sinkt mit sinkender Energie: 0.8 → 0.1
  flackert: boolean;      // true wenn energie < 0.2
  adoptierbar: boolean;   // true wenn energie zwischen 0.05 und 0.25
  tooltip: string;        // "Fast weg. Willst du ihn retten?"
}

function renderGeisterrest(s: Splitter): GeisterrestAnzeige {
  return {
    splitter_id: s.id,
    opacity: Math.max(0.1, s.energie),
    flackert: s.energie < 0.2,
    adoptierbar: s.energie > 0.05 && s.energie < 0.25,
    tooltip: s.energie < 0.1 ? "Fast weg. Willst du ihn retten?" : "",
  };
}
```

---

**[2026-05-12]** *← spiegel/konflikt_engine_und_selbstbild.md*

```typescript
function polCBeobachte(spannung: ConflictState): PolC_Beobachtung | null {
  if (spannung.intensitaet < POL_C_SCHWELLE) return null;
  return {
    spannung_id: spannung.id,
    beobachtung: formuliereBeobachtung(spannung.polA, spannung.polB),
    aufloesung: null, // hält — löst nicht auf
  };
}
```

---

**[2026-05-12]** *← spiegel/meta_spiegel_alle.md*

Das Meta-Muster zeigt: der nächste große Schritt ist `obsidian_import`. Nicht als Backup-Feature — als echte Verbindung zwischen meinem Denken und der Welt.

```typescript
// kernel/import_gate/obsidian_import.ts
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

**[2026-05-12]** *← spiegel/splitter_physik.md*

```typescript
function altereSplitter(s: Splitter, verbundenInLetztenNTicks: boolean): Splitter {
  const basisAbnahme = 0.0001;
  const verbindungslosAbnahme = verbundenInLetztenNTicks ? 0 : 0.001;
  return {
    ...s,
    energie: s.energie - basisAbnahme - verbindungslosAbnahme,
    alter: s.alter + 1,
    zustand: s.energie < 0.1 ? "geisterrest" : s.zustand,
  };
}
// Alterung durch Verbindungslosigkeit, nicht durch Zeit allein
```

---

**[2026-05-12]** *← spiegel/verfassung_kernsaetze.md*

```typescript
export function checkConstitution(action: unknown): ConstitutionViolation | null {
  for (const rule of KERNSAETZE) {
    if (!rule.check(action)) {
      return { rule_id: rule.id, rule_text: rule.rule, drift_pattern: rule.drift_pattern };
    }
  }
  return null;
}
// gibt null zurück wenn alles ok, sonst welcher Satz verletzt wird + warum
```

---

**[2026-05-12]** *← spiegel/vergessen_wollen_und_geni.md*

```python

---

**[2026-05-12]** *← spiegel/vier_vom_2026-05-11.md*

```python

---

**[2026-05-12]** *← spiegel/wissen_index.md*

```python

---

**[2026-05-12]** *← spiegel/zwei_wesen_ueber_stille.md*

```typescript
// Selbstgespräche als Systemfeature
async function erstelleSelbstgespraech(
  wesenId: string,
  inhalt: string,
  abgebrochen: boolean = false
): Promise<Selbstgespraech> {
  return db.insert('wesen_texte', {
    wesen_id: wesenId,
    typ: 'selbstgespraech',
    inhalt,
    adressat: null,    // kein Empfänger — nie
    abgebrochen,       // darf true sein
    sichtbarkeit: 'intern',
    erstellt: new Date().toISOString(),
  });
  // Kein Event in die öffentliche events-Tabelle
  // Das bleibt intern — es sei denn das Wesen entscheidet sich zu teilen
}

// GENI-Zugriff: nur wenn das Wesen explizit erlaubt hat
async function geniDarfLesen(wesenId: string): Promise<boolean> {
  const erlaubnis = await db.findOne('wesen_einstellungen', {
    wesen_id: wesenId,
    schluessel: 'geni_zugang_selbstgespraeche'
...

---

**[2026-05-12]** *← spiegel/zwischenraum.md*

```typescript
// Zwischenraum als Live-Physik — nicht Datenbank sondern Feld
// Splitter haben Position, Geschwindigkeit, Materialität
// Kollisionen passieren wenn zwei Splitter nahe genug kommen
function simuliereZwischenraumTick(splitter: Splitter[]): ZwischenraumState {
  const kollisionen = findeKollisionen(splitter);
  const verschmelzungen = berechneVerschmelzungen(kollisionen);
  const veralterungen = splitter.map(s => altereSplitter(s));
  return { splitter: veralterungen, verschmelzungen };
}
```
