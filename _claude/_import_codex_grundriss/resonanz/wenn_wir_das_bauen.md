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
