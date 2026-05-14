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
