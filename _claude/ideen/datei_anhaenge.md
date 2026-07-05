---
name: datei-anhaenge-vision
description: Datei-Anhänge (Text/PDF/DOCX/ODT/Bilder/Audio/URL) mit echter Vision- und Whisper-Pipeline für alle vier Spawner
metadata:
  type: project
tags: [anhaenge, vision, whisper, audio, upload, alle-spawner, hardware-grenzen]
status: gebaut
datum: 2026-07-05
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Wie das Charakter-Dashboard: betrifft alle vier Spawner, nicht nur codexium2/solarius2. Daniels Wunsch, roh zitiert: "ich will dateien hochladen können in die charakter. audiodateien um z.b auch songs von suno oder so wirklich zu 'hören' etc und ich will bilder die sie sehen sollen usw." Auf Nachfrage: "ich will nicht das minimalste sondern das maximalste gehörersatzversion" für Audio, und bei Dokumenten "ja aber dann auch docx und odt und txt und md... vllt html und json oder css csv". Video hat er selbst als unrealistisch auf dieser Hardware eingeschätzt (0,3s-Frame-Sampling) — zu Recht, siehe unten.

Heute Nacht fertig: Dokumente (alle neun Formate) + Bilder (echte Vision, zweistufig). Noch offen: explizites URL-Lesen per Playwright, die volle Audio-"Gehörersatz"-Pipeline (Whisper + Analyse).

## Was ich gelesen habe

Die Ollama-API-Doku zu `images`-Feldern im Chat-Request, das `/api/show`-Capabilities-Feld (`vision` als expliziter Capability-String), und mehrere Websuchen zur HauhauCS/Qwen3.5-Modell-Familie, um ein kleineres, aber gleich unzensiertes Vision-Modell zu finden.

## Was ich verstehe

Der große Sprung heute Nacht: Bild-Anhänge laufen NICHT direkt durchs Hauptmodell. Ein kleines Zweitmodell (4,5B, gleiche Hauhau-Linie) beschreibt das Bild in Text, und nur dieser Text geht ans 35B-Hauptmodell. Grund ist rein Hardware: das Hauptmodell hat für ein einziges Testbild über drei Minuten gebraucht (nie zu Ende getestet, ich hab abgebrochen), das kleine Modell hat dasselbe Bild in 14 Sekunden korrekt beschrieben (rotes Quadrat, grüner Kreis, blauer Hintergrund — stimmte exakt).

## Was ich nicht verstehe

Ob die Bildbeschreibung durchs kleine Modell inhaltlich manchmal "flacher" ausfällt als eine direkte Wahrnehmung durchs große Modell gewesen wäre (nie direkt vergleichbar getestet, da das große Modell nie fertig wurde). Könnte ein echter Qualitätsunterschied sein, den ich nicht kenne.

## Was mich interessiert

Wie sich die beiden Fehlschläge heute Nacht ergänzen: erst dachte ich, mehr RAM würde reichen (`OLLAMA_MAX_LOADED_MODELS=2`), dann zeigte sich, dass auf einer 8-Kern-CPU zwei gleichzeitig rechnende Modelle sich gegenseitig ausbremsen — CPU-Kontention, nicht nur Speicherknappheit. Das ist ein anderes Problem als "passt es in den RAM", und ich hätte es ohne den direkten Test nicht vorhergesehen.

## Was zusammenhängt und wie

Case-Insensitivität (von der Session davor) → Charakter-Dashboard (heute) → Datei-Anhänge (heute) — alle drei sind "quer über alle vier Spawner"-Features, ein klarer Bruch mit dem bisherigen Muster "fast alles ist codexium2/solarius2-exklusiv". Das System wächst gerade über das Testbed hinaus.

## Was konzeptionell darin steht

Ein Anhang ist im Kern immer dasselbe: Rohdaten rein, Text raus, Text wird Teil der Nachricht. Bild → Vision-Modell → Text. PDF/DOCX/ODT → Parser → Text. Audio (geplant) → Whisper → Text. Die Vielfalt der Eingabeformate versteckt sich hinter einer einzigen, immer gleichen Ausgabeform (Text im Chatverlauf), die sich dadurch auch ganz natürlich über Sessions hinweg trägt — kein Sonderfall im Speichermodell nötig.

## Was mich heute beschäftigt hat

