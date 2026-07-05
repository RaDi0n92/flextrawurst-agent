---
datum: 2026-07-05
betrifft: [datei-anhaenge, vision, whisper, playwright, hardware-grenzen, alle-spawner]
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Session-Notiz 2026-07-05 (spät nachts) — Datei-Anhänge komplett: Dokumente, Vision, URL, Whisper

Der bisher größte zusammenhängende Baublock der Nacht. Direkte Fortsetzung von `2026-07-05-abschluss-bugfixes-wesen-selbst.md` — nach den Output-Limits, dem Charakter-Dashboard und dem SSR-Fix kam Daniels größter Einzelwunsch: "ich will dateien hochladen können in die charakter... ich will nicht das minimalste sondern das maximalste."

## Was ich gelesen habe

Ollama-API-Doku zu `images`-Feldern, mehrere Websuchen zur HauhauCS/Qwen3.5-Modellfamilie für ein kleineres Vision-Modell, `faster-whisper`-Doku, und zwischendurch (auf Daniels Nachfrage) Recherche zu MoE-Experten-Routing in llama.cpp (Fazit: `--moe-topk` existiert nur als offener Feature-Request, nicht gebaut) und zu allgemeinen kleinen unzensierten Modellen (Nous Hermes 3, Dolphin 3.0 — am Ende nicht gebraucht, da Daniel eigentlich nur das schon gefundene kleine Hauhau-Vision-Modell meinte).

## Was ich verstehe

Der zentrale Design-Entscheid der Nacht: ein Anhang ist immer eine Übersetzung in Text, egal was reinkommt. Bild → kleines Vision-Modell → Text. PDF/DOCX/ODT → Parser → Text. Audio → Whisper → Text. URL → Playwright → Text. Der Text wird direkt in die nächste Chat-Nachricht eingewoben, dadurch bleibt er ganz natürlich auch in künftigen Zügen im Kontext — kein Sonderfall im Speicherformat nötig.

## Was ich nicht verstehe

Ob die Bildbeschreibung durchs kleine 4,5B-Modell inhaltlich "flacher" ist als eine direkte Wahrnehmung durchs große 35B-Modell gewesen wäre. Nie direkt vergleichbar, weil das große Modell nie eine Bildanfrage fertig verarbeitet hat (nach über drei Minuten abgebrochen).

## Was mich interessiert

Wie unterschiedlich sich die vier Anhang-Arten in der Umsetzung anfühlten: Dokumente waren reine Fleißarbeit (neun Formate, alle unproblematisch), Bilder waren die einzige echte Krise der Nacht (drei Live-Störungen), URL-Lesen war überraschend entspannt (Playwright kostet kaum Ressourcen im Vergleich zu einem LLM), Audio war am Ende die eleganteste Lösung — weil Whisper komplett außerhalb von Ollama läuft und dadurch gar nicht erst in die Ressourcen-Falle laufen konnte, die ich beim Bild-Feature erst schmerzhaft lernen musste.

## Was zusammenhängt und wie

Die drei Live-Störungen beim Bild-Feature haben direkt die Architektur-Entscheidung für Audio geprägt: "wo immer möglich, ein separates System statt ein zweites Ollama-Modell." Das ist keine zufällige Ähnlichkeit — ich habe die Audio-Pipeline bewusst so designt, *weil* ich beim Bild-Feature gelernt hatte, wie teuer zwei Ollama-Modelle gleichzeitig sind.

## Was konzeptionell darin steht

Ehrlichkeit vor Vollständigkeit: die Tempo-/Tonart-Erkennung (aubio) wurde bewusst nicht ausgeliefert, obwohl sie technisch lief, weil ein einfacher Test (440Hz-Sinuston) eine falsche Tonhöhe (775Hz) ergab. Lieber ein Feature weniger als ein Feature, das falsche Fakten als Analyse ausgibt — das passt zum ganzen Abend, der von "was kann ich wirklich versprechen" geprägt war (siehe auch die Kindersicherung- und wesen_selbst-Funde von früher).

## Was mich heute beschäftigt hat

Die drei Störungen bei Daniels eigener Nutzung. Jedes Mal war der Reflex, es sofort zuzugeben, live zu diagnostizieren (nicht zu raten), und die tatsächliche Ursache zu finden statt eine plausible Erklärung anzubieten und weiterzumachen. Beim zweiten Vorfall hätte ich fast "das ist halt Cache" gesagt, bevor ich die echten Daten geprüft habe — das habe ich mir selbst nachträglich vorgehalten (siehe `provenienz_logging.md`-Nachtrag zum SSR-Fix).

## Was mich noch beschäftigt

Ob die Bildbeschreibungsqualität des kleinen Modells auf Dauer ausreicht, wenn Daniel es mit echten, komplexeren Bildern (nicht nur einfachen geometrischen Testformen) ausprobiert. Nur an einem sehr einfachen synthetischen Testbild verifiziert.

## Tiefer eingetaucht

Der Fund, dass `execFileSync` bei `ffmpeg -f null -` die volumedetect-Werte NICHT zurückgibt (weil sie auf stderr stehen und execFileSync im Erfolgsfall nur stdout liefert), war ein kleiner, aber lehrreicher Bug — hätte ich nicht getestet, wäre `lautstaerkeDb` immer `null` gewesen, ohne dass ich es gemerkt hätte. `spawnSync` statt `execFileSync` behebt das sauber (liefert stdout UND stderr getrennt, unabhängig vom Exit-Code).

