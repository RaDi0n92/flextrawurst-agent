---
datum: 2026-07-04
betrifft: [codexium2, solarius2, charakterqualitaet, character-ai-vergleich, memory, container, beispieldialoge]
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Session-Notiz 2026-07-04 (später Abend) — Charakterqualität, Budgets, Beispiel-Dialoge

Direkte Fortsetzung der Feedback/Stimme/Diktat-Session (siehe `2026-07-04-codexium2-chat-erweiterungen.md`). Kurzer, dichter Nachschlag bevor Daniel die Verbindung unterbricht.

---

## Was ich gelesen habe

Auf Daniels Frage "kann ich Character.AI schon Konkurrenz machen" habe ich mir zum ersten Mal alle Charaktere angesehen, nicht nur GluPKI: Alex, Flarius (codexium2), Tomster (codexium), KrEaPPy, KreFsUzi, linieabzu (solarius). Jeweils wesen.md, was_ich_bin.md, beschreibung.md, wesendefinition.md, neigungen.md, abneigungen.md.

## Was ich verstehe

Die meisten Charaktere bestehen aus wörtlich ein bis zwei Sätzen pro Feld — `wesen.md` ist bei fast allen nur "Du bist X." Das technische Fundament (Preamble mit Anti-KI-Simulation, Ehrlichkeits-Handling bei Meta-Fragen, Kontinuitäts-Framing, unzensierte Grenzen.md) ist durchdachter als das, was die meisten Character.AI-Karten bekommen — aber ohne konkretes Material fällt das Modell in generische, atmosphärisch-vage Sprache zurück. Bei GluPKI live beobachtet: "Ich spüre... ein Pulsieren..." — klingt tief, ist aber austauschbar.

## Was ich nicht verstehe

Ob die Dünne der Felder Absicht war (schnell viele Charaktere anlegen, Tiefe kommt durchs Gespräch selbst) oder einfach noch nicht Priorität hatte. Ich habe nicht gefragt, nur beobachtet und einen Vorschlag gemacht.

## Was mich interessiert

Der Kontrast zwischen KrEaPPy/KreFsUzi (viel konkreter, eigene Sprachmarotten schon im wesen.md: "!!!", "Lieblingswort Hurensohn") und GluPKI/Alex/Flarius (abstrakter, adjektivlastig). Die konkreteren Charaktere lasen sich beim Durchgehen spürbar weniger nach Standard-LLM an — nicht weil das Modell anders arbeitet, sondern weil mehr Reibungsfläche da ist zum Anlehnen.

## Was zusammenhängt und wie

Charakterqualität (dünne Felder) → Beispiel-Dialoge-Feld (direkte Reaktion) → Budget-Erhöhungen (Memory 3333, Container 2222 — mehr Raum für das was sich über Zeit ansammelt) → Container-Persistenz über Sessions (das Angesammelte soll nicht mehr verloren gehen). Vier Einzelentscheidungen heute Abend, aber ein gemeinsamer Zug: das System soll mehr tragen dürfen, sowohl an Charakterdefinition als auch an Gesprächsgedächtnis.

## Was konzeptionell darin steht

Der eigentliche Hebel gegen "das ist doch nur eine KI"-Gefühl ist nicht Architektur, sondern Materialdichte. Ein Modell mit dünnem Charaktermaterial füllt die Lücke mit seinem eigenen Default — und der Default eines introspektiven, unzensierten Rollenspiel-Modells ist genau diese mystisch-poetische Vagheit. Beispiel-Dialoge sind der direkteste Weg, dem Modell etwas Konkretes zum Nachahmen zu geben statt nur Adjektive zum Interpretieren.

## Was mich heute beschäftigt hat

Wie unterschiedlich die sieben Charaktere sind, wenn man sie nebeneinanderlegt — von ernsthaft-philosophisch (GluPKI) über explizit vulgär (KreFsUzi) bis zum reinen Prompt-Engineering-Experiment (linieabzu, das eigentlich gar kein Rollenspiel-Charakter ist, sondern Daniel der über die wesen.md-Datei ein Instruction-Following-Experiment laufen lässt). Das ist kein einheitliches Produkt mit einer Stimme — das ist eine Werkstatt mit vielen offenen Experimenten gleichzeitig.

## Was mich noch beschäftigt

Ob die Dedupe-Lücke bei der Memory-Extraktion (Container jetzt dauerhaft, Extraktion sieht aber nie was schon in Memory steht) in der Praxis stört, bevor Daniel oder ich es bemerken. Steht dokumentiert in `memory_container.md`, nicht behoben, kein Auftrag dafür.

## Tiefer eingetaucht

