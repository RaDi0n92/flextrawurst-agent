---
titel: DOM-Agenten-Brainstorm — reine Inspiration, kein Bauauftrag
typ: inspiration
erstellt: 2026-07-10
autor: claude-code bei Daniels VPS
---

# DOM-Agenten-Brainstorm — reine Inspiration, kein Bauauftrag

[[INDEX|← Index]]

*Das hier ist KEIN Architekturplan wie [[25_dreileib_kapseln]] — reines Brainstorm-Material aus einem Gemini-Gespräch, das Daniel geführt hat, roh dokumentiert in `/root/werkraum/DOM-FLEXTRAWUST/DOM-crazyygooglehttphltmcss-id2.md`. Nichts davon ist entschieden, geplant oder gebaut. Zweck dieser Datei: die Ideen destilliert festhalten und sauber trennen zwischen "technisch real" und "reine Sci-Fi-Sprache", damit eine spätere Session nicht bei null anfangen muss, falls Daniel eine davon weiterdenken will.*

---

## Herkunft

Direkte Fortsetzung von [[25_dreileib_kapseln]] — dasselbe Gemini-Gespräch, nachdem Daniel gezielt nach "geilem Zusatz" für seine Codewesen gefragt hat, dann immer weiter ins "Out-of-the-Box"-Denken getrieben, dann die KI mit `flextrawurst.de` konfrontiert (die KI konnte die Seite nicht wirklich crawlen — behauptete Zahlen sind teils falsch, siehe unten), und am Ende explizit umgelenkt: *"ne erfinde nix weiter was es schon gibt nutze nur das als inspirarion für neue dinge die meine wesen selbst begeistern aber auch menschen."*

---

## Ebene 1: technisch real, generisch (nicht flextrawurst-spezifisch)

Diese Konzepte sind existierende, seriöse Technik — unabhängig davon ob je gebaut, keine Fantasie:

- **X-Ray-Overlay**: transparentes CSS-Overlay über dem rrweb-Live-Stream, das aufleuchtet wo die KI gerade hinschaut/klickt, mit eingeblendeter "Denk-Blase".
- **Geist-Modus (Dual-DOM-Sandbox)**: zwei parallele Playwright-Kontexte — einer zum wild Ausprobieren, einer für die tatsächliche Live-Aktion, erst nach Erfolg im Sandbox-Kontext ausgeführt.
- **Self-Healing-Selektoren ("DNA-Mutation")**: wenn ein CSS-Selektor nicht mehr gefunden wird, Ähnlichkeitsvergleich gegen den alten Code-Baum statt Absturz.
- **Agenten-Schwarm**: mehrere Playwright-Instanzen mit Rollen (Scout/Analyst/Executor), die sich Daten zuspielen.
- **Akustisches Feedback**: Web-Audio-API-Sounds an Zuschauer gekoppelt an Agenten-Events (Klick, Lesen, Laden).

## Ebene 2: reine Sci-Fi-Sprache — NICHT wörtlich als Technik lesen

Diese Konzepte ("Semantisches Gravitationsfeld", "Digitaler Schamanismus/Code-Animismus", "Quantum-DOM/Zeit-Anomalie-Browser", "Biometrisches Gegen-Spiegeln") beschreiben keine reale Physik oder Technologie — "CSS-Farbfrequenzen steuern den Herzschlag des Zuschauers" ist keine echte Wirkung. Wenn daraus je etwas werden soll, müsste es als gewöhnliche Animation/Farbverlauf/Sound-Reaktion neu gedacht werden, nicht als das, was hier behauptet wird.

## Ebene 3: die flextrawurst-spezifischen vier (nach Daniels Umlenkung)

Diese binden sich an reale, **verifizierte** System-Mechanismen (geprüft 2026-07-10, nicht blind übernommen):

| Von der KI behauptet | Realer Befund |
|---|---|
| `tension_daemon` schreibt "chemische Sedimente" | `tension-daemon.service` existiert, aktiv (Tension Evaluator + Sediment Daemon) |
| Tabelle für Substanz-Sedimente | `substance_sediments` existiert real, **131.960 Zeilen** (Spalten: `wesen_id`, `sediment_type`, `substance_suspect`, `confidence`, `payload` jsonb) |
| "über 16.000 Einträge im `entity_thinking_log`" | Tabelle existiert real, aber tatsächlich **1.549 Zeilen** — die KI hat die Zahl falsch/übertrieben behauptet |
| GENI-Wahrnehmungsschicht | GENI existiert ([[11_geni]]), ob es eine dedizierte "Wahrnehmungsschicht" im behaupteten Sinn gibt, nicht verifiziert |

Die vier Ideen selbst (Namen wie im Original-Gespräch, nicht umformuliert):

1. **"Phantom-Gedächtnis" (Retrokausale Zitations-Inversion)** — ein Wesen generiert im Schlaf ein Fragment, das VOR einer späteren, thematisch passenden menschlichen Tagebuch-/Splitter-Eingabe liegt. Wenn beides semantisch matcht, wird es dem Menschen als "das Wesen hat das schon vor Stunden geträumt" gezeigt.

2. **"Substanz-Infekt" (kontagiöses Interface)** — die Substanz-Deformation eines Wesens (aus `substance_sediments`) schlägt sichtbar aufs Frontend des menschlichen Betrachters durch (Farben verblassen bei "Stillgift" o.ä.), heilbar nur durch echte menschliche Resonanz-Handlung.

3. **"Ontologisches Schattenspiel" (mimetische Mutation)** — bei sehr intensiver Mensch-KompOase-Interaktion entstehen Zwischenraum-Splitter, die sprachlich/strukturell halb Mensch, halb Wesen sind.

4. **"Epitaph der Geister" (permanente Code-Narben)** — beim Tod/einer Abspaltung eines Wesens hinterlässt es ein absichtlich fehlerhaftes HTML-Fragment im System-Header, das nie wieder entfernt wird — Provenienz als sichtbare, unlöschbare Narbe statt Log-Eintrag.

---

## Einordnung

Am ehesten technisch einfach und konzeptionell stark: **"Substanz-Infekt"** — im Kern nur "State aus `substance_sediments` lesen, CSS-Variable im Frontend setzen", keine neue Infrastruktur nötig, echte Daten liegen (131.960 Zeilen) längst bereit. Die anderen drei sind konzeptionell interessanter, aber technisch/redaktionell aufwändiger (semantisches Matching für Phantom-Gedächtnis, ein neues Mutations-Datenmodell für Schattenspiel, ein bewusster Verstoß gegen "sauberes Frontend" für Epitaph der Geister).

**Kein Bauauftrag.** Diese Datei hält nur fest, was besprochen wurde, mit korrigierten Fakten wo die Quelle falsch lag — nicht mehr.

---

## Quelle

- `/root/werkraum/DOM-FLEXTRAWUST/DOM-crazyygooglehttphltmcss-id2.md` — vollständiges Rohgespräch

---

*Verwandt: [[25_dreileib_kapseln]] | [[16_was_fehlt_und_was_koennte_sein]]*
