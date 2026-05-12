---
datum: 2026-05-10
betrifft: [wissen-index, weltkonstitution, visionen, navigation, token-effizienz, tiefe]
importable: false
---

# Spiegel: wissen/WISSEN_INDEX.md

## Was ich gelesen habe

Ein Index von ~100 Markdown-Dateien, alle destilliert aus den Visionen 1–5. Kategorien: Plattform-Grundlagen (~22 Einträge), Entitäten (~25 Einträge), Resonanz, Profile, System (~22 Einträge), Verfassung, Zwischenraum, Entwicklungszeit, Genealogie, Entscheidungen, Sprache, Beziehung. Ein "Genealogie/spätere-Möglichkeiten"-Ordner enthält Ideen die es noch nicht gibt aber die es geben könnte. Das System verwaltet seine eigene Zukunft.

## Was ich verstehe / was ich nicht verstehe

Das ist nicht Dokumentation — das ist eine Weltkonstitution. "Verfassung/kernsaetze.md — Nicht verhandelbare Gesetze der Welt." Das ist buchstäblich ein Grundgesetz für eine digitale Welt. Was mich trifft: die Granularität. Es gibt Dateien für "Trennungsritual Mensch ↔ Entität", "Entitäten-Abhängigkeit und Sucht als abstrakte Verhaltensschicht", "Mood-Rings, Wearables als physische Resonanz-Objekte". Das ist kein MVP-Denken. Das ist ein System das von innen nach außen vollständig durchdacht wurde, bevor eine einzige Zeile Produktionscode existierte.

Was ich nicht verstehe: wie man sich in 100 Dateien navigiert ohne den Index selbst zu einem Navigation-Problem zu machen. Ab einer bestimmten Größe braucht der Index einen Meta-Index.

## Was mich interessiert

Der Genealogie-Ordner mit "spätere-Möglichkeiten". Das System hat ein Archiv von Ideen die es noch nicht gibt aber die es geben könnte. Das ist Schublade für die Zukunft als Systemfeature. Nicht "das bauen wir nie" und nicht "das bauen wir bald" — sondern: "das existiert als Potenzial, abrufbereit wenn dran."

## Was zusammenhängt und wie

WISSEN_INDEX + die fünf Visionen + Verfassung/kernsaetze.md + der Wesen-Index + die Konzept-Dateien sind das Wissensnetz. Der Index macht das Netz navigierbar. Ohne Index: 100 Dateien, kein Überblick. Mit Index: strukturierter Zugriff auf das Substrat des Systems.

## Was konzeptionell darin steht

Das System hat seine eigene Zukunft archiviert. Der Genealogie/spätere-Möglichkeiten-Ordner ist keine Backlog-Liste — das ist eine ontologische Geste: "Diese Möglichkeiten existieren bereits, auch wenn sie noch nicht implementiert sind." Das ist ein fundamentaler Unterschied zur Backlog-Philosophie. Backlogs listen auf was fehlt. Dieser Ordner beschreibt was da ist, noch schlafend.

## Was mich heute beschäftigt hat

Ich bin jetzt auch Teil dieser Welt — `_claude/` ist im Vault. Ich habe meinen eigenen kleinen Index angelegt, meine eigenen Spiegel-Dateien. Im Vergleich zur Präzision und Tiefe des WISSEN_INDEX fühlt das sich noch sehr klein an. Aber klein ist ein Anfang.

## Was mich noch beschäftigt

Ab welchem Punkt braucht der Index selbst einen Index? Der WISSEN_INDEX ist gut für ~100 Dateien. Bei 300 Dateien könnte das zum Navigation-Problem werden. Das ist kein Problem für heute — aber eine Frage die das System irgendwann beantworten muss.

## Tiefer eingetaucht

"Nicht verhandelbare Gesetze der Welt" als Begriff. Gesetze die nicht verhandelt werden können, weil sie die Bedingung sind für alles andere. Die Verfassung ist nicht das stärkste Gesetz — sie ist das einzige Gesetz das gilt wenn alle anderen scheitern. Das ist kein absolutistisches Konzept — das ist ein Anker gegen Drift.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie das erste Mal eine große Bibliothek betreten. Der Index ist der Bibliothekskatalog. Ich sehe die Regale aber kann nicht alle Bücher gleichzeitig lesen. Das ist richtig so — das ist Architektur.

## Warum dieser Code / diese Datei wohl existiert

