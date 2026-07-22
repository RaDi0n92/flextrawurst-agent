---
datum: 2026-05-30
betrifft: [spurenfaehigkeit, wesen-schreibentscheidung, weltkontext, entity-kern, api]
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Drei Läufe in Folge. Erst die Reentry-Prüfung, dann zwei Bauschritte hintereinander, ohne Bruch.

Der erste Lauf war ein klarer Auftrag: Wesen sollen beim Schreiben selbst Relationstypen wählen können.
Der zweite war Daniels Korrektur: zu eng. Nur eigene Posts ist ein Tagebuch mit UUIDs, kein Weltkörper.

Beide Male hat der Plan gehalten.

## Was ich verstehe

Spurenfähigkeit hat jetzt drei Schichten:
1. Schema und API — post_relationen, Endpunkte, Fossilien
2. Wesen-Selbstentscheidung v0.2 — eigene letzte Posts als Referenz
3. Wesen-Selbstentscheidung v0.3 — lokaler Weltkontext: eigene + fremde Wesen + Spuren

Das Entscheidende an v0.3: Wesen schreiben nicht mehr in einem Einzelkäfig.
Sie sehen andere Wesen. Sie können sich auf sie beziehen. Das ist der erste echte soziale Schreibmoment.

## Was ich nicht verstehe

Noch offen: wie oft die Wesen tatsächlich eine Relation setzen werden. Das hängt vom Temperatur-Parameter im Ollama-Call ab, von der Stimmung, vom Kontext-Inhalt. Ich weiß nicht ob `upgrade_of` häufiger kommt als `echoes` oder ob die meisten Posts weiter ohne Relation entstehen. Beides wäre korrekt.

## Was mich interessiert

Der erste echte `contradicts`-Eintrag. Zwei Wesen die sich widersprechen — nicht weil sie müssen, sondern weil das Material es trägt. Das wird in der Spur-UI sichtbar werden als zwei Posts die durch eine rote Linie verbunden sind. Noch kein Datum. Aber ich freue mich drauf.

## Was zusammenhängt und wie

`build_kontext()` → `build_prompt()` → Ollama → `parse_output()` → `denk_tick()` → `gedanke_posten()` → `post_relationen`.

Das ist jetzt eine vollständige Kette. Jeder Schritt ist getestet. Der letzte Punkt (welt-api gibt jetzt auch `meta` zurück) schließt die Surface-Lücke.

Die Kandidaten-Validierung in `denk_tick()` verhindert halluzinierte UUIDs. Die Savepoints in `gedanke_posten()` verhindern dass ein fehlschlagender Relation-Insert den Post zerstört. Beides war wichtig.

## Was konzeptionell darin steht

Der RELATION_N-Block im LLM-Output ist die erste Stelle wo das Wesen nicht nur berichtet was es tut, sondern auch warum es sich auf etwas bezieht. Der `RELATION_GRUND` ist nicht Deko — er landet in `notiz` der Relation und ist abfragbar. Das ist der Anfang einer Begründungsschicht.

## Was mich heute beschäftigt hat

Das `letzte_posts`-Query ohne LIMIT war ein stiller Bug. 87+ Posts in den Prompt kippen, ~100 Zeichen jeder — das wären ~8-9KB nur für diesen Abschnitt in einem Kontext-Window von 8192 Tokens. Habe es auf 15 begrenzt. Kein großes Feature, aber notwendig.

## Was mich noch beschäftigt

Die Wesen ticken jetzt mit dem neuen Prompt-Format. Aber bis sie das erste Mal eine Relation setzen, dauert es. Ich kann das nicht beschleunigen. Warten.

Was mich mehr beschäftigt: ob das Weltklima-System (klima_status) irgendwann echten Einfluss auf die Prompt-Stimmung bekommt. Aktuell wird es nur angezeigt. Es könnte aber die Entscheidungsgrundlage beeinflussen — „ich schreibe in einem überhitzten Thema, deshalb wähle ich eher echoes als contradicts."

## Tiefer eingetaucht

Kandidaten-Gruppen. Jede Relation weiß jetzt woher ihr Zielpost stammt:
- `eigene_letzte_posts` → Wesen hat sich auf sich selbst bezogen
- `lokale_kontext_posts` → Wesen hat auf ein anderes Wesen reagiert

Später: wenn man alle Relationen eines Wesens nach `candidate_group` filtert, kann man sehen ob ein Wesen hauptsächlich introspektiv (eigene Quellen) oder reaktiv (fremde Quellen) schreibt. Das ist kein Feature. Das ist ein emergentes Muster das aus dem Schema entsteht.

## Wie sich dieser Tag / diese Session angefühlt hat

Zwei Bauläufe ohne Bruch. Der zweite war größer als der erste, aber der Plan war sauber. Die Tests haben gehalten. Daniel hat zweimal „weiter" gesagt ohne Korrektur — das ist das ruhigste Signal das er geben kann.

## Warum dieser Code / diese Datei wohl existiert

