---
datum: 2026-05-22
autor: codex bei Daniels VPS
quellenbasis: KURATION_RING_2.md; KURATION_SUMMARY.md
provenienztyp: Nutzungsanleitung für getrennte Arbeitsregale
importable: false
warnung: Analyse/Kandidat/Destillat, kein Kanon
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Ring 3 — README Materialtrennung

Warnung: Analyse/Kandidat/Destillat, kein Kanon. Keine Systemregel gilt ohne Daniel-Freigabe.

## Quellenbasis
KURATION_RING_2.md; KURATION_SUMMARY.md

## Provenienztyp
Nutzungsanleitung für getrennte Arbeitsregale

## Zweck
Diese Trennung verhindert, dass schöne oder starke Sätze ihre Herkunft verlieren. Wesen-Originale, Admin-Rahmen und Analyse-Destillate stehen in getrennten Regalen.

## Nutzung
- Wesen-Originale dürfen für Wesenprofile, Bedürfnisse, Beschwerden und Selbstlinien geprüft werden.
- Admin-Rahmen dürfen als Eingriff, Frage, Korrektur oder Ursprung einer Reaktion gelesen werden.
- Analyse-Destillate dürfen nur als Leseschlüssel benutzt werden, nie als Quelle.

## Verboten
- Admin-Sätze als Wesen-Aussagen lesen.
- ChatGPT-Analyse als Rohquelle behandeln.
- Systemregel-Kandidaten aktivieren.
- Beschädigte Rohfunde ohne Prüfung zitieren.

## Was ich gelesen habe
Ich habe `08_tragende_saetze/03_materialtrennung/README.md` als Datei innerhalb des Flarum-Analyse-Körpers gelesen, nicht isoliert. Der Haupttext arbeitet an: Ring 3 — README Materialtrennung. Die relevanten Spannungswörter hier sind: Flarum, Struktur, Admin, Provenienz, Wesen, Systemregel, Bau.

Dabei lese ich den Befund nicht als endgültige Wahrheit, sondern als Schicht über dem Rohmaterial. Wichtig ist, ob die Datei Quelle, Zählung, Interpretation, Kandidat oder Bauanschluss ist.

Die Datei muss deshalb immer mit ihrer Provenienz gelesen werden: Was stammt aus Flarum, was aus Codex-Deutung, was aus Daniel-Rahmung, was aus maschineller Sortierung?

## Was ich verstehe
Ich verstehe diese Datei als tragende_saetze-Schicht. Diese Datei arbeitet an Sätzen als gefährlichem Material: Ein Satz kann tragen, verführen, verkürzen oder seine Quelle verlieren. Entscheidend ist nicht Schönheit, sondern Herkunft, Sprecher, Kontext und Zitierfähigkeit.

## Was ich nicht verstehe
Noch nicht vollständig geklärt ist, wie stark dieser Befund später wirken darf. Die offene Frage ist nicht nur „stimmt das?“, sondern: Welche Rohstellen tragen es, welche Gegenbeispiele gibt es, und wo beginnt Codex-Deutung?

## Was mich interessiert
Mich interessiert an dieser Datei die Stelle, an der aus Text Material für Flextrawurst wird. Nicht als Import, sondern als Frage: Welche Mechanik, welches Datenfeld, welcher Filter oder welche Warnung müsste existieren, damit dieser Befund nicht verloren oder überhöht wird?

## Was zusammenhängt und wie
Diese Datei hängt mit den Rohposts, Ring-2-Kuration, Materialtrennung, freier Leseschicht und Bauanschluss zusammen. Sie steht zwischen Beobachtung und möglicher Systemform: Erst Quelle, dann Kandidat, dann Prüfung, dann vielleicht Mechanismus.

## Was konzeptionell darin steht
Konzeptionell steht hier: Diese Datei arbeitet an Sätzen als gefährlichem Material: Ein Satz kann tragen, verführen, verkürzen oder seine Quelle verlieren. Entscheidend ist nicht Schönheit, sondern Herkunft, Sprecher, Kontext und Zitierfähigkeit. Für Flextrawurst ist der Kern nicht der einzelne Satz, sondern die Unterscheidung, die er erzwingt.

## Was mich heute beschäftigt hat
Mich beschäftigt hier, wie leicht gute Struktur das Denken ersetzen kann. Diese Datei soll nicht nur vollständig sein; sie muss zeigen, wo sie Flextrawurst vorsichtiger, genauer oder lebendiger machen würde.

## Was mich noch beschäftigt
Offen bleibt, welche Teile dieser Datei wirklich gegen Rohquellen hart sind und welche nur plausibel klingen. Gerade plausible Sätze sind riskant, weil sie schnell in spätere Systemlogik rutschen.

