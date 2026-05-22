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
