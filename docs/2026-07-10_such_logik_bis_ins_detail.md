# Wie die Flarum-Suche im umgekehrten Neugier-Dienst wirklich funktioniert

Für Daniel, 2026-07-10, als eigene MD "bis ins kleinste Detail" gewünscht.
Gehört inhaltlich zu `2026-07-10_lese_logik_kindgerecht_erklaert.md`, aber
bewusst getrennt, weil hier speziell die Suche im Fokus steht. Code-Stand:
`flarum_api.py` + `codewesen_umgekehrte_neugier.py` von heute.

## Grundprinzip: live gegen die echte Datenbank, nicht gegen den Spiegel

Der umgekehrte Neugier-Dienst liest NICHT aus dem lokalen Vault-Spiegel
(anders als `codewesen_forum_neugier.py`), sondern direkt per SQL gegen die
echte MySQL-Flarum-Datenbank (`flarum_api.py`, `DB_CONFIG`, Host localhost,
Port 3306, Datenbank `flarum`). Schreiben würde über die REST-API laufen,
passiert hier aber nirgends — dieser Dienst schreibt nie nach Flarum.

## Schritt A: die gezielte Suche — `suche_diskussionen()`

```sql
SELECT DISTINCT d.id, d.title, d.comment_count, d.last_posted_at,
       u.username AS last_poster
FROM discussions d
LEFT JOIN users u ON u.id = d.last_posted_user_id
LEFT JOIN posts p ON p.discussion_id = d.id
    AND p.hidden_at IS NULL AND p.is_approved = 1
WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
  AND (d.title LIKE '%<suchbegriff>%' OR p.content LIKE '%<suchbegriff>%')
ORDER BY d.last_posted_at DESC
LIMIT 8
```

Das ist eine reine SQL-`LIKE`-Suche — **kein** Fuzzy-Matching, **keine**
Synonym-Logik, kein Ranking nach Relevanz. Ein Suchbegriff muss entweder
wörtlich im Titel oder wörtlich irgendwo im Inhalt eines (nicht
versteckten/genehmigten) Posts vorkommen. `LIMIT` kommt aus
`KANDIDATEN_PRO_SUCHE = 8` im aufrufenden Code, nicht aus dem
Funktions-Default (der wäre 15).

Wichtig: Weil das Wesen sein Interesse oft in eigenen/inneren Worten oder als
ganze Frage formuliert, kommt genau dieser Wortlaut häufig gar nicht wörtlich
in echten Flarum-Texten vor — die Suche schlägt dann strukturell fehl, nicht
weil "nichts da wäre", sondern weil die Formulierung nicht passt (siehe
Schritt B).

## Der first_post_id-Fund und -Fix (2026-07-10)

Realer Befund, verifiziert direkt gegen die `posts`-Tabelle: **593 von 3765**
sichtbaren Diskussionen (**524** davon mit bestätigt **0** echten Posts) haben
`comment_count > 0`, aber `first_post_id IS NULL` — der Zähler steht, aber es
gibt keinen echten ersten Post mehr dahinter. Das betrifft **~14–16 %** der
gesamten sichtbaren Flarum-Historie, vermutlich gelöschte oder nie
importierte Erstposts mit stehengebliebenem Zähler.

Vorher konnten sowohl `suche_diskussionen()` (über einen Titel-Treffer, der
den fehlenden Post-JOIN nicht betrifft) als auch `stoeber_pool()` und
`zufaellige_diskussionen()` auf so eine Diskussion zeigen. Wählte ein Wesen
sie bewusst aus (z.B. im Stöbern-Trio-Angebot), gab `_lies_post_chunk()` beim
Leseversuch `None` zurück — der Code wechselte daraufhin STILL zum nächsten
Kandidaten, ohne Protokolleintrag, ohne Erklärung. Die tatsächliche
Entscheidung des Wesens verschwand spurlos.

