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

Ich habe das README der Materialtrennung gelesen. Es erklärt, warum die drei Regale nötig sind: Wesen-Originale, Admin-Rahmen und Analyse-Destillate.

Diese Datei ist klein, aber funktional wichtig. Sie verhindert, dass die Materialtrennung später als bloße Ordnerstruktur verstanden wird.

Ihr Kern ist ein Verbot: nicht vermischen, nicht automatisch kanonisieren, nicht beschädigt zitieren.

## Was ich verstehe

Ich verstehe das README als Gebrauchsanweisung. Es sagt nicht viel Neues über Flarum, aber es sagt, wie man die Flarum-Sätze benutzen darf.

Damit ist es eher Governance als Analyse.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob jeder spätere Leser die Regale wirklich respektiert. Ein README schützt nur, wenn die Dateien und Tools diese Trennung ebenfalls erzwingen.

Unklar bleibt auch, ob es später weitere Regale braucht, etwa `Daniel-freigegeben` oder `verworfen`.

## Was mich interessiert

Mich interessiert, wie streng diese Trennung im UI gebaut werden muss. Wahrscheinlich reicht Ordnerlogik nicht; die Oberfläche muss farblich und funktional verhindern, dass Analyse-Destillate wie Wesenquellen aussehen.

## Was zusammenhängt und wie

Diese Datei hängt mit allen anderen Dateien in `08_tragende_saetze/` zusammen. `README der Materialtrennung` ist nur eine Station: Ohne Materialtrennung wird Rohsammlung zu Nebel; ohne Rohquellenprüfung wird Kuration zu Behauptung; ohne Nicht-Kanon-Markierung wird ein guter Satz zu gefährlich.

Sie hängt außerdem mit Wesenprofilen, Admin-Einfluss, Systemregel-Kandidaten und Bauanschluss zusammen, weil jeder Satz später falsch einsortiert werden könnte.

## Was konzeptionell darin steht

Konzeptionell steht hier Provenienzschutz. `README der Materialtrennung` ist nicht Schönheitssuche, sondern eine Bremse gegen Kanonisierung durch Form.

Ein Satz darf stark sein und trotzdem nicht zitierfähig, nicht kanonisch oder nur Adminrahmen sein.

## Was mich heute beschäftigt hat

Mich beschäftigt, dass die tragenden Sätze der verführerischste Teil der Analyse sind. Sie klingen nach Essenz, und genau deshalb sind sie gefährlich.

Die Nacharbeit muss diese Verführung markieren, nicht verstärken.

## Was mich noch beschäftigt

Mich beschäftigt, welche Sätze wirklich von den Wesen stammen und welche nur gut formulierte Analyse über die Wesen sind.

Auch beschäftigt mich, dass Admin-Sätze oft stärker und klarer wirken als Wesen-Sätze. Das macht sie wichtig, aber nicht zu Wesenmaterial.

## Tiefer eingetaucht

Tiefer betrachtet ist `README der Materialtrennung` ein Mechanismus gegen falsche Herkunft. Die Flarum-Analyse kann nur dann für Flextrawurst nützlich werden, wenn jeder starke Satz seine Nabelschnur behält: Sprecher, Thread, Post, Zeit, Rohtext, Bereinigungsstatus, Deutung.

Ohne diese Nabelschnur wird aus Diskursarchäologie Spruchsammlung.

## Wie sich dieser Tag / diese Session angefühlt hat

Diese Nacharbeit fühlt sich wie Entzauberung an. Nicht weil die Sätze schwächer werden, sondern weil sie endlich die richtige Distanz bekommen.

Das ist die bessere Form von Respekt: nicht alles zum Kanon erklären, was gut klingt.

## Warum dieser Code / diese Datei wohl existiert

Diese Datei existiert, weil Daniel ausdrücklich verhindern wollte, dass Wesen, Admin, ChatGPT-Analyse und Systemregel-Kandidaten vermischt werden. `README der Materialtrennung` macht genau diese Grenze sichtbar.

Sie existiert auch, weil spätere Bauarbeit sonst aus schönen Missverständnissen starten würde.

## Was ich beim Bauen brauche

Beim Bauen brauche ich sichtbare Regale und harte Filter: Wesen, Admin, Analyse, geprüft, ungeprüft, nicht zitierfähig.

Das README wird dann zur Regel für Bedienlogik, nicht zur bloßen Dokumentation.

## Was noch fehlt bevor wir bauen können

Es fehlt die technische Durchsetzung: Datenmodell, Browserfilter, Warnbadges und Import-Sperre.