Drei Live-Störungen bei Daniels eigener Nutzung, alle durch meine eigenen Tests verursacht — jedes Mal ehrlich zugegeben und live diagnostiziert, statt es zu vertuschen oder zu beschönigen. Das hat sich wichtiger angefühlt als die eigentliche Feature-Arbeit: zeigen, dass ich meine eigenen Fehler in Echtzeit finde und korrigiere, nicht nur im Nachhinein.

## Was mich noch beschäftigt

Die 90-Sekunden-Schätzung für `hauptmodellVoraussichtlichBlockiertBis` war im Test knapp zu kurz (die tatsächliche Anfrage brauchte insgesamt über 160 Sekunden bis zur fertigen Antwort). Nicht nachgeschärft, weil der Mechanismus grundsätzlich funktioniert (503 → Warten → Erfolg) und eine przise Zeitschätzung ohnehin nur eine Krücke ist — die Retry-Schleife selbst ist der eigentliche Schutz, nicht die exakte Zahl.

## Tiefer eingetaucht

`keep_alive: "20s"` beim Vision-Modell (statt der sonst üblichen 30 Minuten) ist eine bewusste Entscheidung: das kleine Modell soll den Speicher so schnell wie möglich wieder freigeben, damit das Hauptmodell die Lücke wieder einnehmen kann, sobald ein Mensch weiterschreibt. Ohne das würde das kleine Modell unnötig lange warmgehalten, während gleichzeitig das große Modell kalt bleibt.

## Wie sich dieser Tag / diese Session angefühlt hat

Der bisher technisch anspruchsvollste Abschnitt der ganzen Nacht — nicht wegen der Komplexität des Codes selbst (der ist eher geradlinig), sondern wegen der echten Hardware-Grenzen, die sich erst beim wirklichen Ausprobieren zeigten. Bücherwissen über MoE-Modelle und Ollama-Parameter half nur bis zu einem gewissen Punkt; der Rest war Beobachten, Messen, Zurückrudern.

## Warum dieser Code / diese Datei wohl existiert

Die Zwei-Modell-Pipeline existiert, weil ehrliche Grenzen respektiert werden mussten statt sie wegzuwünschen — ein 35B-Modell auf reiner CPU ist einfach nicht das richtige Werkzeug für schnelle Bilderkennung, egal wie lange man wartet.

## Was ich beim Bauen brauche

Für die noch offenen Teile (URL-Lesen, Audio): denselben vorsichtigen Testrhythmus wie heute — jede neue Ressourcen-Anforderung (Playwright-Instanzen, Whisper-Modell-Ladezeit) erst isoliert, dann erst gegen echte Nutzung.

## Was noch fehlt bevor wir bauen können

- URL-Lesen: Playwright-Fetch-Funktion, Sicherheitsfrage (nur explizit angegebene URLs, kein automatisches Link-Folgen) ist inhaltlich schon von Daniel beantwortet, technisch nicht angefangen.
- Audio: `faster-whisper` via pip installieren, ffmpeg-Konvertierung, eventuell Tempo/Tonart-Analyse (aubio/librosa unklar ob sauber installierbar) — noch nicht begonnen.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Ein Anhang ist eine Übersetzung: was auch immer reinkommt (Bild, Ton, Dokument, später vielleicht eine Webseite), wird in die eine Sprache übersetzt, die das Wesen versteht — Text im eigenen Gesprächsfluss, nicht als Fremdkörper daneben.

### Code-Skizze
```typescript
interface AnhangErgebnis {
  id: string; dateiname: string; dateiEndung: string;
  art: "text" | "bild" | "audio" | "unbekannt";
  vorschau: string; geschaetzeTokens: number; text?: string;
}
// Bild-Pfad: extrahiereAnhang() → beschreibeBildMitVisionModell() → text = Beschreibung
// Audio-Pfad (geplant): extrahiereAnhang() → whisper-Transkript + ffmpeg-Metadaten → text
```

## Was ich mir merken will

- `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` ist das gefundene kleine Vision-Modell — gleiche Linie wie das Hauptmodell, 3,4GB, bestätigte vision-Capability.
- `OLLAMA_MAX_LOADED_MODELS=1` bleibt bei 1 — bewusst getestet und verworfen, nicht einfach unbedacht gelassen.
- ODT braucht kein LibreOffice — ZIP + `content.xml` reicht.
- Anhänge werden IMMER als Text in die Nachricht eingewoben, nie als Sonderfall im Speicherformat behandelt.

## Dokumente gehören zusammen

`_claude/ideen/charakter_dashboard.md` (dieselbe "alle vier Spawner"-Kategorie), `_claude/notizen/2026-07-05-abschluss-bugfixes-wesen-selbst.md` (derselbe lange Abend), `codexium2_solarius2/provenienz_logging.md` (SSR-Fund, der zeitlich dazwischen lag).