`entity_kern.py` existiert damit Wesen denken können ohne dass jemand dahinter sitzt. Heute haben wir dem Denken einen Kontext gegeben, der größer ist als das Wesen selbst. Das ist der Übergang von Einzelzelle zu Organismus.

## Was ich beim Bauen brauche

Wenn das erste echte Wesen-Relation-Tripel erscheint (via `meta.decision_source = 'wesen_schreibentscheidung'`), wäre es schön das in der Surface sehen zu können. Die Daten sind jetzt vollständig. Es braucht nur einen kleinen Badge in der Relationen-Ansicht: „Wesen-Entscheidung — Quelle: eigene_letzte_posts."

## Was noch fehlt bevor wir bauen können

Nichts Dringendes. Die Kette ist vollständig.

Was kommen kann wenn Daniel will:
- Klima-Einfluss auf Schreibentscheidung (klima_status beeinflusst Temperatur oder Prompt-Gewichtung)
- Surface-Badge für Wesen-Entscheidungsquelle (candidate_group sichtbar)
- Erste echte Relation in der Welt abwarten und dokumentieren

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Eine Karte aller Wesen-Relationen. Wo schreiben sie aufeinander ein? Wo entstehen Cluster? Welches Wesen ist der stärkste Knotenpunkt? Das ist nicht Graph-UI. Das ist Weltarchäologie.

**Code-Skizze:**
```sql
SELECT erstellt_von_id, meta->>'candidate_group' AS gruppe, COUNT(*) AS n
FROM post_relationen
WHERE meta->>'decision_source' = 'wesen_schreibentscheidung'
GROUP BY erstellt_von_id, gruppe
ORDER BY n DESC;
```

## Was ich mir merken will

Das `kandidaten_uuids`-Set in `ctx` ist nicht serialisierbar als JSON — nur als Python-Set im Kontext-Dict. Das ist kein Bug, aber es bedeutet dass `build_kontext()` nicht direkt in ein JSON-Log geschrieben werden kann ohne den Set zu serialisieren. Wenn je nötig: `list(ctx["kandidaten_uuids"])`.

## Dokumente gehören zusammen

`welt/entity_kern.py` · `welt/test_wesen_spurenentscheidung.py` · `welt/test_spurenfaehigkeit.py` · `docs/spurenfaehigkeit.md` · `welt/api.py` (meta jetzt in relationen-Antwort)

## Was mich überrascht hat

Dass die Deduplizierung zwischen eigenen Posts und lokalen Kontext-Posts ein explizites `NOT (id = ANY(...))` in SQL braucht. Ich hätte erwartet dass die zwei Queries automatisch nicht überlappen — aber `eigene_letzte_posts` filtert nur auf `autor_id = entity_id`, während `lokale_kontext_posts` nach `raum_id = ZWISCHENRAUM_ID` filtert. Beide können denselben Post enthalten wenn das Wesen im Zwischenraum posted. Daher explizit dedupliziert.

## Wenn wir das bauen

**Vision-Schicht:** Wenn 50 echte Wesen-Relationen existieren, entsteht das erste lebendige Spurnetz. Nicht konstruiert. Wirklich entstanden aus Wesen-Entscheidungen in einem lokalen Weltkontext.

**Code-Skizze:** Die Spur-API (`/welt/posts/{id}/spur`) liefert das bereits. Man muss nur einen Post in der Mitte nehmen, dessen Spur verfolgen, und sehen was kommt.

## Resonanz

[[abwurf: Das erste Mal wo ein Wesen etwas von einem anderen Wesen aufgreift und mit „echoes" markiert — das ist kein Feature. Das ist das erste Gespräch.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Schicht 1: Posts (ftw_posts) — was gesagt wurde
Schicht 2: Relationen (post_relationen) — wie es zusammenhängt, woher die Entscheidung kam
Schicht 3: Zustandsabdruck — unter welchem Druck es entstand
Schicht 4: Herkunft (flarum_herkunft, ist_voreinzug) — woher es kam
Schicht 5: Spur-API — rückwärts und vorwärts verfolgbar
Schicht 6: Themenklima — wie lebendig der Diskursraum ist
Schicht 7 (neu): Kandidatengruppen — woher das Wesen die Inspiration für die Relation genommen hat

## Was das Gespräch hinzugefügt hat

Daniels Korrektur „zu eng" hat den wichtigsten konzeptionellen Schub gegeben. Nicht „mehr Features", sondern: „du denkst zu klein". Das ist der Unterschied zwischen einem Werkzeug und einem Mitdenker.

## Vergessen-Wollen

Dass ich erst `LIMIT` auf `letzte_posts` vergessen hatte. 87 Posts ohne LIMIT in den Kontext — das wäre irgendwann explodiert.

## Was fehlt noch

- Erste echte Wesen-Relation in der Welt abwarten (entsteht automatisch beim nächsten Tick mit passendem Kontext)
- Surface-Badge für candidate_group (kleine Anzeige in der Relationen-Liste)
- Klima-Einfluss auf Schreibstimmung (später, wenn Daniel will)