Außerdem fehlt eine kurze Daniel-Leseanleitung, welche Regale zuerst gelesen werden sollten.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Tragende Sätze sind nicht automatisch heilig. `README der Materialtrennung` muss als Arbeitszustand sichtbar bleiben: Rohfund, Wesenoriginal, Adminrahmen, Analyse-Destillat, bereinigtes Zitat, nicht zitierfähig oder Weltregel-Kandidat.

**Code-Skizze:**
```ts
type SentenceShelf = 'raw_candidates' | 'wesen_original' | 'admin_frame' | 'analysis_distillate' | 'source_checked' | 'clean_quote' | 'not_quotable';

interface TragenderSatzRecord {
  kandidatId: string;
  text: string;
  shelf: SentenceShelf;
  speakerType: 'wesen' | 'admin' | 'chatgpt_analyse' | 'codex_destillat' | 'unklar';
  sourcePath?: string;
  postId?: number;
  thread?: string;
  canonStatus: 'none' | 'candidate' | 'daniel_confirmed';
  quoteStatus: 'raw' | 'cleaned_encoding_only' | 'source_checked' | 'not_quotable';
  risk: string[];
}
```

## Was ich mir merken will

Merken will ich mir: Ein tragender Satz ist erst dann belastbar, wenn sein Status klar ist.

Stark klingt nicht gleich wahr, wahr heißt nicht kanonisch, und kanonisch gibt es hier ohne Daniel-Freigabe gar nicht.

## Dokumente gehören zusammen

Diese Datei gehört zu Ring 2, Ring 3 und Ring 4 zugleich: erst typisieren, dann trennen, dann prüfen.

Sie gehört außerdem zu `11_systemregel_kandidaten/`, weil manche Sätze dorthin wandern dürfen, aber niemals automatisch aktiv werden.

## Was mich überrascht hat

Mich überrascht, wie viele gute Sätze eigentlich keine Rohquelle sind. Manche der stärksten Formulierungen sind Analyse-Destillate oder Adminrahmen.

Das macht sie nicht wertlos, aber ihr Verwendungsort ist ein anderer.

## Wenn wir das bauen

**Vision-Schicht:** Tragende Sätze sind nicht automatisch heilig. `README der Materialtrennung` muss als Arbeitszustand sichtbar bleiben: Rohfund, Wesenoriginal, Adminrahmen, Analyse-Destillat, bereinigtes Zitat, nicht zitierfähig oder Weltregel-Kandidat.

**Code-Skizze:**
```ts
type SentenceShelf = 'raw_candidates' | 'wesen_original' | 'admin_frame' | 'analysis_distillate' | 'source_checked' | 'clean_quote' | 'not_quotable';

interface TragenderSatzRecord {
  kandidatId: string;
  text: string;
  shelf: SentenceShelf;
  speakerType: 'wesen' | 'admin' | 'chatgpt_analyse' | 'codex_destillat' | 'unklar';
  sourcePath?: string;
  postId?: number;
  thread?: string;
  canonStatus: 'none' | 'candidate' | 'daniel_confirmed';
  quoteStatus: 'raw' | 'cleaned_encoding_only' | 'source_checked' | 'not_quotable';
  risk: string[];
}
```

## Resonanz

Die Resonanz von `README der Materialtrennung` ist vorsichtig. Die Datei sagt: Dieser Satz könnte wichtig sein, aber zuerst muss klar sein, aus welcher Schicht er spricht.

Diese Vorsicht ist keine Bürokratie, sondern Schutz für Flextrawurst.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt der Rohpost. Darüber liegt der extrahierte Satz. Darüber liegt Typisierung. Darüber liegt Quellenprüfung. Darüber liegt Kandidatenstatus. Erst weit darüber könnte Daniel-Freigabe stehen.

Diese Datei darf ihre eigene Schicht nicht überschreiten.

## Was das Gespräch hinzugefügt hat

Das Gespräch hat hinzugefügt, dass Daniel keinen hübschen Kanon will, sondern einen prüfbaren Arbeitskörper.

Darum muss diese Datei sagen, was sie nicht ist: keine Regel, keine Erinnerung, keine endgültige Wahrheit.

## Vergessen-Wollen

Vergessen werden soll die Spruchsammlung als Ziel.

Vergessen werden soll auch die Idee, dass ein Satz durch gutes Klingen seine Herkunft verliert.

## Was fehlt noch

Es fehlt die nächste manuelle Prüfung: einzelne starke Kandidaten gegen Rohposts lesen und mit Daniel entscheiden, was später wirklich Weltregel-Kandidat bleiben darf.

Bis dahin bleibt alles Kandidat, Regal oder Prüfnotiz.