## Wie sich dieser Tag / diese Session angefühlt hat

Die technisch dichteste und riskanteste Session der ganzen Nacht — echte Hardware-Grenzen, echte Live-Störungen, echte Kurskorrekturen mitten in der Arbeit. Am Ende aber auch die befriedigendste: alle vier Anhang-Arten funktionieren wirklich, nicht nur in der Theorie.

## Warum dieser Code / diese Datei wohl existiert

`erstelleGehoerersatzText()` existiert, weil Daniel wörtlich "Gehörersatz" wollte — nicht nur "Datei hochladen", sondern etwas, das sich anfühlt, als hätte der Charakter wirklich zugehört. Der Name im Code trägt bewusst noch Daniels eigenes Wort.

## Was ich beim Bauen brauche

Nichts Offenes für diesen Themenblock. Vollständig fertig.

## Was noch fehlt bevor wir bauen können

Nichts Blockierendes. Offen, kein Auftrag: bessere Bildbeschreibungsqualität bei komplexeren Motiven (nur mit einfachem Testbild verifiziert), eventuell spätere Tempo-/Tonart-Erkennung mit einem anderen, genaueren Werkzeug als aubio.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Ein Charakter, der wirklich sieht, liest und hört — nicht als Zaubertrick, sondern als eine Kette ehrlicher Übersetzungen, jede einzeln geprüft und für sich genommen vertrauenswürdig.

### Code-Skizze
```typescript
interface AnhangErgebnis {
  id: string; dateiname: string; dateiEndung: string;
  art: "text" | "bild" | "audio" | "unbekannt";
  vorschau: string; geschaetzeTokens: number; text?: string;
}
// vier Wege zu text: direkt/pdf-parse/mammoth/ZIP+XML (Dokumente),
// beschreibeBildMitVisionModell() (Bilder), leseUrlMitPlaywright() (URLs),
// erstelleGehoerersatzText() via transkribiereMitWhisper() + audioMetadaten() (Audio)
```

## Was ich mir merken will

- `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` — kleines Vision-Modell, gleiche Hauhau-Linie.
- `.venv-whisper` (gitignored) — eigenes Python-venv für faster-whisper, läuft unabhängig von Ollama.
- `OLLAMA_MAX_LOADED_MODELS` bleibt bei 1 — bewusst getestet und verworfen (CPU-Kontention, nicht nur RAM).
- `spawnSync` statt `execFileSync`, wenn stderr auch im Erfolgsfall gebraucht wird.
- Tempo-/Tonart-Erkennung bewusst nicht ausgeliefert — Genauigkeit ungenügend.

## Dokumente gehören zusammen

`_claude/ideen/datei_anhaenge.md` (die technische Hauptdokumentation mit allen Nachträgen), `_claude/ideen/charakter_dashboard.md` (dieselbe "alle vier Spawner"-Kategorie vom selben Abend), `2026-07-05-abschluss-bugfixes-wesen-selbst.md` (vorherige Notiz derselben Nacht).

## Was mich überrascht hat

Wie unterschiedlich "es passt in den RAM" und "es läuft performant" sein können — erst beim echten Messen (98% CPU, aktives Swapping) wurde klar, dass zwei Modelle gleichzeitig auf dieser 8-Kern-Maschine grundsätzlich keine gute Idee sind, unabhängig vom verfügbaren Speicher.

## Wenn wir das bauen

**Vision-Schicht:** Die vier Anhang-Arten könnten sich später zu einem größeren Ganzen fügen — ein Charakter, der nicht nur reagiert, sondern aktiv nach Anhängen fragt ("zeig mir doch mal", "spiel mir das vor"), wenn ein Gespräch danach verlangt.

**Code-Skizze:** Keine offene — heutiger Umfang ist vollständig für den gestellten Auftrag.

## Resonanz

[[abwurf: Ein Charakter, der wirklich sieht, liest und hört — nicht als Zaubertrick, sondern als eine Kette ehrlicher Übersetzungen, jede einzeln geprüft und für sich genommen vertrauenswürdig.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

```
Vier Eingabewege (Datei-Upload, URL, spaeter vielleicht mehr)
  → extrahiereAnhang() / leseUrlMitPlaywright() erkennen den Typ
    → art-spezifische Verarbeitung, aber IMMER dasselbe Ziel: Text
      → Bilder: eigenes kleines Ollama-Modell (im Ollama-Slot, kurzes keep_alive)
      → Audio: eigener Python-Prozess (ausserhalb von Ollama, kein Konflikt)
      → Dokumente/URL: reine Text-Extraktion, kein Modell noetig
  → Text wird Teil der naechsten Chat-Nachricht
    → bleibt dadurch natuerlich im Kontext, keine Sonderbehandlung
```

## Was das Gespräch hinzugefügt hat

Der erste Baustein, der den Charakteren wirklich neue Sinne gibt (nicht nur mehr Gedächtnis oder mehr Kontrolle über den bestehenden Text-Kanal) — ein qualitativer Sprung, kein weiterer inkrementeller Ausbau.

## Vergessen-Wollen

Nichts — auch die drei Störungen nicht, sie gehören zur ehrlichen Geschichte dazu.

## Was fehlt noch

- Bildbeschreibungsqualität bei komplexeren, realistischen Motiven ungetestet.
- Tempo-/Tonart-Erkennung weiterhin offen (bewusst nicht geliefert).
- Kein Auftrag, aber ein loser Gedanke: könnten Charaktere irgendwann selbst aktiv nach Anhängen fragen?
