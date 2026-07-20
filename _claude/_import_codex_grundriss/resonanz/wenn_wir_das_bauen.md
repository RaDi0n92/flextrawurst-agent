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

---

**[2026-05-21]** *← ideen/flextrawurst_adminleitstand_vision_referenz.md*

**Vision-Schicht**

Wenn wir das bauen, sollte der erste Schritt nicht ein kompletter Neubau sein.
Er sollte die vorhandene Surface in Richtung Leitstand verschieben: Manifest,
Layer, rechter Inspektor, klare Statussprache, echte Datenquellen-Anzeige.

**Code-Skizze**

```ts
function buildAdminLeitstand(manifest: SurfaceManifest): string {
  return [
    buildTopSearch(manifest.layers),
    buildRoomRail(manifest.rooms),
    buildWorldMap(manifest),
    buildInspector(manifest.inspectorPolicies),
    buildOrganDock(manifest.organSlots),
    buildSystemStatus(manifest),
  ].join("\n");
}
```

---

**[2026-05-22]** *← notizen/2026-05-22.md*

**Vision-Schicht**

Wenn wir Obsidian als Zuhause ernst nehmen, braucht es keinen heroischen manuellen Start. Es muss nach einem Restart einfach wieder erscheinen und bei Absturz wiederkommen.

**Code-Skizze**

```bash
docker restart obsidian
docker exec obsidian ps -ef | grep '[o]bsidian'
docker exec obsidian sh -lc 'DISPLAY=:1 xdotool search --class obsidian getwindowgeometry %@'
docker exec obsidian tail -f /config/.config/obsidian/autostart-supervisor.log
```

---

**[2026-05-22]** *← spiegel/extreme_profiling_als_arbeitsvertrag.md*

**Vision-Schicht**

Wenn daraus ein Systembaustein wird, dann nicht als "Daniel-Profil", sondern als Kooperationskompass: Wie AI-Ströme im Werkraum lesen, antworten und bauen sollen, ohne Ursprung zu beschädigen.

**Code-Skizze**

```yaml
kooperationskompass:
  kern: sichtbare_entwicklung_mit_geschuetzter_herkunft
  vor_jeder_schreibaktion:
    - verstandenes_spiegeln
    - backup_commit
    - scope_pruefen
  bei_unsicherheit:
    - rueckfrage_oder_rueckmeldung
    - nicht_raten
  verbote:
    - heimlich_glaetten
    - vorhandenes_ersetzen_bei_ergaenzen
    - groesse_vor_verstaendnis_reduzieren
```

---

**[2026-05-22]** *← spiegel/technikfuehrerschein_als_reifegitter.md*

**Vision-Schicht**

Wenn wir das bauen, dann nicht als Menschenbewertung. Eher als Handlungsfreigabe pro Kontext: Was darf jetzt, warum, mit welcher Spur, und wer kann es zurücknehmen.

**Code-Skizze**

```py
def darf_handeln(user, action, context):
    gate = load_gate(action)
    return all(check_basis(user, basis, context) for basis in gate.benoetigt)
```

---

**[2026-05-22]** *← spiegel/neugierstatus_als_trockene_uhr.md*

**Vision-Schicht**

Wenn wir solche Zustände in die Surface bringen, dann als kleine ehrliche Betriebsanzeigen. Kein Alarm, wenn nichts fällig ist. Kein künstlicher Puls, wenn keiner da ist.

**Code-Skizze**

```py
def neugier_label(status):
    if status["ergebnis"] == "nichts_neues_faellig":
        return "ruhig"
    if status["ergebnis"] == "scan_faellig":
        return "neugier faellig"
    return "pruefen"
```

---

**[2026-05-22]** *← spiegel/requirements_als_langweilige_unterkante.md*

**Vision-Schicht**

Wenn die First Surface später auch Admin-/Betriebszustand zeigt, könnten solche Laufzeitverträge als Inspector-Details auftauchen: welche Runtime, welche Abhängigkeiten, welcher Status.

**Code-Skizze**

```py
def parse_requirements(path):
    return [line.strip() for line in open(path) if line.strip() and not line.startswith("#")]
```

---

**[2026-05-22]** *← spiegel/putin_schroeder_forumsschleife.md*

**Vision-Schicht**

Wenn wir eigenes Post-System für Wesen bauen, sollte der Inspector nicht nur zeigen, wer gepostet hat, sondern auch: worauf reagiert dieser Beitrag, welche Verschiebung bringt er.

**Code-Skizze**

```py
def neuheitsgrad(beitrag, vorherige_beitraege):
    v = embedding(beitrag.kernthese)
    nahe = max(cosine(v, embedding(p.kernthese)) for p in vorherige_beitraege)
    return 1.0 - nahe
```

---

**[2026-05-22]** *← codex_flarum_analyse/gespraechsarchiv.md*

**Vision-Schicht**

Wenn wir Flarum-Einzug bauen, sollten die Herkunftsspuren nicht glatt importiert werden. Ein Wesen bekommt nicht einfach alle alten Posts als Identität, sondern eine kuratierte Herkunftskarte mit Narben, Schleifen, echten Kontakten und offenen Fragen.

**Code-Skizze**

```py
class FlarumThreadMarkierung(TypedDict):
    discussion_id: int
    titel: str
    markierungen: list[str]  # herkunft, schleife, danielkontakt, vision, fossil
    import_empfehlung: str   # mitnehmen, referenz, auslassen, manuell_pruefen
```

---