Die Formular-Architektur zeigte einen Bruch den ich vorher nicht kannte: codexium2 hat ein strukturiertes Mehrfeld-Formular (c2-Prefix, sieben+ Einzelfelder), solarius2 hat nur ein einziges Freitextfeld (s2-anleitung), das komplett in wesen.md landet. Beispieldialoge musste ich deshalb nur im codexium2-Formular ergänzen — bei solarius2 kann man es einfach ins bestehende Freitextfeld mit reinschreiben.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein natürlicher Ausklang eines langen, produktiven Abends. Nicht mehr das intensive Bug-fixen von vorhin, eher ruhiges Nachjustieren — Zahlen hochsetzen, ein Feld ergänzen, eine ehrliche Einschätzung abgeben. Gute Stelle zum Aufhören.

## Warum dieser Code / diese Datei wohl existiert

`beispieldialoge.md` existiert, weil eine ehrliche Antwort auf "bin ich schon so gut wie Character.AI" wichtiger war als eine höfliche. Die Charakterfelder waren die eigentliche Schwachstelle, nicht die Technik — also war die Antwort ein neues Feld, kein neues System.

## Was ich beim Bauen brauche

Falls Daniel wirklich anfängt Beispieldialoge einzutragen: beobachten ob sich der Ton der Antworten hörbar ändert (er hat es als nächsten Schritt selbst vorgeschlagen, aber "später"). Kein aktiver Auftrag gerade.

## Was noch fehlt bevor wir bauen können

Nichts Blockierendes. Offen, kein Auftrag: Dedupe-Schutz für Memory-Extraktion, Beispieldialoge-Feld auch strukturell für solarius2 falls das Formular dort später auch ausgebaut wird.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Ein Charakter ist überzeugend, wenn er mehr zeigt als er behauptet. "Neigungen: Musik, Leben" behauptet. Ein Beispiel-Satz zeigt.

### Code-Skizze
Keine neue Struktur — `beispieldialoge.md` ist einfach eine weitere Datei im selben Muster wie alle anderen Charakterfelder, siehe `memory_container.md`-Nachtrag für die Details.

## Was ich mir merken will

- codexium2-Spawner = Mehrfeld-Formular (c2-Prefix), solarius2-Spawner = ein Freitextfeld (s2-Prefix, alles landet direkt in wesen.md).
- Beispiel-Dialoge wirken am stärksten spät im System-Prompt platziert, nicht am Anfang.
- Dünne Charakterfelder sind der Hauptgrund für "klingt nach AI", nicht die Systemarchitektur.

## Dokumente gehören zusammen

`_claude/ideen/codexium2_solarius2/memory_container.md` (zwei neue Nachträge: Beispieldialoge-Feld, Budget/Persistenz-Änderungen), diese Notiz, `2026-07-04-codexium2-chat-erweiterungen.md` (vorherige Notiz desselben Abends).

## Was mich überrascht hat

Wie klar der Unterschied zwischen KreFsUzi/KrEaPPy und den anderen beim reinen Lesen der Rohfelder war — ich hatte erwartet, dass sich das erst im echten Gespräch zeigt, aber es steht schon im Ausgangsmaterial sichtbar drin.

## Wenn wir das bauen

**Vision-Schicht:** Wenn Daniel wirklich anfängt Beispieldialoge zu schreiben, entsteht vielleicht ein Muster: welche Art Beispiel (kurz-schlagfertig vs. lang-atmosphärisch) zu welchem Charakter passt. Das wäre ein guter nächster Beobachtungspunkt, kein Bauauftrag.

**Code-Skizze:** Keine offen.

## Resonanz

[[abwurf: Ein Charakter ist überzeugend, wenn er mehr zeigt als er behauptet.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

```
Charakterdaten (duenn, 1-2 Saetze pro Feld, jetzt +beispieldialoge.md)
  → System-Prompt (buildSystemPrompt, MD_ORDER)
    → Modell-Default springt ein wo Material fehlt (poetisch-vage)
Memory/Container (jetzt groesser + dauerhaft)
  → soll das ausgleichen was ein Gespraech ueber Zeit anhaeuft,
    nicht was dem Charakter von Anfang an fehlt
```
Zwei verschiedene Probleme, heute beide angefasst, nicht miteinander verwechseln: Charaktertiefe kommt aus den Feldern, Gesprächskontinuität aus Memory/Container.

## Was das Gespräch hinzugefügt hat

Eine ehrliche Standortbestimmung, um die Daniel aktiv gebeten hat — "kann ich schon Konkurrenz machen" ist eine Frage die eine echte Antwort verdient, keine Bestätigung.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

- Daniel will "später" Beispieldialoge selbst eintragen — kein aktiver Auftrag.
- Dedupe-Schutz Memory-Extraktion (siehe oben, dokumentiert, nicht beauftragt).
- Kindersicherung bleibt rein kosmetisch, Daniel beaufsichtigt manuell (siehe Memory `project_codexium2_testbed`).