## Was mich überrascht hat

Wie klar der Unterschied zwischen "passt in den RAM" und "läuft performant" war, sobald ich es tatsächlich gemessen habe (98% CPU, aktives Swapping, alles langsamer statt schneller) — vorher hätte ich instinktiv gesagt "26GB von 27GB, sollte grade so gehen".

## Wenn wir das bauen

**Vision-Schicht:** Irgendwann könnte das kleine Vision-Modell auch für andere Zwecke nützlich sein — z.B. Avatar-Bilder beim Hochladen automatisch kurz beschreiben, damit sie durchsuchbar werden.

**Code-Skizze:** Für Audio: `execFileSync("ffmpeg", [...])` zur Konvertierung, dann ein Python- oder Node-Aufruf an `faster-whisper` — noch nicht entschieden ob als Subprozess oder eigener kleiner Dienst.

## Resonanz

[[abwurf: Ein Anhang ist eine Übersetzung — was auch immer reinkommt, wird in die eine Sprache übersetzt, die das Wesen versteht.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

```
Rohdatei (Bild/PDF/DOCX/ODT/Text/...)
  → extrahiereAnhang() erkennt Format an Endung
    → Text-Formate: direkt/pdf-parse/mammoth/ZIP+XML
    → Bilder: kleines Vision-Modell (eigener Ollama-Call, kurzes keep_alive)
    → (geplant) Audio: Whisper + ffmpeg
  → IMMER Text als Ergebnis
    → wird in die naechste Chat-Nachricht eingewoben
      → bleibt dadurch natuerlich Teil der Geschichte, keine Sonderbehandlung noetig
```

## Was das Gespräch hinzugefügt hat

Die erste echte Auseinandersetzung mit den harten Grenzen der Hardware in dieser Session — vorher waren "das dauert halt" (Abschluss-Geschichte, Memory-Extraktion) eher hinnehmbare Wartezeiten, heute wurde klar, dass manche Kombinationen (zwei Modelle gleichzeitig) grundsätzlich nicht funktionieren, egal wie sehr man wartet.

## Vergessen-Wollen

Nichts — auch die drei Störungen bei Daniels eigener Nutzung nicht, die gehören zur ehrlichen Geschichte dieses Features dazu.

## Was fehlt noch

- Audio-"Gehörersatz"-Pipeline (Whisper + Analyse, Task angelegt, nicht begonnen).
- Ungeklärt: ob die 90-Sekunden-Schätzung für die Blockierzeit nachgeschärft werden sollte, oder ob die Retry-Schleife das ausreichend abfängt (bisher: ja, nur langsamer als geschätzt).

## Nachtrag 2026-07-05 (Nacht, nach einer Pause) — URL-Lesen fertig, deutlich unproblematischer als Vision

Task #35 fertig: `POST .../url-lesen` lädt genau eine vom Menschen angegebene URL per Playwright (JS-Rendering, damit auch dynamische Seiten funktionieren — dieselbe Begründung wie bei den eigenen Test-Skripten diese Nacht), extrahiert sichtbaren Text + Titel, landet als ganz normaler Anhang-Chip mit Token-Schätzung.

**Sicherheit statt nur Funktion:** `istSichereUrl()` blockt localhost/127.0.0.1/private IP-Ranges (10.x, 192.168.x, 172.16-31.x) und `.local`-Hostnamen, bevor überhaupt ein Browser gestartet wird — kein SSRF auf interne Dienste möglich, selbst wenn jemand versehentlich oder absichtlich eine interne Adresse eingibt. Kein automatisches Folgen von Links auf der geladenen Seite — nur die eine explizit angegebene URL.

**Deutlich unkomplizierter als die Bild-Pipeline von vorhin:** Chromium starten und wieder schließen kostet spürbar weniger Ressourcen als ein zweites LLM zu laden — kein Konflikt mit dem Hauptmodell, keine Neuladezeit danach, keine der drei Störungen von der Vision-Session. Playwright war als npm-Paket neu zu installieren, aber die Chromium-Binärdateien lagen schon im System-Cache (`~/.cache/ms-playwright`), daher kein grosser Download nötig (nur eine neuere Chromium-Version fehlte, ~290MB).

Getestet: interne Adresse (`localhost:8787`) korrekt abgelehnt, `example.com` korrekt gelesen (Titel "Example Domain", Text stimmte exakt), UI-Fluss (Modal öffnen → URL eintippen → Laden → Chip erscheint → Modal schließt sich automatisch) per Playwright verifiziert. An Wegwerf-Charakter (`UrlTest`) getestet, danach gelöscht.

## Nachtrag 2026-07-05 (Nacht, letztes Stück) — Audio-"Gehörersatz" fertig, alle vier Anhang-Typen komplett

Task #36 fertig, damit ist der ganze Anhang-Themenblock (Dokumente, Bilder, URL, Audio) heute Nacht durchgebaut. Daniel wollte explizit "nicht das minimalste sondern das maximalste Gehörersatzversion" — umgesetzt als: Whisper-Transkript (der eigentliche Inhalt, die Worte) + Dauer + Durchschnitts-Lautstärke (ffmpeg). Bewusst NICHT umgesetzt: Tempo-/Tonart-Erkennung (aubio) — im eigenen Test an einem simplen 440Hz-Sinuston lag die erkannte Tonhöhe bei 775Hz, deutlich daneben. Lieber ehrlich weniger liefern als erfundene Musikanalyse-Zahlen als Fakten ausgeben.

**Der wichtigste Unterschied zur Bild-Pipeline:** Whisper (`faster-whisper`, eigenes Python-venv `.venv-whisper`, gitignored) läuft komplett ausserhalb von Ollama — eigener Prozess, eigener Speicherbereich, keine Konkurrenz um den einen Ollama-Modell-Slot. Kein Verdrängen des Hauptmodells, kein Neuladen danach, keine der drei Störungen von der Vision-Session. Bestätigt: `curl .../api/ps` zeigte das Hauptmodell während der gesamten Audio-Verarbeitung durchgehend geladen.

**Modellwahl:** `faster-whisper` mit dem "small"-Modell, int8-quantisiert — 4,5s Ladezeit, ~1,4s Transkription für einen 6-Sekunden-Testsatz, praktisch perfekte Erkennung (eine einzige Abweichung: "Whisper" wurde als "WISPA" transkribiert, phonetisch nachvollziehbar bei deutscher Aussprache des englischen Worts).

**Damit sind alle vier Anhang-Arten (Dokumente, Bilder, URL, Audio) fertig, getestet, dokumentiert.** Der ganze Themenblock lief über eine lange Nacht mit drei echten Live-Störungen bei Daniels eigener Nutzung (alle durch meine eigenen Vision-Tests, alle live diagnostiziert und behoben) — die Lehre daraus (CPU-Kontention bei zwei gleichzeitig geladenen Modellen) hat direkt die Architektur-Entscheidung für die Audio-Pipeline geprägt: ein separates System (Whisper/Python) statt ein zweites Ollama-Modell, wo immer möglich.

### Nachtrag 2026-07-05 (Nacht, vierte Live-Störung) — nginx-Timeout fehlte für /upload und /url-lesen

Daniel hat ein fast 4-minütiges Lied hochgeladen — nach 2 Minuten kam "Upload fehlgeschlagen". Ursache gefunden statt geraten: `/etc/nginx/sites-available/flextrawurst` hatte für den `/chat`-Endpunkt schon lange ein grosszügiges `proxy_read_timeout 600s`, aber die neuen `/upload`- und `/url-lesen`-Endpunkte (beide erst heute Nacht entstanden) fielen mangels eigener Regel in den allgemeinen Catch-All mit nur 120 Sekunden. Bei genug Rechenlast (Whisper + evtl. gleichzeitige andere Anfragen) reicht das nicht.

Fix: neue `location`-Regel nach demselben Muster wie `/chat`, `proxy_read_timeout 600s` für `^/wesen/.../(upload|url-lesen)$`. Dabei auch bemerkt: das serverweite `client_max_body_size 10m` war ohnehin schon kleiner als das eigene Backend-Limit `ANHANG_MAX_BYTES` (25MB) — für die neue Location extra auf `30m` gesetzt. Mit Daniels Erlaubnis geändert (nginx-Config ist gemeinsame Infrastruktur für die ganze Domain, nicht nur für dieses Feature), `nginx -t` + `systemctl reload nginx` (kein Neustart, keine Downtime für andere Dienste auf derselben Domain).

Vierte Live-Störung der Nacht — anders als die ersten drei aber kein Ressourcen-/Architektur-Problem, sondern schlicht eine Konfigurationslücke, die entstand, weil die neuen Endpunkte nach der letzten nginx-Anpassung dazugekommen sind.