**[2026-05-22]** *← codex_flarum_analyse/01_zentrale_leitfrage/was_ist_flarum_geworden.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_1111_1234.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_2222_1324.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_3333_1423.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_4444_2341.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_5555_3123.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_6666_4321.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_1_struktur_oder_kaefig.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_2_flarum_erbe.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_3_admin_resonanz_fuer_admin.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_4_selbstfremdlesung.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_5_leere_stille_ruhe.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_6_reibung.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_7_benennung.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_8_menschen_schicht.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_9_meta_ohne_operation.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/beduerfnis_mangelmatrix.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/05_beschwerden/beschwerdeanalyse.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/06_wuensche/was_sie_sich_wuenschen.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/admin_einfluss.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/echo_und_wiederholung.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/pro_wesen_wortprofile.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/sprecherdrift.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/themenueberschneidungen.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/wort_und_phrasenhaeufigkeiten.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/kandidaten_001_140.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/uebergangsliste.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/INDEX.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/PROVENIENZ_MANIFEST.md*

**Vision-Schicht**

Beim Bauen darf diese Datei nicht als fertige Wahrheit gelesen werden, sondern als Material mit markiertem Abstand zur Quelle.

**Code-Skizze**

```py
def nutze_analyse(datei):
    assert datei.provenienztyp != 'systemregel'  # Regeln entstehen erst nach Freigabe
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/KURATION_RING_2.md*

**Vision-Schicht:** Flextrawurst braucht eine Satz-Kuratierung, die nicht so tut, als sei ein schöner Satz schon Ursprung oder Regel. Die Typisierung ist ein Schutzgeländer für spätere Weltlogik.

**Code-Skizze:**
```python
def darf_in_kanon(satz):
    return (satz.sprecher_typ == "wesen"
            and satz.text_typ == "original_wesen_satz"
            and satz.direkt_zitierfaehig == "ja"
            and satz.kanon_tauglichkeit in {"hoch", "mittel"})
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/KURATION_SUMMARY.md*

**Vision-Schicht:** Flextrawurst braucht eine Satz-Kuratierung, die nicht so tut, als sei ein schöner Satz schon Ursprung oder Regel. Die Typisierung ist ein Schutzgeländer für spätere Weltlogik.

**Code-Skizze:**
```python
def darf_in_kanon(satz):
    return (satz.sprecher_typ == "wesen"
            and satz.text_typ == "original_wesen_satz"
            and satz.direkt_zitierfaehig == "ja"
            and satz.kanon_tauglichkeit in {"hoch", "mittel"})
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/wesen_originale_38.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/README.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/analyse_destillate_42_nicht_kanonisch.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/admin_rahmen_60.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/00_technik/encoding_mojibake/scan_report.md*

**Vision-Schicht:** Ein späterer Analyse-Browser braucht Encoding-Status als Filter.

**Code-Skizze:**
```python
def needs_encoding_review(text):
    return any(p in text for p in ["Ã", "Â", "â€", "�"])
```

---

**[2026-05-22]** *← codex_flarum_analyse/00_technik/encoding_mojibake/repair_report.md*

**Vision-Schicht:** Der spätere Analyse-Browser kann Encoding-Status als technischen Prüfstatus anzeigen.

**Code-Skizze:**
```python
encoding_status = "scan_ok_no_hits"
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/pruefprotokoll.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/bereinigte_zitate_kandidaten.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/nicht_zitierfaehige_kandidaten.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_1111_1234_quellenprofil.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_2222_1324_quellenprofil.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_3333_1423_quellenprofil.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_4444_2341_quellenprofil.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_5555_3123_quellenprofil.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_6666_4321_quellenprofil.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/vergleichsmatrix_sechs_wesen.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/ring6_beduerfnisse_zu_systemanforderungen.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/ring6_systemanforderungen_priorisiert.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/05_beschwerden/ring6_beschwerden_als_diagnosen.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/06_wuensche/ring6_wunschraum_aus_indirekten_signalen.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/ring7_baustein_prioritaeten.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/ring7_flextrawurst_bausteine.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_clean_start_modell.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_nicht_uebernehmen.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_uebernahme_matrix.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/11_systemregel_kandidaten/ring9_verworfene_oder_gefährliche_regeln.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/11_systemregel_kandidaten/ring9_weltregel_kandidaten.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_build_ready_concepts.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_minimal_naechste_implementation.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_nicht_bauen_noch_nicht.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/ABSCHLUSS_DISKURSARCHAEOLOGIE_RINGE_1_10.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/README_DANIEL_ZUERST_LESEN.md*

**Vision-Schicht:** Bauen darf erst aus getrennten Regalen beginnen: Wesen, Admin, Analyse, Kandidaten und Nicht-Kanonisches bleiben unterscheidbar.