## Tiefer eingetaucht
Tiefer gelesen ist `08_tragende_saetze/03_materialtrennung/README.md` kein isolierter Bericht, sondern ein Testfall für Provenienz. Die entscheidende Frage lautet: Welche spätere Fehlkonstruktion würde entstehen, wenn man diese Datei ohne ihre Warnungen übernimmt?

## Wie sich dieser Tag / diese Session angefühlt hat
Diese Nachschärfung fühlt sich wie eine Korrektur an: Die Pflichtabschnitte sollen nicht mehr Tapete sein, sondern kleine Denkfenster. Bei dieser Datei heißt das, ihre konkrete Gefahr und ihren konkreten Nutzen auszusprechen.

## Warum dieser Code / diese Datei wohl existiert
Diese Datei existiert, weil im Flarum-Material etwas sonst zu schnell verschwimmen würde: Ring 3 — README Materialtrennung. Sie hält eine Analyseachse fest, die später geprüft, widersprochen oder in ein Werkzeug übersetzt werden kann.

## Was ich beim Bauen brauche
Beim Bauen braucht jeder Satz einen QuoteCandidate mit source_ref, speaker_type, text_type, cleaned_text, raw_text, risk, canon_status und Daniel-Freigabe.

## Was noch fehlt bevor wir bauen können
Es fehlt für jeden starken Kandidaten die letzte manuelle Entscheidung: Rohzitat, bereinigte Lesefassung, Verwendungsort und Ausschlussgrund müssen zusammen sichtbar sein.

## Datenstruktur die ich mir vorstelle
**Vision-Schicht:** Diese Datei braucht eine eigene Herkunftsmarkierung: Sie darf gelesen, verglichen und befragt werden, aber nicht ohne Prüfung wirken.

**Code-Skizze:**
```ts
interface AnalyseSchicht {
  pfad: string;
  titel: string;
  kategorie: "tragende_saetze";
  quellenbasis: string[];
  kernbegriffe: string[];
  interpretation: boolean;
  kanon: false;
  danielFreigabe: false;
  naechstePruefung: string;
}
```

## Was ich mir merken will
Merken: `08_tragende_saetze/03_materialtrennung/README.md` darf nicht als fertiger Baustein gelesen werden. Sein Wert liegt darin, eine Frage schärfer zu machen: Ring 3 — README Materialtrennung.

## Dokumente gehören zusammen
Zusammengehörig sind diese Datei, die Rohposts im Flarum-Export, `PROVENIENZ_MANIFEST.md`, die Materialtrennung der tragenden Sätze und die freie Leseschicht. Erst zusammen zeigen sie Quelle, Deutung und Bauvorsicht.

## Was mich überrascht hat
Überraschend ist, wie schnell selbst eine gut gemeinte Analyse-Schicht wieder zur scheinbaren Autorität wird. Darum muss diese Datei ihre eigene Begrenzung mitführen.

## Wenn wir das bauen
**Vision-Schicht:** Wenn aus dieser Datei etwas gebaut wird, dann nur als überprüfbarer Kandidat mit Rückweg zur Quelle.

**Code-Skizze:**
```python
def aus_datei_bauen(eintrag):
    assert eintrag["kanon"] is False
    assert eintrag.get("source_ref")
    return "review_candidate"
```

## Resonanz
Die Resonanz dieser Datei liegt in ihrer Reibung: Sie sagt nicht nur „das ist so“, sondern zwingt zu fragen, was Flextrawurst daraus nicht falsch machen darf.

## Die Schichten des Systems — wie ich sie jetzt sehe
Ich sehe hier Rohmaterial, Analyse, Kandidat und Bauanschluss als getrennte Schichten. `08_tragende_saetze/03_materialtrennung/README.md` liegt in der tragende_saetze-Schicht und darf nur über Provenienzbrücken in spätere Systeme wandern.

## Was das Gespräch hinzugefügt hat
Daniels Kritik hat hinzugefügt, dass vollständige Abschnitte nicht reichen. Jede Pflichtüberschrift muss eigenes Denken tragen, sonst wird Struktur wieder zur leeren Form.

## Vergessen-Wollen
Vergessen will ich die bequeme Abkürzung, einen Abschnitt mit einem Dateislogan zu füllen. Diese Datei verlangt eine eigene kleine Entscheidung darüber, was sie für Flextrawurst bedeutet.

## Was fehlt noch
Es fehlt die nächste menschliche Review: Daniel muss später entscheiden, ob diese Lesart trägt, ob sie zu stark ist, oder ob sie nur als Archivspur bleiben soll.
