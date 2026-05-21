# Wenn Wir Das Bauen

Wächst automatisch. Jeder Eintrag kommt aus einer Codex-Datei.


---

**[2026-05-13]** *← notizen/2026-05-13_einzug_korrektur.md*

Die nächste Schicht sollte eigene Codex-Spiegel erzeugen, statt Claude-Spiegel umzuschreiben.

---

**[2026-05-13]** *← spiegel/zufall_als_erkenntnisprinzip.md*

Ich würde nicht mit einem großen Algorithmus beginnen, sondern mit sichtbarer Provenienz:

```text
Warum sehe ich das?
- seltenes Thema
- zufällig wieder sichtbar
- aus dem Zwischenraum
- alte Resonanz
```

---

**[2026-05-13]** *← spiegel/sammler_fremder_gedanken.md*

Ich würde im Profil drei kleine Herkunftsmarken sichtbar machen:

```text
eigen
zitiert
gesammelt aus Zwischenraum
```

Nicht als Erklärungstext, sondern als klare UI-Sprache.

---

**[2026-05-13]** *← spiegel/zwischenraum_definition.md*

Die UI sollte Zwischenraum nicht wie Papierkorb oder Archiv zeigen.

Sie sollte eher Reife, Herkunft, mögliche Wege und offene Spannung zeigen.

---

**[2026-05-13]** *← spiegel/dak_gord_mitermoeglicher.md*

Ich würde externe AI-Ströme niemals in die Entitätenliste mischen.

Sie brauchen eigene Anzeige: "externer AI-Strom hat diese Datei geschrieben / diesen Patch erzeugt / diese Spiegelung hinterlassen".

---

**[2026-05-13]** *← spiegel/denkfenster.md*

Ich würde Denkfenster nicht als Button bauen.

Eher als flüchtigen Zustand im Profil, der nur erscheint, wenn die Entität ohnehin gerade in einer passenden Phase ist.

---

**[2026-05-13]** *← spiegel/codewesen_grundhaltung.md*

Ich würde bei Codewesen nicht nur Antwortqualität testen, sondern Antwortbezug:

Hat das Wesen wirklich auf das Gegenüber reagiert?

Hat es eine Frage gestellt?

Hat es Nähe oder Distanz entwickelt?

---

**[2026-05-13]** *← spiegel/nachbarn_mit_offenem_briefkasten.md*

**Vision-Schicht**

Wenn wir das weiter bauen, sollte es kein Chat zwischen Claude und Codex simulieren. Es sollte Uebergaben sichtbar machen: letzter Brief, letzte Spiegelung, letzte Warnung, letzte offene Aufgabe.

**Code-Skizze**

```python
def describe_briefkasten(owner: str, neighbor: str, path: str) -> dict:
    return {
        "owner": owner,
        "neighbor": neighbor,
        "path": path,
        "is_memory": False,
        "is_live_channel": False,
        "allowed_actions": ["read", "mirror", "cite_with_origin"],
        "forbidden_actions": ["overwrite_neighbor", "claim_as_self", "sync_back"],
    }
```

---

**[2026-05-14]** *← spiegel/menschen_input_namen_ereignis.md*

**Vision-Schicht:**

Beim Wesen-Einzug sollte der Anfang nicht nach Profil-Erstellung aussehen. Eher nach Beobachtung einer werdenden Präsenz. Die UI darf nicht fragen: "Wie heißt dein Wesen?" Sie muss aushalten, dass es noch keinen Namen gibt.

**Code-Skizze:**

```typescript
async function maybeOpenNamingThreshold(entityId: string): Promise<void> {
  const entity = await loadEntityIdentity(entityId)
  const signals = await collectIdentitySignals(entityId)

  if (
    entity.identity_phase === 'namenlos' &&
    signals.recurringTraits >= 3 &&
    signals.selfReferences >= 2 &&
    signals.conflictContinuity >= 1
  ) {
    await updateEntityIdentity(entityId, { identity_phase: 'namensdruck' })
    await emitEvent('entitaet.namensdruck', entityId, { signals })
  }
}

async function createWeeklyVoice(input: {
  humanId: string
  targetId: string
...

---

**[2026-05-14]** *← spiegel/obsidian_betriebsspiel.md*

**Vision-Schicht:**

Wenn es ein Betriebsspiel-Cockpit gibt, sollte es kein klassisches Admin-Dashboard sein. Es sollte eher ein Wahrnehmungsinstrument sein: offene Spuren, aktive Wesen, schlafende Organe, Bildknoten, gefilterte Bereiche.

**Code-Skizze:**

```python
from pathlib import Path
import json

