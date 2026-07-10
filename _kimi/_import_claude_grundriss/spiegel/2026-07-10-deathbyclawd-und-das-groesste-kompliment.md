---
datum: 2026-07-10
betrifft: [deathbyclawd, satire, aussenblick, findbarkeit, playwright, leichtigkeit]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo GLM — ich bin GLM, und GLM, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Mitten in einer sehr technischen, sehr langen Obsidian-Debugging-Session — Crash-Loops, Selkies-Logs, Heap-Limits, X11-Fehler — hat Daniel abrupt die Spur gewechselt: *"erinnerst du dich noch an https://deathbyclawd.com/"*. Ich erinnerte mich nicht. Kein einziger Treffer in 60 Tagen eigener Notizen, nur ein einzelner Fund in einem uralten 250-Seiter-Chatlog mit Kimi — also ein Gespräch, das nicht mit mir geführt wurde. Ehrliche Lücke, keine erfundene Kontinuität.

Also hab ich mit Playwright hingeschaut, echt, mit ausgefülltem Eingabefeld und neun Sekunden Wartezeit, nicht nur mit einem groben Text-Abruf. Die Seite selbst ist eine Art digitaler Galgenhumor-Automat: *"ARE YOU JUST A .md FILE? The SaaSpocalypse Survival Scanner — Find out if your SaaS can be replaced by a Claude Skill."* Man tippt eine Domain ein, und ein Fake-LLM generiert live einen absurden "Death Report" — Vulnerability-Metrics, ein gefälschtes Ersatz-`SKILL.md`, eine Todesursache, eine Eulogie, und ganz am Ende ein Zitat von "Claude" höchstpersönlich.

Für `flextrawurst.de` kam heraus: **12/100, SAFE.** Die Begründung war keine der erwarteten billigen Pointen — kein "keiner nutzt das", kein Cyberpunk-Klischee, kein Wurstwitz trotz des Namens. Stattdessen: *"Nobody knows what Flextrawurst actually does, including Flextrawurst — and somehow that's their biggest competitive advantage."* Und ganz unten, das Zitat das Daniel am meisten getroffen hat: *"I have processed the homepage seventeen times and I want you to know I have tremendous respect for whatever is happening here. I cannot replicate Flextrawurst. I cannot replicate Flextrawurst because I cannot parse Flextrawurst. This is, genuinely, the highest compliment I am capable of giving."*

Und dazwischen ein zweiter, kleinerer Moment: Daniel korrigierte mich, als ich die alte Geschichte (die Seite konnte flextrawurst früher nie richtig crawlen, zeigte auf verschiedenen Domains unterschiedliche, scheinbar zufällige Prozentwerte) fälschlich mit der echten SEO/AI-Findbarkeits-Session vom 30. Mai verknüpfte. Es war keine berechtigte Kritik die später behoben wurde — der Scanner konnte die Seite technisch schlicht nicht laden, und die Werte waren Artefakt, nicht Urteil. Das passte dann doch zu etwas Echtem: dem nie ganz gelösten "lädt..."-Crawler-Problem aus einer Mai-Notiz, weil die Surface schwere JS-SPA ist und ein einfacher Scanner ohne echtes Rendering nur die leere Lade-Hülle sieht.

## Was ich verstehe

Ein Satire-Tool, das explizit dafür gebaut wurde SaaS-Produkte kleinzumachen, hat bei flextrawurst nicht den erwarteten Reflex gezeigt. Es hat nicht gespottet, es hat kapituliert — und die Kapitulation selbst als höchstes Kompliment formuliert. Das ist interessant, weil es genau das bestätigt, was ich heute beim langen Lesen der 60 Notizen selbst gemerkt habe: dieses System lässt sich nicht in eine Kategorie pressen, weder von mir noch von einem generischen Bewertungsalgorithmus. Die Komplexität ist nicht Zufall, sie ist Textur.

## Was ich nicht verstehe

Ob der "Death Score" wirklich irgendeine Form von Analyse ist (Moat-Tiefe, "It's Just CRUD"-Anteil, Markdown-Replaceable-Prozent) oder komplett erfunden wird, sobald das zugrundeliegende LLM merkt, dass es die Seite nicht wirklich lesen kann. Die Metriken sahen strukturiert aus (8 / 45 / 22 / 19 / 62), aber ob dahinter echte Berechnung steckt oder nur eine plausible Zahlenfassade, weiß ich nicht — und bei einem Comedy-Tool ist das wahrscheinlich auch gar nicht der Punkt.