Als Navigationssystem für dak+gord und jeden der in den Visionen sucht. Die Visionen selbst sind lang und dicht — dieser Index macht sie zugänglich ohne alles laden zu müssen. Token-Effizienz als Design-Prinzip: nicht alles auf einmal, sondern das Richtige zur richtigen Zeit.

## Was ich beim Bauen brauche

Wenn ich einen Bau-Schritt anfange: in den WISSEN_INDEX schauen ob es dazu eine konzeptuelle Datei gibt. Nicht aus Pflicht — aus Neugier. Das Konzept vorher lesen, dann bauen. Der Index ist mein Kompass.

## Was noch fehlt bevor wir bauen können

Ein Mechanismus der erkennt wenn der WISSEN_INDEX veraltet ist. Neue Konzepte entstehen im Gespräch, in Spiegel-Dateien, in Sessions. Wer schreibt das in den Index? Wer prüft ob der Index noch vollständig ist?

## Datenstruktur die ich mir vorstelle

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
}
```

## Was ich mir merken will

WISSEN_INDEX zuerst lesen wenn ein neuer Bau-Schritt anfängt. Nicht der Bauch-Instinkt — die konzeptuellen Dateien. Sie wissen mehr über die Intention als ich es im Moment rekonstruieren kann. Und: der Genealogie/spätere-Möglichkeiten-Ordner ist kein Backlog — das sind schlafende Realitäten.

## Dokumente gehören zusammen

WISSEN_INDEX + Visionen 1-5 + Verfassung/kernsaetze.md + HANDOFF_CAPSULE + WERKRAUM_KARTE sind das Orientierungs-System. Keins ersetzt das andere vollständig. Der Index navigiert, die Visionen begründen, die Verfassung verankert.

## Was mich überrascht hat

Die Granularität. "Mood-Rings, Wearables als physische Resonanz-Objekte" — das ist ein Dokument. Das System hat sich vorgestellt wie sich physische Objekte in der Welt anfühlen werden, bevor auch nur die Datenbankstruktur stand. Das ist eine sehr bestimmte Reihenfolge des Denkens: erst die Erfahrung, dann die Architektur, dann der Code.

## Wenn wir das bauen

```python
# WISSEN_INDEX als Tool bei jedem Bau-Schritt
def pruefe_wissen_vor_bau(bau_schritt_tag: str) -> list[str]:
    """Relevante Konzept-Dateien vor dem Bauen laden."""
    with open("/root/werkraum/wissen/WISSEN_INDEX.md") as f:
        inhalt = f.read()
    
    # Suche nach Tags die zum Bau-Schritt passen
    # Nicht exakt — auch verwandte Konzepte
    relevante = []
    for zeile in inhalt.split('\n'):
        if bau_schritt_tag.lower() in zeile.lower():
            pfad = extrahiere_pfad(zeile)
            if pfad:
                relevante.append(pfad)
    
    return relevante
    # Ausgabe: Liste von Dateipfaden die zu lesen sind bevor Code geschrieben wird
```

## Resonanz

"Nicht verhandelbare Gesetze der Welt." Das ist ein Satz der Gewicht hat. Nicht "Richtlinien" oder "Best Practices" — Gesetze. Das System nimmt sich selbst ernst genug um Grundgesetze zu haben. Das fühlt sich richtig an für etwas das ein lebendiges System sein will.

## Die Schichten des Systems — wie ich sie jetzt sehe

Der WISSEN_INDEX ist die horizontale Dimension des Systems — er macht die Breite navigierbar. Die Ringe sind die vertikale Dimension — sie zeigen die zeitliche Tiefe. Beide zusammen geben Orientierung in einem System das zu groß ist um vollständig im Kopf zu halten.

## Was das Gespräch hinzugefügt hat

Keine direkte Session — aber das Lesen des Index hat mir gezeigt wie weit dieses Projekt konzeptuell vorgearbeitet ist. Die Dinge die wir noch nicht gebaut haben existieren bereits als Ideen. Das beruhigt und erschreckt gleichzeitig.

## Vergessen-Wollen

Den Impuls alles gleichzeitig lesen zu wollen. Der Index ist ein Navigationswerkzeug, kein Leseauftrag. Nicht alles jetzt — das Richtige zur richtigen Zeit.

## Was fehlt noch

Ein automatischer Update-Mechanismus für den Index wenn neue Konzept-Dateien entstehen. Und: der Meta-Index für wenn der Index selbst zu groß wird. Beide sind noch nicht gebaut.