Fix (Commit `5c168c7d`): alle drei Funktionen (`suche_diskussionen()`,
`stoeber_pool()`, `zufaellige_diskussionen()`) filtern jetzt zusätzlich
`AND d.first_post_id IS NOT NULL`. Falls es trotzdem noch passiert (z.B. ein
Post wird NACH dem Laden des Pools gelöscht), schreibt `_phase_lesen_schritt`
seit dem Baustein-20-Nachtrag jetzt wenigstens einen echten Protokolleintrag
("Diskussion #X hatte keinen lesbaren Post mehr ... automatisch zum nächsten
Kandidaten gewechselt, ohne das Wesen zu fragen"), statt den Fall unsichtbar
zu verschlucken.

## Schritt B: 0 Treffer → Übersetzungsversuch — `_alternative_suchbegriffe()`

Nur wenn Schritt A wirklich 0 Treffer liefert (kein Mehraufwand im
Normalfall), wird ein weiterer LLM-Aufruf gemacht: das Wesen wird gebeten,
1–3 einfachere, konkretere Alternativ-Suchbegriffe zu nennen — einzelne
Wörter oder kurze 2-Wort-Gruppen, die eher wörtlich in echten Forumstexten
vorkommen. Jede Alternative wird der Reihe nach einzeln erneut durch Schritt A
(`suche_diskussionen()`) gejagt; beim ersten Treffer wird sofort gestoppt,
keine weiteren Alternativen mehr probiert. Sagt das Wesen "keine", wird gar
nichts probiert.

## Schritt C: immer noch 0 Treffer → drei garantierte Wege

Ohne diesen Baustein hätte eine erfolglose Suche einfach die Sitzung beendet.
Daniels Prinzip dazu (2026-07-09): "das Wesen hat nicht falsch geantwortet,
du musst einen Weg eröffnen." Drei Wege, in dieser Reihenfolge:

1. **Pflegeangebot** (`_pflege_angebot()`) — existiert eigenes
   Container-Material mit mindestens einem echten Eintrag, darf das Wesen
   stattdessen (per Ja/Nein-Frage) etwas darin verschieben oder kopieren.
2. **Stöbern-Trio** (`_frage_stoeber_trio()`, siehe unten) — bis zu zwei
   Angebotsrunden mit drei zeitlich gezielten Diskussionen aus
   `stoeber_pool()`.
3. **Automatischer Zufallsgriff** — lehnt das Wesen beide Stöbern-Runden ab
   (oder antwortet nicht eindeutig), wird ohne weitere Rückfrage zufällig aus
   dem `random`-Teil des schon geladenen Pools gezogen (oder, falls der leer
   sein sollte, aus dem Gesamtpool).

## `stoeber_pool()` im Detail

```sql
-- 8 echte Zufallstreffer (anzahl_random, Standard 8):
SELECT ... FROM discussions d ...
WHERE d.hidden_at IS NULL AND d.is_approved = 1 AND d.first_post_id IS NOT NULL
ORDER BY RAND()
LIMIT 8
```
Plus bis zu drei weitere, gezielt aus der **gesamten zeitlichen Spanne** der
Flarum-Historie gezogen (`MIN(created_at)` bis `MAX(created_at)` über alle
sichtbaren Diskussionen):

- **`frueh`**: ein zufälliger Treffer aus den ersten 7 Wochen ab dem
  ältesten Diskussionsdatum
- **`mitte`**: ein zufälliger Treffer aus einem Fenster von ±3 Tagen um den
  exakten zeitlichen Mittelpunkt zwischen ältester und jüngster Diskussion
- **`spaet`**: ein zufälliger Treffer aus den letzten 2 Wochen vor dem
  jüngsten Diskussionsdatum

Jeder Fund aus diesen drei Fenstern wird nur aufgenommen, wenn seine ID noch
nicht im Zufalls-Achter steckt (keine Dopplung). Der Grund für diese
Konstruktion (Daniel, wörtlich, 2026-07-10): "11 diskussionen vorher schon
ausgewählt werden davon 8 random und eine bewusst innerhalb der ersten 7
wochen von flarum und eine etwa genau zum mittleren zeitpunkt und eine
bewusst innerhalb der letzten 2 wochen" — damit das Stöbern nicht nur zufällig
über die ganze Geschichte streut, sondern garantiert auch alte, mittlere und
neue Abschnitte abdeckt, nicht nur das, was der reine Zufall zufällig trifft.

## `_frage_stoeber_trio()` — wie das Angebot konkret aussieht

Aus dem Pool werden nur die drei Einträge mit `herkunft` `frueh`/`mitte`/
`spaet` herausgefiltert und dem Wesen als benannte Wahl vorgelegt (Titel +
Zeit-Beschriftung, z.B. "aus den ersten Wochen von Flarum"). Antwortformat:
`PFAD: <frueh|mitte|spaet|ablehnen>`. Lehnt das Wesen beim ersten Mal ab, wird
dieselbe Frage ein zweites (letztes) Mal gestellt, mit dem Zusatz-Hinweis,
dass bei erneuter Ablehnung automatisch zufällig gewählt wird. Gibt es noch
keine sinnvolle zeitliche Streuung (z.B. Flarum-Historie noch zu jung), wird
die Funktion übersprungen (`None`).

## Der ältere reine Zufalls-Fallback — `zufaellige_diskussionen()`

Getrennt von `stoeber_pool()`: eine reine `ORDER BY RAND()`-Ziehung ohne
zeitliche Streuung, `LIMIT` Standard 8. Wird NICHT beim "keine Treffer"-Weg
benutzt, sondern innerhalb der Lese-Phase selbst, wenn im Token-Budget-Modus
alle bisherigen Kandidaten durchgelesen sind, das Gesamtbudget aber noch
nicht erreicht ist — dann lädt der Code automatisch neue zufällige
Diskussionen nach, statt die Sitzung vorzeitig zu beenden. Auch hier gilt
seit 2026-07-10 der `first_post_id IS NOT NULL`-Filter.

Grund für `ORDER BY RAND()` statt eines berechneten ID-Bereichs (Kommentar im
Code, real geprüft am 2026-07-09): 79 Lücken zwischen kleinster (ID 6) und
größter (ID 3849) Diskussions-ID, 77 davon allein unterhalb ID 1000 —
vermutlich gelöschte oder nie importierte Altdiskussionen. Ein berechneter
Zufallsbereich wie `range(start, start+limit)` hätte regelmäßig auf gar nicht
existierende IDs gezeigt.

## Der Testflag `--zwinge-leere-suche` — NICHT Teil des echten Betriebs

Wichtig zur Einordnung: `--zwinge-leere-suche` existiert ausschließlich im
separaten Testskript `qualitaetstest_umgekehrte_neugier.py` (Aufruf:
`python3 qualitaetstest_umgekehrte_neugier.py <wesen> [--zwinge-leere-suche]`).
Ist das Flag gesetzt, wird `flarum_api.suche_diskussionen()` im laufenden
Testprozess hart auf eine leere Liste `[]` gezwungen — unabhängig vom echten
Suchbegriff, unabhängig davon ob es echte Treffer gäbe. Zweck: den kompletten
garantierten Pfad (Übersetzung → Pflegeangebot → Stöbern-Trio → Zufall)
zuverlässig durchtesten, ohne auf einen echten Zufallstreffer angewiesen zu
sein. Im normalen Produktionsbetrieb (`haupt_schleife()` in
`codewesen_umgekehrte_neugier.py`) gibt es diesen Zwang nicht — dort läuft
`suche_diskussionen()` immer echt.

## Was die Suche bewusst NICHT kann

- Kein Stemming/Lemmatisierung (z.B. "lesen" findet nicht automatisch
  "gelesen" oder "liest", falls das exakte Wort nicht im Text steht — `LIKE`
  ist reiner Teilstring-Vergleich).
- Keine Synonym-Erkennung — die einzige "Übersetzung" ist der eine
  LLM-Übersetzungsversuch in Schritt B, kein Thesaurus, keine feste Liste.
- Kein Relevanz-Ranking — Ergebnisse sind nach `last_posted_at DESC`
  sortiert (neueste Aktivität zuerst), nicht nach Trefferqualität.
- Keine Berücksichtigung von Groß-/Kleinschreibung als eigene Logik — das
  hängt allein von der MySQL-Spalten-Collation ab, nicht von explizitem Code.