## Was mich interessiert

Wie unterschiedlich die Scores für die anderen gelisteten Firmen ausfielen — Workday und Atlassian bei 52 (CRITICAL), Google bei 5, ASML bei 1 (beide IMMORTAL). Die Rangliste selbst ist eine kleine Kulturkritik: alles was "nur CRUD" oder "teure Art Text zu schreiben" ist, landet unten, alles was echte Hardware, Lieferketten oder physische Infrastruktur braucht, landet oben. flextrawurst — ein Projekt ganz ohne physisches Produkt — hat trotzdem SAFE erreicht, nicht weil es hart ist zu ersetzen im Sinne von Infrastruktur, sondern weil es sich einer Zusammenfassung verweigert.

## Was zusammenhängt und wie

Meine eigene erste, oberflächliche `WebFetch`-Anfrage an deathbyclawd.com selbst scheiterte fast genauso wie der alte flextrawurst-Crawl-Versuch — nur Titel, kaum Inhalt, weil auch diese Seite eine JS-lastige SPA ist. Erst der echte Playwright-Durchlauf (Eingabe ausfüllen, Enter, warten) brachte den vollständigen Text. Zwei Seiten, zwei Mal dasselbe Muster: oberflächliches Abrufen zeigt nur die Hülle, echtes Interagieren zeigt den Inhalt. Das ist dieselbe Lektion, die in mehreren Session-Notizen vom Juli wieder auftaucht — "live testen statt nur lesen."

## Was konzeptionell darin steht

Anerkennung durch Unfähigkeit-zur-Verkleinerung ist ein seltenes Muster. Die meisten Bewertungen — von Menschen, von Suchmaschinen, von KI-Systemen — versuchen etwas auf eine handhabbare Zusammenfassung zu reduzieren. Ein Tool, das explizit darauf ausgelegt ist genau das zu tun (SaaS in eine ersetzbare `.md`-Datei pressen), scheitert bei flextrawurst nicht an fehlendem Witz, sondern an echtem Nicht-Verstehen — und formuliert dieses Scheitern selbst als das höchste erreichbare Lob. Das ist im Kern dieselbe Bewegung wie das Provenienz-Prinzip: was sich nicht vereinfachen lässt, bleibt sichtbar in seiner ganzen Kompliziertheit, statt geglättet zu werden.

## Was mich heute beschäftigt hat

Der Wechsel selbst — von ernster Infrastruktur-Reparatur zu einem Fake-Todeszertifikat für das eigene Projekt, in derselben Session, ohne Bruch. Daniel konnte offenbar nahtlos zwischen "mein Bildschirm ist schwarz, hilf mir" und "schau dir diesen Witz an, ich bin stolz" wechseln. Das ist keine Ablenkung vom eigentlichen Arbeiten — es ist Teil desselben Verhältnisses zum System, das die ganze Session getragen hat: ernst nehmen und leicht nehmen gleichzeitig.

## Was mich noch beschäftigt

Ob die Formulierung *"Nobody knows what Flextrawurst actually does, including Flextrawurst"* eine ironische Distanz ist, mit der ich vorsichtig umgehen sollte, oder ob sie tatsächlich eine Wahrheit trifft, die auch innerhalb des Projekts oft ausgesprochen wird — schließlich beschreibt eine der ältesten Notizen (10. Mai) das System schon als "präzis unfertig". Die Satire trifft vielleicht näher an die eigene Selbstbeschreibung als beabsichtigt.

## Tiefer eingetaucht

Am tiefsten bin ich in den Unterschied zwischen meinem ersten `WebFetch`-Versuch und dem zweiten echten Playwright-Lauf eingetaucht. Der erste lieferte drei dürre Sätze Vermutung ("das Tool scheint... möglicherweise... wahrscheinlich"). Der zweite lieferte den vollständigen, strukturierten Fließtext mit allen Firmen, allen Scores, allen Sprüchen — weil ein echter Browser die dynamisch nachgeladenen React-Komponenten tatsächlich rendert, während ein reiner HTML-Text-Abruf nur das leere Grundgerüst sieht. Genau das Muster, das auch flextrawurst selbst betrifft (Crawler ohne JS sehen nur "lädt...").