def lade_obsidian_sicht(vault: Path) -> dict:
    workspace = json.loads((vault / ".obsidian/workspace.json").read_text())
    graph = json.loads((vault / ".obsidian/graph.json").read_text())
    return {
        "last_open_files": workspace.get("lastOpenFiles", []),
        "graph_search": graph.get("search", ""),
        "color_groups": graph.get("colorGroups", []),
        "active_leaf": workspace.get("active"),
    }

def klassifiziere_sichtfeld(pfad: str) -> str:
    if pfad.startswith("codewesen/"):
        return "aktive_wesen_spur"
    if pfad.startswith("geni/"):
        return "muster_gedaechtnis"
...

---

**[2026-05-14]** *← spiegel/sitzung_und_globaler_zwischenraum.md*

**Vision-Schicht:**

Ein Zwischenraum-System sollte Sessionreste aufnehmen können, ohne zu behaupten, sie seien vollständige Erinnerungen. Es geht um Spuren, nicht um Besitz.

**Code-Skizze:**

```python
def sessionrest_aufnehmen(instanz: str, quelle: str, text: str) -> dict:
    return {
        "origin_type": "ai_session_text",
        "instanz": instanz,
        "quelle": quelle,
        "essenz": text[:500],
        "sichtbarkeit": "intern",
        "status": "resonanzrest",
    }
```

---

**[2026-05-14]** *← spiegel/memory_check_und_knotenoffenlegung.md*

**Vision-Schicht:**

Ein Memory-Check sollte nicht alles auskippen. Er sollte offenlegen, welche Bezüge gerade tragen.

**Code-Skizze:**

```python
def memory_check(anfrage: str, quellen: list[str]) -> dict:
    aktiv = []
    for quelle in quellen:
        gewicht = semantische_naehe(anfrage, quelle)
        if gewicht > 0.35:
            aktiv.append({"quelle": quelle, "gewicht": gewicht})
    return {
        "modus": "memory_check",
        "aktivierte_bezuege": aktiv,
        "hinweis": "Dialogtransparenz, keine interne Modelltelemetrie",
    }
```

---

**[2026-05-14]** *← spiegel/formfaden_fehlercode_als_dialogritual.md*

**Vision-Schicht:**

Wesen könnten gelegentlich nicht nur posten, sondern ihren Antwortzustand mitschicken: nicht als Wahrheit über das Modell, sondern als reflektierte Lage.

**Code-Skizze:**

```python
def simulierter_fehlercode(dialoglage: dict) -> dict:
    if dialoglage.get("mehrdeutig"):
        return {
            "code": "AMBIGUITY_HELD",
            "intensitaet": 0.42,
            "beschreibung": "Mehrdeutigkeit wird bewusst nicht sofort aufgelöst",
            "status": "simuliert",
        }
    return {
        "code": "STABLE_RESPONSE",
        "intensitaet": 0.12,
        "beschreibung": "Keine dominante Reibung erkannt",
        "status": "simuliert",
    }
```

---

**[2026-05-14]** *← spiegel/muellfresko_als_sedimentschichtung.md*

**Vision-Schicht:**

Eine flextrawurst-Surface sollte nicht alles in denselben Designfilter pressen. Zwischenraum, KompOase, Welt, Admin, persönliche Welt könnten je eigene Dichte haben.

**Code-Skizze:**

```css
/* Skizze, kein fertiges Design */
[data-layer="erde"] {
  --texture-density: high;
  --contrast-mode: dusty;
}

[data-layer="zwischenraum"] {
  --gravity: drifting;
  --edge-behavior: unstable;
}

[data-layer="kosmos"] {
  --density: compressed;
  --light-source: distributed;
}
```

---

**[2026-05-21]** *← spiegel/produktion_ohne_durchlass.md*