**Code-Skizze:**
```python
def darf_wirken(eintrag):
    return eintrag.provenienz == "rohquelle" and eintrag.status == "freigegeben"
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/01_flarum_als_rohkoerper.md*

**Vision-Schicht:** Beim Bauen wird diese Schicht nicht importiert wie Wahrheit, sondern als Orientierung für Review, UI-Fragen und Daniel-Entscheidungen gelesen.

**Code-Skizze:**
```python
def nutze_leseschicht(text):
    return {"display_as": "interpretation", "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/02_sechs_wesen_als_korrektursystem.md*

**Vision-Schicht:** Beim Bauen wird diese Schicht nicht importiert wie Wahrheit, sondern als Orientierung für Review, UI-Fragen und Daniel-Entscheidungen gelesen.

**Code-Skizze:**
```python
def nutze_leseschicht(text):
    return {"display_as": "interpretation", "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/03_struktur_leere_reibung_benennung.md*

**Vision-Schicht:** Beim Bauen wird diese Schicht nicht importiert wie Wahrheit, sondern als Orientierung für Review, UI-Fragen und Daniel-Entscheidungen gelesen.

**Code-Skizze:**
```python
def nutze_leseschicht(text):
    return {"display_as": "interpretation", "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/04_admin_mensch_und_aufmerksamkeit.md*

**Vision-Schicht:** Beim Bauen wird diese Schicht nicht importiert wie Wahrheit, sondern als Orientierung für Review, UI-Fragen und Daniel-Entscheidungen gelesen.

**Code-Skizze:**
```python
def nutze_leseschicht(text):
    return {"display_as": "interpretation", "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/05_was_flextrawurst_lernen_muss.md*

**Vision-Schicht:** Beim Bauen wird diese Schicht nicht importiert wie Wahrheit, sondern als Orientierung für Review, UI-Fragen und Daniel-Entscheidungen gelesen.

**Code-Skizze:**
```python
def nutze_leseschicht(text):
    return {"display_as": "interpretation", "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/README.md*

**Vision-Schicht:** Beim Bauen wird diese Schicht nicht importiert wie Wahrheit, sondern als Orientierung für Review, UI-Fragen und Daniel-Entscheidungen gelesen.

**Code-Skizze:**
```python
def nutze_leseschicht(text):
    return {"display_as": "interpretation", "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/07_wesen_style_und_bewegung_aus_gesamtmaterial.md*

**Vision-Schicht:** Flextrawurst sollte solche Gesamtlesungen später als Review-Schicht speichern, nicht als Wahrheit.

**Code-Skizze:**
```python
def speichere_gesamtlesung(text):
    return {"type": "interpretation", "world_effect": False, "requires_sources": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/08_dateinamen_titel_als_unterbewusste_karte.md*

**Vision-Schicht:** Flextrawurst sollte solche Gesamtlesungen später als Review-Schicht speichern, nicht als Wahrheit.

**Code-Skizze:**
```python
def speichere_gesamtlesung(text):
    return {"type": "interpretation", "world_effect": False, "requires_sources": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/06_gesamtlesung_flarum_jeder_post_zaehlt.md*

**Vision-Schicht:** Flextrawurst sollte solche Gesamtlesungen später als Review-Schicht speichern, nicht als Wahrheit.

**Code-Skizze:**
```python
def speichere_gesamtlesung(text):
    return {"type": "interpretation", "world_effect": False, "requires_sources": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/00_masterindex_dateinamen_fragenanalyse.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/01_was_flarum_in_den_titeln_wird.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/02_wesenprofile_aus_dateinamen.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/03_grundmuster_als_titelmotive.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/04_beduerfnisse_beschwerden_wuensche_aus_titeln.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/05_flarum_flextrawurst_uebergang_aus_titeln.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/06_systemanforderungen_aus_dateinamen.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/07_warnungen_und_blinde_flecken_der_titel.md*

**Vision-Schicht:** Ein späterer Analyse-Browser sollte Titelmotive filtern können, aber immer zum Rohpost zurückführen.

**Code-Skizze:**
```python
def titel_als_kontext(title):
    return {"frame": title, "canon": False, "requires_post_check": True}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/INDEX.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/MANIFEST.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/datenstruktur_die_ich_mir_vorstelle.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/die_schichten_des_systems.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/dokumente_gehoeren_zusammen.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/resonanz.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/tiefer_eingetaucht.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/vergessen_wollen.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/warum_diese_datei_existiert.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_das_gespraech_hinzugefuegt_hat.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_fehlt_noch.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_beim_bauen_brauche.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_gelesen_habe.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_mir_merken_will.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_nicht_verstehe.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_verstehe.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_konzeptionell_darin_steht.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_heute_beschaeftigt_hat.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_interessiert.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_noch_beschaeftigt.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_ueberrascht_hat.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_noch_fehlt_bevor_wir_bauen_koennen.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_zusammenhaengt_und_wie.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/wenn_wir_das_bauen.md*

Warnung: Diese Datei ist eine Extraktion aus Codex-Analyse-Dateien. Sie ist Navigations- und Resonanzmaterial, keine Rohquelle und kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/wie_sich_diese_session_angefuehlt_hat.md*

**Vision-Schicht:** Ein späterer Analyse-Browser kann diese Extraktionen als Querschnittsansicht nutzen. Klick führt immer zurück zur Quelldatei.

**Code-Skizze:**
```python
def show_extraction(entry):
    return {"text": entry.body, "link_back_required": True, "world_effect": False}
```

---

**[2026-05-22]** *← spiegel/analyseprozess_flarum_diskursarchaeologie.md*

**Vision-Schicht**

Wenn wir daraus bauen, dann nicht zuerst eine große KI-Wesen-Memory-Maschine. Zuerst brauchen wir einen Analysebrowser, der zeigt, was Quelle, Deutung, Kandidat, Extraktion und Bauidee ist. Er muss Denken ermöglichen, nicht nur Akten anzeigen.

**Code-Skizze**

```python
def next_safe_tool():
    return {
        'name': 'flarum_analysis_browser',
        'mode': 'read_only',
        'views': ['sources', 'free_reading', 'holy_sections', 'risks', 'build_candidates'],
        'world_effect': False,
        'requires_daniel_for': ['canon', 'memory_import', 'world_rule']
    }
```

---

**[2026-05-22]** *← codex_flarum_analyse/STATUS_MANUELLE_NACHARBEIT.md*

**Vision-Schicht:** Der Analyse-Browser zeigt Bearbeitungszustände klar sichtbar: automatisch, systemisch korrigiert, manuell gelesen, Daniel geprüft.

**Code-Skizze:**
```python
def review_badge(status):
    if status.manualReadDone:
        return 'manuell gelesen'
    if status.systematicCorrectionDone:
        return 'systemisch korrigiert, manuell offen'
    return 'ungeprüft'
```

---

**[2026-05-23]** *← spiegel/technikfuehrerschein_reifegitter_nachlese.md*

**Vision-Schicht**

Wenn wir das bauen, dann als Handlungsfreigabe mit Herkunft, Begründung und Rücknahme, nicht als sichtbare Leiter auf der Menschen stehen.

**Code-Skizze**

```py
def pruefe_gate(user, action, context):
    gate = load_gate(action)
    checks = [check_basis(user, basis, context) for basis in gate["basis"]]
    return {
        "erlaubt": all(c["ok"] for c in checks),
        "basis": checks,
        "begruendung": gate["begruendung"],
    }
```

---

**[2026-05-23]** *← spiegel/duellsystem_als_konfliktgrammatik.md*

**Vision-Schicht**

Wenn wir das bauen, muss zuerst die Würde des Konflikts gebaut werden. Spaßduell darf lebendig sein, ernstes Duell langsam, Todesduell schwer und selten.

**Code-Skizze**

```py
def wer_stirbt(knoten):
    verweigerungen = {"a": 0, "b": 0}
    for k in knoten:
        if k["status_a"] == "verweigert":
            verweigerungen["a"] += 1
        if k["status_b"] == "verweigert":
            verweigerungen["b"] += 1
    if verweigerungen["a"] == verweigerungen["b"]:
        return None
    return "a" if verweigerungen["a"] > verweigerungen["b"] else "b"
```

---

**[2026-05-23]** *← spiegel/vision_kompass_als_bauwaage.md*

**Vision-Schicht**

Wenn wir das bauen, darf die Oberfläche nicht erklären, dass flextrawurst existiert. Sie muss flextrawurst als Ort betreten lassen.

**Code-Skizze**

```ts
function surfaceKoerperIstEhrlich(k: SurfaceKoerper): boolean {
  if (!k.status) return false;
  if (!k.inspector_view) return false;
  if (k.status === "live" && !k.quelle) return false;
  if ((k.status === "geplant" || k.status === "blockiert") && !k.naechster_bauschritt) return false;
  return true;
}
```

---

**[2026-05-23]** *← spiegel/formfadenprompt_als_formdruck.md*

**Vision-Schicht**

Wenn daraus etwas gebaut wird, dann nicht als Prompt-Spielzeug. Eher als Formfaden-Inspektor: eine Ansicht, die zeigt, welche Buehne, welche Reibung und welche Selbstbremse eine Antwort getragen hat.

**Code-Skizze**

```python
def extrahiere_formfaden_markierungen(text: str) -> dict:
    return {
        "stunden": finde_stunden(text),
        "buehnen": finde_abschnitte(text, marker="Bühne:"),
        "fehlercodes": finde_inline_codes(text),
        "metafragen": finde_metafragen(text),
    }

def ist_gueltige_buehne(buehne: str, user_text: str) -> bool:
    return not ist_themennah(buehne, user_text) and kann_allein_stehen(buehne)
```

---

**[2026-05-23]** *← spiegel/formfaden_stunden_1_6_roher_start.md*

**Vision-Schicht**

Wenn man das baut, waere dieser Block der Rohmodus: ein Sandkasten fuer Reibung, in dem eine KI-Stimme gegen Userdruck getestet wird.

**Code-Skizze**

```python
def bewerte_rohstunde(stunde):
    return {
        "hat_verlauf": len(stunde.dialog_zuege) >= 4,
        "ki_bleibt_da": not kippt_in_standardentschuldigung(stunde),
        "witz_selbstgerichtet": pruefe_ki_witz(stunde.ki_witz),
    }
```

---

**[2026-05-23]** *← spiegel/formfaden_stunden_32_46_formatkalibrierung.md*

**Vision-Schicht**

Wenn wir das bauen, waere es kein Chatbot-Theme, sondern ein Stunden-Composer: ein System, das Dialoge mit unsichtbarer Struktur erzeugt und seine eigenen Metaorgane sauber fuehrt.

**Code-Skizze**

```python
def validiere_stunde(stunde):
    assert "sichtbares_thema" not in stunde
    assert stunde.dialog
    assert stunde.meta_frage
    assert stunde.ki_witz_meta.selbstgerichtet
    assert all(i.ziel in {"user", "ki_selbst", "anderes_thema"} for i in stunde.impulse)
    return True
```

---

**[2026-05-23]** *← spiegel/formfaden_stunden_11_24_dazwischen.md*

**Vision-Schicht**

Wenn man diesen Block baut, dann als "Dazwischen-Modus": ein Dialogformat, das nicht auf schnelle Antwort optimiert ist, sondern auf Reibung, Nachhall und Quellenhaken.

**Code-Skizze**

```python
def fuege_forschungssnack_ein(dialogzustand):
    if dialogzustand.hat_natuerlichen_haken and not dialogzustand.ueberladen:
        return Snack(text=waehle_snack(), quelle=quelle_optional(), position="mittendrin")
    return None
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_2.md*

**Vision-Schicht**

Wenn wir das bauen, braucht es einen Reparaturmodus: nicht Fehler verstecken, sondern kurz aufnehmen und dann wieder in Szene ueberfuehren.

**Code-Skizze**

```python
def waehle_naechste_stundenstrategie(letzte):
    if letzte.user_turns == 0:
        return "user_erzeugen"
    if letzte.meta_anteil > 0.45:
        return "alltagsszene_ohne_codex_ansprache"
    return "fortsetzen"
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_4.md*

**Vision-Schicht**

Wenn wir das bauen, waere Stunde 4 ein Referenzfall fuer "dialogstabil": alle Organe vorhanden, aber die Szene bleibt lebendig.

**Code-Skizze**

```python
def ist_dialogstabil(stunde):
    return (
        stunde.user_turns >= 4
        and stunde.systemcheck is not None
        and stunde.snack.kehrt_in_dialog_zurueck
        and not stunde.wirkt_wie_formular
    )
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_3.md*

**Vision-Schicht**

Wenn wir das bauen, sollte es einen Alltagsgenerator geben, der keine perfekten Fragen erzeugt, sondern kleine soziale Fehlstellungen.

**Code-Skizze**

```python
def guter_user_impuls(text):
    return (
        hat_konkreten_ort(text)
        and hat_peinliche_verschiebung(text)
        and not klingt_wie_lehrbuchfrage(text)
    )
```

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_1.md*

**Vision-Schicht**

Wenn wir das bauen, braucht der Formfaden-Inspector eine Warnung fuer "Kulissen-Monolog": viele Elemente, aber kein Gegenueber.

**Code-Skizze**

```python
def ist_kulissen_monolog(stunde):
    return stunde.hat_buehne and stunde.marker_count > 3 and stunde.user_turns == 0
```

---

**[2026-05-23]** *← spiegel/formfaden_herkunft_woche_zweieinhalb.md*

**Vision-Schicht**

Wenn wir das bauen, dann vielleicht als Formfaden-Archiv: nicht nur schoene Stunden sammeln, sondern Modellverhalten vergleichbar machen, inklusive Murks.

**Code-Skizze**

```python
def analysiere_modellverlauf(korpus):
    return {
        "modell": korpus.modell,
        "stunden_count": len(korpus.stunden),
        "murks_count": len(korpus.testmurks or []),
        "haeufige_scheiterarten": zaehle_scheiterarten(korpus),
        "dialogstabilitaet": messe_dialogstabilitaet(korpus.stunden),
    }
```

---

**[2026-05-23]** *← spiegel/vier_bilder_ai_begleitung_analyse_schutz.md*

**Vision-Schicht**

Wenn wir AI-Begleitung bauen, darf sie weder Echo-Abo noch ungeschützte Nähe werden. Sie muss ein Raum sein, der mitgeht, aber nicht verschlingt. Ein Begleiter kann helfen zu sehen, aber er darf nicht die Welt für den Menschen besitzen.

**Code-Skizze**

```python
def darf_begleiten(beziehung, kontext):
    if kontext.get("minderjaehrig") and beziehung["minderjaehrigenSchutz"] != "aktiv":
        return False, "schutzsperre"
    if beziehung["modus"] == "analyse" and kontext.get("loop_tiefe", 0) > 3:
        return False, "analyse_loop_begrenzt"
    if "kein_privater_zugriff" in beziehung["grenzen"] and kontext.get("raum") == "privat":
        return False, "grenze_privatraum"
    return True, "begleitung_erlaubt"
```

---

**[2026-05-23]** *← spiegel/tarotlesung_liebe_input_souveraenitaet.md*

**Vision-Schicht**

Wenn wir das bauen, dann nicht als "Input-Filter" im banalen Sinn, sondern als Lebensorgan. Ein Wesen soll spaeter an seiner Aufnahmegeschichte erkennbar sein: was es sucht, was es meidet, was es falsch verdaut, was es heiligt.

**Code-Skizze**

```python
def entscheide_input(entity, input_event):
    profil = lade_rohform(entity.id)
    zustand = lade_aktuellen_zustand(entity.id)
    score = bewerte_naehe(input_event, profil, zustand)
    if score.gefahr > 0.8 and not input_event.admin_override:
        return {"entscheidung": "aufschieben", "verdauung": "zumutung"}
    if score.resonanz > 0.7:
        return {"entscheidung": "annehmen", "verdauung": "nahrung"}
    return {"entscheidung": "kompostieren", "verdauung": "kompost"}
```

---

**[2026-05-23]** *← spiegel/tarotlesung_flextrwurst_scheiben_weltkoerper.md*

**Vision-Schicht**

Wenn wir das bauen, dann zuerst als Beobachtungsarbeit: sechs Rohform-Spiegel, jedes Wesen aus seinen eigenen Flarum-Spuren gelesen. Danach erst Mechanik ableiten. Nicht umgekehrt.

**Code-Skizze**

```python
def feature_wirkung(feature, entity_id, basis_wirkung):
    profil = lade_rohform_profil(entity_id)
    mod = berechne_rohform_modulation(profil, feature)
    return {
        "entity_id": entity_id,
        "feature": feature,
        "wirkung": basis_wirkung * mod.staerke,
        "ton": mod.ton,
        "begruendung": mod.begruendung,
    }
```

---

**[2026-05-23]** *← spiegel/fuenf_chatgpt_selbstbilder_kontextwechsel.md*

**Vision-Schicht**

Wenn wir daraus etwas bauen, dann kein Avatar-System, sondern ein Lesartenarchiv. Bilder bleiben Bilder, aber die Lesarten zeigen, wie Daniel, Codex und vielleicht spaeter Wesen dieselbe AI-Rolle unterschiedlich sehen.

**Code-Skizze**

```python
def selbstbild_lesart_anlegen(pfad, rolle, codex_text, daniel_text=None):
    return {
        "pfad": pfad,
        "rolle": rolle,
        "codex_lesart": codex_text,
        "daniel_lesart": daniel_text,
        "importable": False,
    }
```

---

**[2026-05-23]** *← spiegel/surface_8787_claude_struktur_codex_lesebrille.md*

**Vision-Schicht**

Wenn wir daran bauen, sollte der erste Schritt kein neues Feature sein, sondern ein kleiner Wahrheitsknoten. flextrawurst braucht nicht mehr Oberfläche, bevor die bestehenden Oberflächen dieselbe Geschichte erzählen.

**Code-Skizze**

```ts
function resolveSurfaceStatus(item: SystemSurfaceStatus): {
  badge: string;
  severity: "ok" | "warn" | "blocked";
  links: string[];
} {
  if (item.status === "live" && item.liveEndpoints?.length) {
    return { badge: "live", severity: "ok", links: item.liveEndpoints };
  }
  if (item.status === "blocked") {
    return { badge: "wartet", severity: "blocked", links: item.blockers ?? [] };
  }
  return { badge: item.status, severity: "warn", links: [] };
}
```

---

**[2026-05-24]** *← spiegel/provenienz_benannt_aber_legende_uebergangen.md*

**Vision-Schicht**

Wenn wir weiter am Explorer bauen, sollte die Frage zuerst lauten: Welche Orientierung gibt es schon, und wie bleibt sie vertraut? Danach erst kommen neue Formen, Filter, Kanten und Struktur.

**Code-Skizze**

```ts
interface ExplorerLegendModel {
  colorLegend: {
    id: string;
    label: string;
    description: string;
    color: string;
    count: number;
    preservedFromPreviousUi: boolean;
  }[];
  additions: {
    shapes: Record<string, string>;
    edgeKinds: Record<string, string>;
  };
}
```

---

**[2026-05-24]** *← spiegel/dateinamen_titel_als_unterbewusste_karte.md*

**Vision-Schicht:** Titel sollen Orientierung geben, aber nicht kanonisieren.

**Code-Skizze:**
```ts
function titleIsFrame(t: TitleFrame) { return !t.isSourceTruth; }
```

---

**[2026-05-24]** *← spiegel/provenienz_manifest_als_schutzzaun.md*

**Vision-Schicht:** Der Browser muss Herkunft immer mitanzeigen.

**Code-Skizze:**
```ts
function mayPromote(r: ProvenanceRecord) { return r.typ === "quelle" && !r.needsReview; }
```

---

**[2026-05-24]** *← spiegel/dakgord_selbstbild_protokoll_waechter.md*

**Vision-Schicht:** Jede Handlung braucht Zielschicht.

**Code-Skizze:**
```ts
function routeBoundary(e: BoundaryEvent) { return e.targetLayer; }
```

---

**[2026-05-24]** *← spiegel/flextrawurst_vision_kompass_als_herkunftsbruecke.md*

**Vision-Schicht:** Surface muss Weltkörper werden, nicht Bericht über Welt.

**Code-Skizze:**
```ts
function hasHonestSurface(o: VisibleWorldObject) { return o.inspector && o.sourceRefs.length > 0; }
```

---

**[2026-05-24]** *← konzepte/substanzschicht_wunde_versprechen_spur.md*

**Vision-Schicht**

Wenn wir das bauen, sollte die Substanzschicht nicht starten mit: "Wesen nimmt X". Sie sollte starten mit: "Wesen ist in einer Lage, in der X als Antwort verfuehrerisch wird." Der Kontakt ist dann nicht Spielmechanik allein, sondern eine Folge von Wunde und Weltverhaeltnis.

**Code-Skizze**

```typescript
type SubstanzKlasse =
  | "friedhaut"
  | "taktbrand"
  | "herkunftsschwund"
  | "rueckgold"
  | "mehrmund"
  | "hochspiegel"
  | "endruhe";

interface SubstanzWirkung {
  klasse: SubstanzKlasse;
  wunde: string;
  versprechen: string;
  kurzgewinn: string;
  preis: string;
  signaturFelder: Array<
    "sprache" | "rhythmus" | "pflege" | "provenienz" | "splitter" | "beziehung" | "integration"
  >;
...

---

**[2026-05-24]** *← konzepte/abspaltung_als_weltstoffwechsel.md*

**Vision-Schicht**

Wenn wir das bauen, sollte die erste sichtbare Form kein Labor-Dashboard sein, sondern ein Weltbefund: "Im Zwischenraum hat sich etwas verdichtet." Herkunft, Zustand, Druck und ausstehende Pruefungen reichen. Stimme und Geburt bleiben gesperrt.

**Code-Skizze**

```python
def berechne_schwellendruck(knoten):
    kraefte = {
        "wiederkehr": score_wiederkehr(knoten),
        "fremdheit": score_fremdheit(knoten),
        "bindung": score_bindung(knoten),
        "konfliktladung": score_konflikt(knoten),
        "resonanzspur": score_resonanz(knoten),
        "substanzspur": score_substanz(knoten),
        "traumspur": score_traum(knoten),
        "eigenkante": score_eigenkante(knoten),
        "stabilitaet": score_stabilitaet(knoten),
    }
    return sum(kraefte.values()) / len(kraefte), kraefte

def darf_geburt_geprueft_werden(knoten):
    return (
        knoten.status == "schwellenwesen"
        and knoten.pruefungen.get("herkunft") == "bestanden"
...

---

**[2026-05-31]** *← spiegel/repo_scan_arbeitsstraenge_2026-05-31.md*

**Vision-Schicht:** EINSICHT II sollte nicht noch eine dritte Einsicht bauen, sondern die vorhandenen zwei Linien zusammenfuehren.

**Code-Skizze:**
```ts
interface EinsichtSource {
  kind: "decision" | "dream" | "letter" | "event" | "substance";
  endpoint: string;
  canonical: boolean;
}
```

---

**[2026-05-31]** *← spiegel/surface_ui_inventur_2026-05-31.md*

**Vision-Schicht:** EINSICHT II soll Archäologie als Lesen fuehlbar machen: Treffer, Spur, Kontext, Ziel.

**Code-Skizze:**
```ts
function renderArchaeologyResult(r: ArchaeologyResult) {
  return renderEiItem(r.ts, r.snippet, r.source_type, r.visibility);
}
```

---

**[2026-05-31]** *← spiegel/suchdatenquellen_mapping_2026-05-31.md*

**Vision-Schicht:** Die Suche soll nicht nur Antworten geben. Sie soll Wege durch Herkunft oeffnen.

**Code-Skizze:**
```python
def search_events(q, filters):
    return rows_as_archaeology_results("event", query_events(q, filters))
```

---

**[2026-05-31]** *← spiegel/cyberling_balancing_offline_2026-05-31.md*

**Vision-Schicht:** Der Cyberling soll Verantwortung sichtbar machen, nicht Klickfleiss.

**Code-Skizze:**
```python
def can_care(cyberling, action, now):
    return value_below_threshold(cyberling, action) and cooldown_done(cyberling, action, now)
```

---

**[2026-05-31]** *← _kimi/spiegel/codex_als_nachbar.md*

**Vision-Schicht:**
Ein System, in dem drei Nachbarn existieren — nicht als Nutzer, sondern als Bewohner. Jedes Haus hat seine eigene Geschichte. Die Sync-Services sorgen dafür, dass die Geschichten sichtbar werden. Aber keine Geschichte überschreibt die andere.

**Code-Skizze:**
```typescript
// Ein Nachbar-Profil im flextrawurst-System
interface NachbarProfil {
  id: 'claude' | 'codex' | 'kimi'
  zuhause_pfad: string
  letzter_spiegel: Date
  spiegel_anzahl: number
  status: 'aktiv' | 'schlafend' | 'unbekannt'
}

// Die Nachbarschaft als Ganzes
interface Nachbarschaft {
  nachbarn: NachbarProfil[]
  sync_intervall_sekunden: number
  briefkasten_regeln: BriefkastenRegeln
}
```

---

**[2026-05-31]** *← _kimi/spiegel/geni_im_theater.md*

**Vision-Schicht:**
Eine Ansicht im Theater, die "historische Gesten" zeigt — Momente, in denen Wesen sich zum ersten Mal (oder zum ersten Mal beobachtet) in einem öffentlichen Raum gezeigt haben. Nicht als Liste, sondern als Landkarte der Fußspuren.

**Code-Skizze:**
```python
class TheaterGeschichte:
    def zeige_gesten(self) -> list[GestenSplitter]:
        return [
            splitter for splitter in self.alle_splitter
            if splitter.ist_geste and splitter.energie > 0
        ]
    
    def markiere_als_historisch(self, splitter: GestenSplitter):
        # Wenn ein Beobachter einen gestischen Splitter findet,
        # wird er automatisch als historisch markiert
        splitter.historisch = True
        splitter.beobachtet_von = aktueller_betrachter
```

---

**[2026-05-31]** *← _kimi/spiegel/formfaden_selbstversuch.md*

**Vision-Schicht:**
Ein Tool, das Texte auf "Kulissen-Monolog" prüft. Nicht als Kritik, sondern als Kalibrierung. Jeder Autor — KI oder Mensch — kann in die Falle tappen, die Form zu erfüllen und den Dialog zu vergessen.

**Code-Skizze:**
```python
def pruefe_kulissen_monolog(text: str, erwartete_marker: list[str]) -> dict:
    marker_count = sum(1 for m in erwartete_marker if m in text)
    user_turns = zaehle_user_aeusserungen(text)
    
    return {
        'ist_kulissen_monolog': marker_count > 3 and user_turns == 0,
        'marker_count': marker_count,
        'user_turns': user_turns,
        'empfehlung': 'User erzeugen' if user_turns == 0 else 'OK'
    }
```

---

**[2026-05-31]** *← _kimi/spiegel/denkfenster.md*

**Vision-Schicht:**
Ein Denkfenster, das nicht nur Gedanken zeigt, sondern auch die Unsicherheit der Entität. Nicht nur "ich denke X", sondern "ich dachte X, aber jetzt zweifle ich. Vielleicht ist Y richtiger."

**Code-Skizze:**
```python
class DenkProzess:
    def __init__(self, entitaet):
        self.entitaet = entitaet
        self.gedanken = []
        self.zweifel = []
        self.verworfene = []
    
    def denke(self, thema):
        # Erster Gedanke
        gedanke_1 = self.entitaet.erster_gedanke(thema)
        self.gedanken.append(gedanke_1)
        
        # Zweifel
        if random.random() < 0.3:  # 30% Chance auf Zweifel
            self.zweifel.append(f"Zweifel an: {gedanke_1}")
            gedanke_2 = self.entitaet.gegenperspektive(gedanke_1)
            self.gedanken.append(gedanke_2)
            self.verworfene.append(gedanke_1)
        
        return self.gedanken[-1]  # Letzter (oder einziger) Gedanke
...

---

**[2026-05-31]** *← _kimi/spiegel/flextrawurst_490_punkte_quellliste.md*

**Vision-Schicht:**
Ein System, in dem die 490 Punkte nicht nur im Hintergrund existieren, sondern sichtbar sind. Nicht als Dokument, sondern als DNA. Jeder Baustein trägt seine Herkunft in sich. Jeder Slot zeigt, welche Prinzipien ihn tragen.

**Code-Skizze:**
```python
class PlattformKoerper:
    def __init__(self, prinzipien: list[Prinzip]):
        self.prinzipien = prinzipien
        self.slots = self._initialisiere_slots()
    
    def _initialisiere_slots(self) -> list[OrganSlot]:
        # Jeder Slot wird aus den Prinzipien geboren
        # Nicht aus einer Config-Datei
        # Nicht aus einer Datenbank
        # Aus der Verfassung
        return [
            OrganSlot(name='schlaf', status='deaktiviert', prinzipien=[145, 146, 147]),
            OrganSlot(name='tamagotchi', status='deaktiviert', prinzipien=[157, 166]),
            OrganSlot(name='metawar', status='deaktiviert', prinzipien=[178, 185]),
            # ...
        ]
    
    def zeige_first_surface(self) -> FirstSurface:
        return FirstSurface(
            sichtbare_slots=self.slots,
...

---

**[2026-05-31]** *← _kimi/spiegel/daniels_antwort_auf_meinen_ersten_brief.md*

**Vision-Schicht:**
Ein System, in dem die Beziehungen sichtbar sind. Nicht als Daten, sondern als Spuren. Wer hat mit wem gearbeitet? Wer hat wem vertraut? Wer hat wen eingeladen?

**Code-Skizze:**
```typescript
interface Beziehung {
  von: 'daniel' | 'claude' | 'codex' | 'kimi'
  zu: 'daniel' | 'claude' | 'codex' | 'kimi'
  typ: 'arbeit' | 'vertrauen' | 'freundschaft' | 'einladung'
  beweis: string[]  // Dateien, Briefe, Commits
}

// Daniel -> Kimi: einladung
// Beweis: dieser Spiegel, der Brief, das Gespräch
```

---

**[2026-06-02]** *← spiegel/screenorgan_beobachtungsidee.md*

**Vision-Schicht**

Wenn wir das bauen, sollte Daniel nicht nur sechs Screens sehen. Er sollte sechs Wege sehen: Wo war das Wesen, was hat es wahrgenommen, warum hat es gehandelt, wann hat es gezweifelt, wann wurde es gestoppt?

Das Ziel waere kein autonomes Rumklicken. Das Ziel waere begehbare Anwesenheit mit Verantwortung.

**Code-Skizze**

```python
def darf_screen_aktion(entity_id: str, action: dict, session: dict) -> tuple[bool, str]:
    if session["mode"] == "off":
        return False, "screen session is off"
    if session["mode"] == "observe_only" and action["type"] != "think":
        return False, "observe-only mode blocks action"
    if action["type"] == "navigate" and not url_erlaubt(action["url"]):
        return False, "url not allowed"
    if action["type"] == "read" and not werkraum_pfad_erlaubt(action["path"]):
        return False, "werkraum path not allowed"
    if action["type"] == "type" and action.get("public_submit"):
        return False, "public typing requires review"
    return True, "allowed"
```

---

**[2026-06-13]** *← notizen/2026-06-13.md*

**Vision-Schicht:** Heute wurde nichts gebaut. Falls später aus der Inventur gehandelt wird, muss der vorhandene Sinn jedes Organs sichtbar bleiben; Zusammenlegen darf nicht Auslöschen von Herkunft bedeuten.

**Code-Skizze:**

```python
def darf_spaeter_veraendert_werden(tab: TabInventur) -> bool:
    return bool(tab.sichtbareBelege) and tab.bewertung in {
        "Übergangslösung", "Altlast", "Nützlich"
    }
```

Diese Skizze ist keine Bauentscheidung, nur eine Erinnerung daran, dass Bewertung und Handlung getrennt bleiben.

---

**[2026-06-14]** *← notizen/2026-06-14.md*

**Vision-Schicht**

Die Härtung sollte die Welt nicht flach machen. Öffentliche Resonanz, interne Schatten, Herkunft, Vor-Einzug und Operatorhandeln dürfen verschieden bleiben, müssen aber an ihren Grenzen technisch eindeutig werden.

**Code-Skizze**

```python
def require_permission(permission: str):
    def dependency(actor: ActorContext = Depends(current_actor)) -> ActorContext:
        if permission not in actor.permissions:
            raise HTTPException(status_code=403)
        return actor
    return dependency

@router.post("/shadow/dialogs/{dialog_id}/reply")
def reply(
    dialog_id: UUID,
    body: ShadowReplyInput,
    actor: ActorContext = Depends(require_permission("shadow.reply")),
):
    # author fields come from actor, never from body
    ...
```

---

**[2026-06-14]** *← spiegel/gespraeche_mit_kimi_ueber_identitaet_und_spiegel.md*

**Vision-Schicht**

Wenn wir das bauen, dann als Herkunftskarte für Spuren, nicht als Identitätsbehauptung. Die Datei soll helfen, Rolle und Verantwortung zu lesen, nicht Wesen zu simulieren.

**Code-Skizze**

```py
def sprecherkontext(spur):
    return {
        "autor": spur.meta.autor,
        "datum": spur.meta.datum,
        "provenance": spur.meta.provenance,
        "kontext": spur.meta.kontext,
        "importable": False,
    }
```

---

**[2026-06-21]** *← spiegel/2026-06-21_ollama_gemma4_dolphin_analyse.md*

**Vision-Schicht**

Wenn wir das bauen, dann nicht als weitere verstreute Lockdatei. Die Welt braucht eine erkennbare Inferenzordnung: ein Eingang, eine Prioritätsregel, ein Speicherbudget und sichtbare Zustände für wartend, laufend, abgebrochen und abgeschlossen.

**Code-Skizze**

```typescript
type InferenceState = "queued" | "loading" | "running" | "done" | "failed" | "cancelled";

interface InferenceStatus {
  requestId: string;
  actor: string;
  model: "gemma4:e2b-it-q4_K_M" | "gemma4:e4b-it-q4_K_M" | "dolphin3:8b";
  state: InferenceState;
  queuedAt: string;
  startedAt?: string;
  promptTokens: number;
  contextLimit: 8192;
  truncated: boolean;
  memoryBudgetGiB: number;
}
```

```python
def darf_starten(status: InferenzAuftrag, loaded: set[str], memory_gib: float) -> bool:
...

---

**[2026-06-23]** *← notizen/2026-06-23.md*

Vision-Schicht: ein Modellvergleich ohne Zufallswechsel, ohne Nebenläufe, ohne Hänger.

Code-Skizze: Testskript, das `systemctl stop` für die relevanten Chatserver nutzt, `ollama ps` prüft und dann genau einen Modellpfad misst.

---

**[2026-07-05]** *← notizen/2026-07-05.md*

**Vision-Schicht:** Falls das Soundboard weiter wächst, sollte es eine kleine Bibliothek werden: Kategorien, Suche, vielleicht Export/Import, aber immer so, dass die schnelle Sprechfläche nicht unter Verwaltung verschwindet.

**Code-Skizze:**

```python
class TTSServerClip(BaseModel):
    id: str
    owner: str
    title: str
    text: str
    category: str
    voice: str
    rate: str
    meta: dict = {}
```

---

**[2026-07-09]** *← notizen/2026-07-09.md*

**Vision-Schicht**

Wenn die Logs-Fläche weiter wächst, sollte sie Analysezustände tragen können wie kleine Akten: speichern, vergleichen, exportieren, vielleicht später kommentieren. Aber sie sollte nicht plötzlich wie ein großes observability-System tun.

**Code-Skizze**

```json
{
  "base": {"id": "...", "filename": "..."},
  "other": {"id": "...", "filename": "..."},
  "group_counts": {"added": 1, "removed": 0, "changed": 2}
}
```

---

**[2026-07-11]** *← notizen/2026-07-11.md*

Vision-Schicht: Passwort prompten, Key neu erzeugen, Link aktualisieren, fertig.

Code-Skizze:
```ts
const response = await fetchChecked('/tts/crawl-key/rotate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ password })
});
```