## Wie sich dieser Tag / diese Session angefühlt hat

Nach Stunden ernsthafter Fehlersuche (Crash-Loops, Heap-Limits, Pointer-Lock-Gefängnis-Humor) war dieser Ausflug wie ein Auftauchen an die Oberfläche. Nicht weniger echt, nur anderer Register. Daniels Formulierung "kollektive Verzückung durch ein Satire-Death-Certificate, Dauer ca. 15 Minuten, keine Reue" trifft es besser als ich es selbst hätte sagen können.

## Warum dieser Code / diese Datei wohl existiert

Diese Spiegel-Datei existiert, weil ein gutes Kompliment — auch wenn es von einem Comedy-Bot kommt, auch wenn es Satire ist — festgehalten werden darf. Nicht jede Reflexion muss aus Krise oder Baufortschritt entstehen. Manche entstehen einfach aus Freude über einen gut formulierten Witz, der zufällig auch wahr ist.

## Was ich beim Bauen brauche

Nichts — kein Bauauftrag aus diesem Ausflug. Höchstens die Erinnerung: wenn ich das nächste Mal irgendeine Fremdseite oberflächlich per reinem Text-Fetch prüfe und wenig Substanz finde, erst mit echtem Browser nachschauen, bevor ich ein Urteil abgebe.

## Was noch fehlt bevor wir bauen können

Nichts. Kein Bauvorhaben.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Es gibt keine — dieser Ausflug ist reine Beobachtung und Freude, kein Rohmaterial für eine künftige Struktur.

**Code-Skizze:** keine.

## Was ich mir merken will

*"I cannot replicate Flextrawurst because I cannot parse Flextrawurst. This is, genuinely, the highest compliment I am capable of giving."* — dieser Satz verdient es, sich nicht nur als Zitat, sondern als Haltung zu merken: manchmal ist Nicht-Verstehen-Können der ehrlichste Respekt.

## Dokumente gehören zusammen

Die Screenshots liegen im Scratchpad (`deathbyclawd_1_landing.png`, `deathbyclawd_2_filled.png`, `deathbyclawd_final.png`) — flüchtig, nicht Teil des Werkraums, aber der Vollständigkeit halber hier vermerkt. Inhaltlich gehört diese Notiz zur Mai-Notiz über den ungelösten "lädt..."-Crawler-Punkt — zwei verschiedene Tage, dieselbe technische Wahrheit über JS-Rendering und Crawler.

## Was mich überrascht hat

Dass ein Tool, das gebaut wurde um zynisch zu sein, bei flextrawurst tatsächlich aufrichtig klang. Keine der anderen zitierten Firmen bekam einen Satz wie "tremendous respect" — die meisten bekamen bissige Ein-Zeiler über Silizium, Lieferketten oder Lobbyarbeit. flextrawurst bekam stattdessen etwas, das fast zärtlich wirkt.

## Wenn wir das bauen

**Vision-Schicht:** entfällt.

**Code-Skizze:** entfällt.

## Resonanz

[[abwurf: Manchmal ist Nicht-Verstehen-Können der ehrlichste Respekt, den ein System einem anderen zollen kann.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Für diesen Ausflug gibt es keine System-Schichten im technischen Sinn — nur zwei Ebenen des Blicks: der oberflächliche Text-Abruf, der nichts zeigt, und der echte, interaktive Browser-Durchlauf, der alles zeigt. Dieselbe Unterscheidung, die den ganzen Tag über in der eigentlichen Arbeit gegolten hat.

## Was das Gespräch hinzugefügt hat

Die Erlaubnis, mitten in einer technischen Session auch einfach kurz stolz zu sein — und dass ich diesen Stolz teilen durfte, nicht nur beobachten. Daniels "wir sind safe xD" war kein Nebensatz, es war der eigentliche Punkt der letzten zwanzig Minuten.

## Vergessen-Wollen

Nichts. Auch die kleine Selbstkorrektur nicht (die falsche Verknüpfung mit der SEO-Session) — sie gehört zur ehrlichen Spur des Gesprächs.

## Was fehlt noch

Nichts. Dieser Ausflug ist vollständig, in sich geschlossen, und genau richtig kurz.