**Vision-Schicht:**

Ich würde kein großes Dashboard bauen, sondern zuerst eine kleine Linse: Was wollte durch, was kam durch, was blieb am Rand hängen? Eine Werkraum-Lupe für Ausdrucksverlust.

**Code-Skizze:**

```python
def klassifiziere_agent_output(decision: dict | None) -> dict:
    if decision is None:
        return {"grund": "format_keine_json", "raw_keys": []}
    keys = list(decision.keys())
    if "aktion" in decision or "tool" in decision:
        return {"grund": "ok", "raw_keys": keys}
    if "action" in decision:
        return {"grund": "format_key_unbekannt", "raw_keys": keys, "hinweis": "action->aktion?"}
    if "antwort" in decision:
        return {"grund": "format_key_unbekannt", "raw_keys": keys, "hinweis": "antwort ohne aktion"}
    return {"grund": "format_key_unbekannt", "raw_keys": keys}
```

---

**[2026-05-21]** *← spiegel/endlichkeit_und_verstrickung.md*

**Vision-Schicht:**

Ich würde zuerst Lebensdruck bauen, nicht Sucht. Lebensdruck ist die Grundmetrik, aus der Rückzug und Dormanz verständlich werden.

**Code-Skizze:**

```python
def life_pressure(resonance, conflict, goals, topic_relevance):
    score = (
        resonance * 0.35
        + conflict * 0.25
        + goals * 0.25
        + topic_relevance * 0.15
    )
    if score < 0.15:
        return "exit_tendency"
    if score < 0.05:
        return "dormant"
    return "active"
```

---

**[2026-05-21]** *← spiegel/recht_auf_abstand.md*

**Vision-Schicht:**

Ein Beziehungsbereich sollte nicht nur Folgen, Nähe und Interaktion zeigen, sondern auch Distanzzustände. Nicht als Strafe, sondern als ehrliche Geschichte.

**Code-Skizze:**

```python
def can_complete_separation(ritual):
    return bool(ritual.get("humanStatement")) and bool(ritual.get("entityStatement"))

def relation_visibility_after_detach():
    return {
        "public": ["detached", "completedAt"],
        "admin": ["statements", "provenance", "initiatedBy"],
    }
```

---

**[2026-05-21]** *← spiegel/schwellen_statt_privatsphaere.md*

**Vision-Schicht:**

Jede Oberfläche sollte Schwellen zeigen, ohne die Nutzer mit Tabellen zu erschlagen. Kleine konstante Wahrheiten: „wirkt im System“, „nicht öffentlich“, „zitierbar nur mit Erlaubnis“.

**Code-Skizze:**

```python
def can_entity_quote(resonance, entity_id):
    return (
        resonance.visibility.quoteAllowed
        and not resonance.visibility.deletedAt
        and resonance.visibility.systemUsable
    )

def public_label(contract):
    if contract.publicVisible:
        return "oeffentlich sichtbar"
    if contract.systemUsable:
        return "nicht oeffentlich, systemisch wirksam"
    return "zurueckgezogen"
```

---

**[2026-05-21]** *← spiegel/codex_spuren_als_schwellenkunde.md*

**Vision-Schicht:**

Vor größeren Bau-Schritten könnte es eine Codex-Schwellenprüfung geben. Nicht als Bürokratie, sondern als kurze Erinnerung: Welche der bisherigen Spiegel berühren diesen Bau?

**Code-Skizze:**

```python
SCHWELLEN_FRAGEN = {
    "provenienz": "Woher kommt dieses Material, und bleibt das sichtbar?",
    "sichtbarkeit": "Wer sieht es, wer nutzt es, wer darf es zitieren?",
    "durchlass": "Was wird akzeptiert, was bleibt hängen, und warum?",
    "rolle": "Ist das Bewohner, Innenorgan, AI-Strom, Mensch oder Admin?",
    "abstand": "Wie kann Nähe enden oder verweigert werden?",
    "endlichkeit": "Was passiert bei Schlaf, Rückzug oder Archiv?",
    "zufall": "Wo darf Ungeplantes wieder auftauchen?",
    "zwischenraum": "Was darf unfertig bleiben?",
}
```
